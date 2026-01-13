"""
Shared fixtures for tests.
"""

import os
import sys
import sqlite3
import tempfile
import pytest
from unittest.mock import patch, MagicMock
from cryptography.fernet import Fernet

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "backend"))


@pytest.fixture(scope="session", autouse=True)
def setup_test_db():
    """Setup test database path before any tests run."""
    import tempfile

    test_db = tempfile.mktemp(suffix=".db")
    os.environ["TEST_DB_NAME"] = test_db
    yield test_db
    # Cleanup
    if os.path.exists(test_db):
        try:
            os.remove(test_db)
        except:
            pass


@pytest.fixture(autouse=True)
def clean_test_db():
    """Clean database before each test."""
    db_name = os.getenv("TEST_DB_NAME", ":memory:")
    if os.path.exists(db_name):
        con = sqlite3.connect(db_name)
        cur = con.cursor()
        # Clear all tables
        try:
            cur.execute("DELETE FROM drive_documents")
            cur.execute("DELETE FROM chats")
            cur.execute("DELETE FROM assistants")
            cur.execute("DELETE FROM clients")
            con.commit()
        except:
            pass
        finally:
            con.close()
    yield


@pytest.fixture
def temp_db(tmp_path):
    """Create a temporary database for testing."""
    db_path = tmp_path / "test.db"
    con = sqlite3.connect(str(db_path))
    cur = con.cursor()

    # Create tables
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS clients (
            client_id TEXT PRIMARY KEY,
            api_key TEXT
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS assistants (
            assistant_id TEXT PRIMARY KEY,
            client_id TEXT
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS chats (
            chat_id TEXT PRIMARY KEY,
            channel_name TEXT,
            chat TEXT
        )
    """
    )
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS drive_documents (
            file_id TEXT PRIMARY KEY,
            client_id TEXT,
            file_name TEXT,
            content_hash TEXT,
            last_modified TEXT,
            content TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """
    )
    con.commit()
    con.close()

    return str(db_path)


@pytest.fixture
def encryption_key():
    """Generate a valid Fernet encryption key for testing."""
    return Fernet.generate_key().decode()


@pytest.fixture
def mock_env(encryption_key):
    """Mock environment variables for testing."""
    with patch.dict(
        os.environ, {"ENCRYPTION_KEY": encryption_key, "BOT_TOKEN": "test_bot_token"}
    ):
        yield


@pytest.fixture
def mock_backboard_client():
    """Mock the BackboardClient for testing."""
    mock_client = MagicMock()
    mock_assistant = MagicMock()
    mock_assistant.assistant_id = "test_assistant_id"
    mock_client.create_assistant = MagicMock(return_value=mock_assistant)

    mock_thread = MagicMock()
    mock_thread.thread_id = "test_thread_id"
    mock_client.create_thread = MagicMock(return_value=mock_thread)

    return mock_client
