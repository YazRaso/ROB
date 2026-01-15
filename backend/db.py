"""
Database utility functions for PostgreSQL on Railway.

Tables:
    - clients
    - assistants
    - chats
    - drive_documents
    - repositories

Each table has lookup and create functions.
"""

import os
import psycopg2
from psycopg2.extras import RealDictCursor

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is required")


def get_connection():
    """Get a new database connection with RealDictCursor."""
    conn = psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)
    return conn


# Client functions
def lookup_client(client_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM clients WHERE client_id = %s
        """,
        (client_id,),
    )
    client = cur.fetchone()
    cur.close()
    conn.close()
    return dict(client) if client else None


def create_client(client_id: str, api_key: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO clients (client_id, api_key) VALUES (%s, %s)
        """,
        (client_id, str(api_key)),
    )
    conn.commit()
    cur.close()
    conn.close()


# Assistant functions
def lookup_assistant(client_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM assistants WHERE client_id = %s
        """,
        (client_id,),
    )
    assistant = cur.fetchone()
    cur.close()
    conn.close()
    return dict(assistant) if assistant else None


def create_assistant(assistant_id: str, client_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO assistants (assistant_id, client_id) VALUES (%s, %s)
        """,
        (str(assistant_id), client_id),
    )
    conn.commit()
    cur.close()
    conn.close()


# Thread/Chat functions
def lookup_thread(chat_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM chats WHERE chat_id = %s
        """,
        (chat_id,),
    )
    chat = cur.fetchone()
    cur.close()
    conn.close()
    return dict(chat) if chat else None


def create_thread(chat_id: str, channel_name: str, chat: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO chats (chat_id, channel_name, chat) VALUES (%s, %s, %s)
        """,
        (chat_id, channel_name, chat),
    )
    conn.commit()
    cur.close()
    conn.close()


# Drive document functions
def lookup_drive_document(file_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM drive_documents WHERE file_id = %s
        """,
        (file_id,),
    )
    doc = cur.fetchone()
    cur.close()
    conn.close()
    return dict(doc) if doc else None


def create_drive_document(
    file_id: str,
    client_id: str,
    file_name: str,
    content_hash: str,
    last_modified: str,
    content: str,
):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO drive_documents
        (file_id, client_id, file_name, content_hash, last_modified, content)
        VALUES (%s, %s, %s, %s, %s, %s)
        """,
        (file_id, client_id, file_name, content_hash, last_modified, content),
    )
    conn.commit()
    cur.close()
    conn.close()


def update_drive_document(file_id: str, content_hash: str, content: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        UPDATE drive_documents
        SET content_hash = %s, content = %s, updated_at = CURRENT_TIMESTAMP
        WHERE file_id = %s
        """,
        (content_hash, content, file_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def get_all_drive_documents_for_client(client_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM drive_documents WHERE client_id = %s
        """,
        (client_id,),
    )
    docs = cur.fetchall()
    cur.close()
    conn.close()
    return [dict(doc) for doc in docs] if docs else []


# Repository functions
def add_repository(repo_url: str, client_id: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO repositories (repo_url, client_id) VALUES (%s, %s)
        """,
        (repo_url, client_id),
    )
    conn.commit()
    cur.close()
    conn.close()


def lookup_repository(repo_url: str):
    conn = get_connection()
    cur = conn.cursor()
    cur.execute(
        """
        SELECT * FROM repositories WHERE repo_url = %s
        """,
        (repo_url,),
    )
    repo = cur.fetchone()
    cur.close()
    conn.close()
    return dict(repo) if repo else None
