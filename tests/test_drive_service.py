"""
Test cases for Google Drive integration functionality.
Tests document processing, change detection, and Backboard integration.
"""

import pytest
import asyncio
from unittest.mock import Mock, patch, AsyncMock, MagicMock
from src.backend.drive_service import DriveService, extract_file_id_from_url
from src.backend import db


class TestFileIdExtraction:
    """Test file ID extraction from various Google Drive URL formats."""

    def test_extract_from_standard_docs_url(self):
        url = "https://docs.google.com/document/d/1ABC123xyz/edit"
        file_id = extract_file_id_from_url(url)
        assert file_id == "1ABC123xyz"

    def test_extract_from_file_url(self):
        url = "https://drive.google.com/file/d/1XYZ789abc/view"
        file_id = extract_file_id_from_url(url)
        assert file_id == "1XYZ789abc"

    def test_extract_from_url_with_query_params(self):
        url = "https://drive.google.com/open?id=1DEF456uvw"
        file_id = extract_file_id_from_url(url)
        assert file_id == "1DEF456uvw"

    def test_invalid_url_returns_none(self):
        url = "https://example.com/invalid"
        file_id = extract_file_id_from_url(url)
        assert file_id is None

    def test_direct_file_id(self):
        # Should work with just the file ID too
        file_id = "1ABC123xyz"
        result = extract_file_id_from_url(file_id)
        assert result is None  # Won't match patterns


class TestDriveService:
    """Test DriveService class functionality."""

    @pytest.fixture
    def drive_service(self):
        """Create a DriveService instance for testing."""
        return DriveService(
            credentials_path="test_credentials.json", token_path="test_token.json"
        )

    def test_compute_content_hash(self, drive_service):
        """Test content hashing for change detection."""
        content1 = "This is test content"
        content2 = "This is test content"
        content3 = "Different content"

        hash1 = drive_service.compute_content_hash(content1)
        hash2 = drive_service.compute_content_hash(content2)
        hash3 = drive_service.compute_content_hash(content3)

        # Same content should produce same hash
        assert hash1 == hash2
        # Different content should produce different hash
        assert hash1 != hash3

    @patch("src.backend.drive_service.build")
    @patch("src.backend.drive_service.Credentials")
    def test_get_file_metadata(self, mock_creds, mock_build, drive_service):
        """Test fetching file metadata from Drive API."""
        # Mock the Drive service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the API response
        mock_metadata = {
            "id": "123",
            "name": "Test Document",
            "modifiedTime": "2026-01-12T10:00:00Z",
            "mimeType": "application/vnd.google-apps.document",
            "webViewLink": "https://docs.google.com/document/d/123/edit",
        }

        mock_service.files().get().execute.return_value = mock_metadata
        drive_service.service = mock_service

        # Test getting metadata
        metadata = drive_service.get_file_metadata("123")

        assert metadata is not None
        assert metadata["id"] == "123"
        assert metadata["name"] == "Test Document"

    @patch("src.backend.drive_service.build")
    def test_get_document_content(self, mock_build, drive_service):
        """Test extracting content from Google Docs."""
        # Mock the Drive service
        mock_service = MagicMock()
        mock_build.return_value = mock_service

        # Mock the export response
        test_content = b"This is test document content"
        mock_service.files().export_media().execute.return_value = test_content
        drive_service.service = mock_service

        # Test getting content
        content = drive_service.get_document_content("123")

        assert content == "This is test document content"

    @pytest.mark.asyncio
    @patch("src.backend.drive_service.BackboardClient")
    @patch("src.backend.db.lookup_client")
    @patch("src.backend.db.lookup_assistant")
    @patch("src.backend.db.lookup_drive_document")
    @patch("src.backend.db.create_drive_document")
    @patch("src.backend.encryption.decrypt_api_key")
    async def test_process_new_document(
        self,
        mock_decrypt,
        mock_create_doc,
        mock_lookup_doc,
        mock_lookup_assistant,
        mock_lookup_client,
        mock_backboard,
        drive_service,
    ):
        """Test processing a new document (first time)."""
        # Setup mocks
        mock_lookup_client.return_value = {
            "client_id": "test",
            "api_key": "encrypted_key",
        }
        mock_lookup_assistant.return_value = {"assistant_id": "asst_123"}
        mock_lookup_doc.return_value = None  # Document doesn't exist yet
        mock_decrypt.return_value = "decrypted_api_key"

        # Mock Backboard client
        mock_bb_instance = AsyncMock()
        mock_thread = AsyncMock()
        mock_thread.thread_id = "thread_123"
        mock_bb_instance.create_thread.return_value = mock_thread

        # Mock streaming response
        async def mock_add_message(*args, **kwargs):
            yield {"type": "content_streaming", "content": "Response chunk 1"}
            yield {"type": "content_streaming", "content": " chunk 2"}

        mock_bb_instance.add_message = mock_add_message
        mock_backboard.return_value = mock_bb_instance

        # Mock Drive service methods
        drive_service.get_file_metadata = Mock(
            return_value={
                "id": "123",
                "name": "Test Doc",
                "modifiedTime": "2026-01-12T10:00:00Z",
                "webViewLink": "https://example.com",
            }
        )
        drive_service.get_document_content = Mock(return_value="Test content")

        # Process the document
        await drive_service.process_document("123", "test_client")

        # Verify document was created in database
        mock_create_doc.assert_called_once()
        args = (
            mock_create_doc.call_args[1]
            if mock_create_doc.call_args[1]
            else mock_create_doc.call_args[0]
        )
        assert "Test content" in str(args)

    @pytest.mark.asyncio
    @patch("src.backend.db.lookup_drive_document")
    async def test_process_unchanged_document(self, mock_lookup_doc, drive_service):
        """Test that unchanged documents are skipped."""
        # Mock existing document with same hash
        mock_lookup_doc.return_value = {
            "file_id": "123",
            "content_hash": drive_service.compute_content_hash("Test content"),
        }

        # Mock Drive service methods
        drive_service.get_file_metadata = Mock(
            return_value={
                "id": "123",
                "name": "Test Doc",
                "modifiedTime": "2026-01-12T10:00:00Z",
            }
        )
        drive_service.get_document_content = Mock(return_value="Test content")

        # Process the document
        with patch("builtins.print") as mock_print:
            await drive_service.process_document("123", "test_client")

            # Should print "No changes detected"
            assert any(
                "No changes detected" in str(call) for call in mock_print.call_args_list
            )


