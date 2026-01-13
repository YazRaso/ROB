"""
This module handles Google Drive integration for the onboarding assistant.
It polls Google Drive documents for changes, extracts content, and feeds it to Backboard's memory.

Key features:
- OAuth2 authentication with Google Drive
- Polling mechanism to detect content changes
- Content extraction from Google Docs
- Integration with Backboard API for memory storage
"""

import os
import time
import asyncio
import hashlib
from datetime import datetime
from typing import Optional, Dict, List
from dotenv import load_dotenv
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import db
from backboard import BackboardClient
import encryption

load_dotenv()

# Scopes required for reading Google Drive files
SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]


class DriveService:
    """
    Service class to manage Google Drive integration.
    Handles authentication, content extraction, and change detection.
    """

    def __init__(
        self, credentials_path: str = "credentials.json", token_path: str = "token.json"
    ):
        """
        Initialize the Drive service.

        Args:
            credentials_path: Path to Google OAuth2 credentials file
            token_path: Path to store/load authentication token
        """
        # Use absolute paths relative to this file's directory
        current_dir = os.path.dirname(os.path.abspath(__file__))
        if not os.path.isabs(credentials_path):
            self.credentials_path = os.path.join(current_dir, credentials_path)
        else:
            self.credentials_path = credentials_path

        if not os.path.isabs(token_path):
            self.token_path = os.path.join(current_dir, token_path)
        else:
            self.token_path = token_path

        self.service = None
        self.creds = None

    def authenticate(self):
        """
        Authenticate with Google Drive API using OAuth2.
        Creates new credentials if none exist, refreshes if expired.
        """
        # Check if token file exists and load credentials
        if os.path.exists(self.token_path):
            self.creds = Credentials.from_authorized_user_file(self.token_path, SCOPES)

        # If credentials don't exist or are invalid, get new ones
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found at {self.credentials_path}. "
                        "Please download OAuth2 credentials from Google Cloud Console."
                    )
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                self.creds = flow.run_local_server(port=8080)

            # Save credentials for next time
            with open(self.token_path, "w") as token:
                token.write(self.creds.to_json())

        # Build the Drive service
        self.service = build("drive", "v3", credentials=self.creds)
        print("Successfully authenticated with Google Drive")

    def get_document_content(self, file_id: str) -> Optional[str]:
        """
        Extract text content from a Google Doc.

        Args:
            file_id: Google Drive file ID

        Returns:
            Extracted text content or None if extraction fails
        """
        try:
            # For Google Docs, we need to export as plain text
            request = self.service.files().export_media(
                fileId=file_id, mimeType="text/plain"
            )
            content = request.execute()
            return content.decode("utf-8")
        except HttpError as error:
            print(f"Error fetching document {file_id}: {error}")
            return None

    def get_file_metadata(self, file_id: str) -> Optional[Dict]:
        """
        Get metadata for a Drive file.

        Args:
            file_id: Google Drive file ID

        Returns:
            Dictionary containing file metadata
        """
        try:
            file = (
                self.service.files()
                .get(
                    fileId=file_id,
                    fields="id, name, modifiedTime, mimeType, webViewLink",
                )
                .execute()
            )
            return file
        except HttpError as error:
            print(f"Error fetching metadata for {file_id}: {error}")
            return None

    def compute_content_hash(self, content: str) -> str:
        """
        Compute MD5 hash of content to detect changes.

        Args:
            content: Text content to hash

        Returns:
            MD5 hash as hex string
        """
        return hashlib.md5(content.encode("utf-8")).hexdigest()

    async def process_document(self, file_id: str, client_id: str):
        """
        Process a single document: extract content and send to Backboard if changed.

        Args:
            file_id: Google Drive file ID
            client_id: Client ID for Backboard integration
        """
        # Get file metadata
        metadata = self.get_file_metadata(file_id)
        if not metadata:
            print(f"Failed to get metadata for file {file_id}")
            return

        # Extract content
        content = self.get_document_content(file_id)
        if not content:
            print(f"Failed to extract content from file {file_id}")
            return

        # Compute content hash for change detection
        content_hash = self.compute_content_hash(content)

        # Check if document has been processed before
        existing_doc = db.lookup_drive_document(file_id)

        if existing_doc:
            # Document exists - check if content changed
            if existing_doc["content_hash"] == content_hash:
                print(f"No changes detected in {metadata['name']}")
                return
            print(f"Changes detected in {metadata['name']}")
        else:
            print(f"Processing new document: {metadata['name']}")

        # Send content to Backboard
        try:
            # Get client from database
            client = db.lookup_client(client_id)
            if not client:
                print(f"Client {client_id} not found")
                return

            # Decrypt API key
            decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
            backboard_client = BackboardClient(api_key=decrypted_api_key)

            # Get assistant
            assistant = db.lookup_assistant(client_id)
            if not assistant:
                print(f"No assistant found for client {client_id}")
                return

            assistant_id = assistant["assistant_id"]

            # Create a temporary text file with the content
            import tempfile

            temp_file_path = None
            try:
                # Create temporary file with document content
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".txt", delete=False, encoding="utf-8"
                ) as temp_file:
                    # Write content with metadata header
                    header = f"""Document: {metadata['name']}
Last Modified: {metadata['modifiedTime']}
Source: Google Drive
Link: {metadata.get('webViewLink', 'N/A')}

{'='*60}

"""
                    temp_file.write(header + content)
                    temp_file_path = temp_file.name

                # Upload document to assistant
                print(f"Uploading {metadata['name']} to Backboard...")
                document = await backboard_client.upload_document_to_assistant(
                    assistant_id, temp_file_path
                )

                # Wait for document to be indexed
                print(f"Waiting for document to be indexed...")
                max_wait_time = 60  # Maximum 60 seconds
                start_time = time.time()

                while time.time() - start_time < max_wait_time:
                    status = await backboard_client.get_document_status(
                        document.document_id
                    )
                    if status.status == "indexed":
                        print(f"✅ Document indexed successfully: {metadata['name']}")
                        break
                    elif status.status == "failed":
                        print(f"❌ Document indexing failed: {status.status_message}")
                        return
                    await asyncio.sleep(2)
                else:
                    print(f"⚠️  Document indexing timeout for {metadata['name']}")

            finally:
                # Clean up temporary file
                if temp_file_path and os.path.exists(temp_file_path):
                    os.remove(temp_file_path)

            print(f"Successfully uploaded to Backboard: {metadata['name']}")

            # Update or create database entry
            if existing_doc:
                print(f"Updating existing document in DB: {file_id}")
                db.update_drive_document(file_id, content_hash, content)
            else:
                print(f"Creating new document in DB: {file_id} for client {client_id}")
                db.create_drive_document(
                    file_id=file_id,
                    client_id=client_id,
                    file_name=metadata["name"],
                    content_hash=content_hash,
                    last_modified=metadata["modifiedTime"],
                    content=content,
                )
            print(f"Document saved to database: {file_id}")

        except Exception as e:
            print(f"Error processing document: {e}")
            import traceback

            traceback.print_exc()

    async def poll_documents(
        self, file_ids: List[str], client_id: str, interval: int = 300
    ):
        """
        Continuously poll Google Drive documents for changes.

        Args:
            file_ids: List of Google Drive file IDs to monitor
            client_id: Client ID for Backboard integration
            interval: Polling interval in seconds (default: 5 minutes)
        """
        print(
            f"Starting Drive polling for {len(file_ids)} documents (interval: {interval}s)"
        )

        while True:
            try:
                for file_id in file_ids:
                    await self.process_document(file_id, client_id)

                print(f"Waiting {interval} seconds before next poll...")
                await asyncio.sleep(interval)

            except KeyboardInterrupt:
                print("\nStopping Drive polling...")
                break
            except Exception as e:
                print(f"Error during polling: {e}")
                # Wait before retrying even if there's an error
                await asyncio.sleep(interval)

    def register_document_for_monitoring(self, file_id: str, client_id: str):
        """
        Register a Google Drive document for monitoring.

        Args:
            file_id: Google Drive file ID
            client_id: Client ID for Backboard integration
        """
        # Check if file exists and is accessible
        metadata = self.get_file_metadata(file_id)
        if not metadata:
            raise ValueError(f"Cannot access file {file_id}")

        # Store in database
        existing = db.lookup_drive_document(file_id)
        if not existing:
            db.create_drive_document(
                file_id=file_id,
                client_id=client_id,
                file_name=metadata["name"],
                content_hash="",
                last_modified=metadata["modifiedTime"],
                content="",
            )
            print(f"Registered document for monitoring: {metadata['name']}")
        else:
            print(f"Document already registered: {metadata['name']}")


# Helper function to extract file ID from Google Drive URL
def extract_file_id_from_url(url: str) -> Optional[str]:
    """
    Extract file ID from a Google Drive URL.

    Args:
        url: Google Drive URL (e.g., https://docs.google.com/document/d/FILE_ID/edit)

    Returns:
        File ID or None if extraction fails
    """
    # Common patterns in Google Drive URLs
    patterns = [
        "/d/",  # /d/FILE_ID/
        "id=",  # ?id=FILE_ID
        "/file/d/",  # /file/d/FILE_ID
    ]

    for pattern in patterns:
        if pattern in url:
            start = url.find(pattern) + len(pattern)
            end = url.find("/", start)
            if end == -1:
                # Try to find query parameters
                end = url.find("?", start)
            if end == -1:
                # Take rest of string
                file_id = url[start:]
            else:
                file_id = url[start:end]

            # Clean up the file ID
            file_id = file_id.strip("/")
            if file_id:
                return file_id

    return None
