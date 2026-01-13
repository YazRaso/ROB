"""
This program is designed to setup demo.db as well as utility functions
Three tables are created
    -   clients
    -   assistants
    -   chats
    -   drive_documents
Each table has a lookup and a create function
    -   lookup functions check if the input exists
    -   create functions add the input to the db
"""

import sqlite3
import os

# Allow overriding database name for testing
DB_NAME = os.getenv("TEST_DB_NAME", "demo.db")

con = sqlite3.connect(DB_NAME)
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


cur.execute(
    """
    CREATE TABLE IF NOT EXISTS repositories (
        repo_url TEXT PRIMARY KEY,
        client_id TEXT
    )
"""
)

def get_connection():
    con = sqlite3.connect(DB_NAME)
    con.row_factory = sqlite3.Row
    return con


# client functions
def lookup_client(client_id: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        SELECT * FROM clients WHERE client_id = ?
    """,
        (client_id,),
    )
    client = cur.fetchone()
    con.close()
    return dict(client) if client else None


def create_client(client_id: str, api_key: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO clients (client_id, api_key) VALUES (?, ?)
    """,
        (client_id, str(api_key)),
    )
    con.commit()
    con.close()


# Assistant functions
def lookup_assistant(client_id: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        SELECT * FROM assistants WHERE client_id = ?
    """,
        (client_id,),
    )
    assistant = cur.fetchone()
    con.close()
    return dict(assistant) if assistant else None


def create_assistant(assistant_id: str, client_id: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO assistants (assistant_id, client_id) VALUES (?, ?)
""",
        (str(assistant_id), client_id),
    )
    con.commit()
    con.close()


# Thread functions
def lookup_thread(chat_id: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        SELECT * FROM chats WHERE chat_id = ?
    """,
        (chat_id,),
    )
    chat = cur.fetchone()
    con.close()
    return dict(chat) if chat else None


def create_thread(chat_id: str, channel_name: str, chat: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO chats (chat_id, channel_name, chat) VALUES (?, ?, ?)
    """,
        (chat_id, channel_name, chat),
    )
    con.commit()
    con.close()


# Drive document functions
def lookup_drive_document(file_id: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        SELECT * FROM drive_documents WHERE file_id = ?
    """,
        (file_id,),
    )
    doc = cur.fetchone()
    con.close()
    return dict(doc) if doc else None


def create_drive_document(
    file_id: str,
    client_id: str,
    file_name: str,
    content_hash: str,
    last_modified: str,
    content: str,
):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO drive_documents 
        (file_id, client_id, file_name, content_hash, last_modified, content) 
        VALUES (?, ?, ?, ?, ?, ?)
    """,
        (file_id, client_id, file_name, content_hash, last_modified, content),
    )
    con.commit()
    con.close()


def update_drive_document(file_id: str, content_hash: str, content: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        UPDATE drive_documents 
        SET content_hash = ?, content = ?, updated_at = CURRENT_TIMESTAMP
        WHERE file_id = ?
    """,
        (content_hash, content, file_id),
    )
    con.commit()
    con.close()


def get_all_drive_documents_for_client(client_id: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        SELECT * FROM drive_documents WHERE client_id = ?
    """,
        (client_id,),
    )
    docs = cur.fetchall()
    con.close()
    return [dict(doc) for doc in docs] if docs else []


# Repo Functions 

def add_repository(repo_url: str, client_id: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        INSERT INTO repositories (repo_url, client_id) VALUES (?, ?)
    """,
        (repo_url, client_id),
    )
    con.commit()
    con.close()

def lookup_repository(repo_url: str):
    con = get_connection()
    con.row_factory = sqlite3.Row
    cur = con.cursor()
    cur.execute(
        """
        SELECT * FROM repositories WHERE repo_url = ?
    """,
        (repo_url,),
    )
    repo = cur.fetchone()
    con.close()
    return dict(repo) if repo else None