class TestDatabaseIntegration:
    """Test database operations for Drive documents."""

    @pytest.fixture(autouse=True)
    def setup_and_teardown(self):
        """Setup test database before each test, cleanup after."""
        # Setup is handled by conftest.py
        yield
        # Cleanup is handled by conftest.py

    def test_create_and_lookup_drive_document(self):
        """Test creating and retrieving a Drive document."""
        db.create_drive_document(
            file_id="test_123",
            client_id="test_client",
            file_name="Test Document",
            content_hash="abc123",
            last_modified="2026-01-12T10:00:00Z",
            content="Test content",
        )

        doc = db.lookup_drive_document("test_123")

        assert doc is not None
        assert doc["file_id"] == "test_123"
        assert doc["file_name"] == "Test Document"
        assert doc["content_hash"] == "abc123"

    def test_update_drive_document(self):
        """Test updating an existing Drive document."""
        # Create initial document
        db.create_drive_document(
            file_id="test_456",
            client_id="test_client",
            file_name="Test Doc",
            content_hash="old_hash",
            last_modified="2026-01-12T09:00:00Z",
            content="Old content",
        )

        # Update the document
        db.update_drive_document(
            file_id="test_456", content_hash="new_hash", content="New content"
        )

        # Verify update
        doc = db.lookup_drive_document("test_456")
        assert doc["content_hash"] == "new_hash"
        assert doc["content"] == "New content"

    def test_get_all_drive_documents_for_client(self):
        """Test retrieving all documents for a specific client."""
        # Create multiple documents for different clients
        db.create_drive_document(
            file_id="doc1",
            client_id="client_a",
            file_name="Doc 1",
            content_hash="hash1",
            last_modified="2026-01-12T10:00:00Z",
            content="Content 1",
        )

        db.create_drive_document(
            file_id="doc2",
            client_id="client_a",
            file_name="Doc 2",
            content_hash="hash2",
            last_modified="2026-01-12T10:00:00Z",
            content="Content 2",
        )

        db.create_drive_document(
            file_id="doc3",
            client_id="client_b",
            file_name="Doc 3",
            content_hash="hash3",
            last_modified="2026-01-12T10:00:00Z",
            content="Content 3",
        )

        # Get documents for client_a
        docs = db.get_all_drive_documents_for_client("client_a")

        assert len(docs) == 2
        assert all(doc["client_id"] == "client_a" for doc in docs)

        # Get documents for client_b
        docs = db.get_all_drive_documents_for_client("client_b")
        assert len(docs) == 1
