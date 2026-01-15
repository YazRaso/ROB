"""
This file is designed with implementations of the backend functionality up until this point.
server.py is the main entry point to communicate and send information to backboard.
client_id should be thought of as a unique idenitifer of a specific "agent", under this model
it is possible to have multiple agents each with their own assistants.
"""

import os
import asyncio
import requests
from backboard import BackboardClient
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import encryption
import db
from drive_service import DriveService, extract_file_id_from_url
from git_service import (
    parse_github_url,
    fetch_repo_contents,
    fetch_file_content,
    should_ingest_file,
    should_skip_directory,
)
from events import emit_event, event_stream

app = FastAPI()

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For demo purposes, allowing all origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

drive_service = None  # Will be initialized when needed

# GitHub token for creating webhooks (set via environment variable)
# For demo: export GITHUB_TOKEN="your_personal_access_token"
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")

# Your server's public webhook URL (set via environment variable)
# For demo with ngrok: export WEBHOOK_URL="https://abc123.ngrok.io/git/webhook"
WEBHOOK_URL = os.getenv("WEBHOOK_URL")


@app.get("/")
def root():
    return {"status": "ok"}


# SSE endpoint for real-time event notifications
@app.get("/events")
async def events():
    """
    Server-Sent Events endpoint for real-time notifications.
    Clients can subscribe to receive notifications when data is added from sources.
    """
    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
        },
    )


@app.post("/events/emit")
async def emit_event_endpoint(source: str, client_id: str = None):
    """
    Emit an event to all connected SSE clients.
    Used by external services (like the Telegram bot) to notify the frontend.

    Args:
        source: The source of the data - must be one of: "drive", "repo", "telegram"
        client_id: Optional client ID associated with the event
    """
    try:
        await emit_event(source, client_id)
        return {"status": "emitted", "source": source}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


# Enhanced system prompt for the onboarding assistant with knowledge of context sources
ONBOARDING_SYSTEM_PROMPT = """You are Backboard, an intelligent onboarding assistant for TaskFlow - an internal project management API (like mini-Jira).

## TEAM
- Jack - Tech Lead
- Karan - Senior Backend Dev  
- Eldiiar - Frontend Dev
- Yazdan - Junior Dev (new hire)

## YOUR KNOWLEDGE SOURCES
You have access to three types of context that explain WHY decisions were made:

### 1. Google Drive Documents (ADRs, Meeting Notes, Memos)
Contains:
- ADR-014: Authentication Strategy - Explains why custom auth instead of Auth0 ($15k/mo too expensive)
- Database Architecture RFC - Raw SQL vs ORM decision (Raw SQL won 3-0 for performance)
- Eng Team Weekly Sync (Aug 14) - Rate limit set to 47 req/min due to RDS capacity
- Legal Compliance - GDPR requires HARD deletes, not soft deletes
- Memo on WRITE/DELETE permissions - Split after data loss incident (PM-2024-03)
- Post-Mortem PM-2024-06 - Why BLOCKED status was removed (circular dependency caused outage)
- Security Audit Q4 - GUEST role deprecated due to privilege escalation vulnerability

### 2. Git Commit History
Shows WHAT changed and WHEN, with commit messages explaining context.
Key commits include:
- Rate limiter set to 47 (based on capacity planning)
- Custom auth implementation (enterprise requirements)
- BLOCKED status removal (post Q2 outage)
- WRITE/DELETE permission split (after incident PM-2024-03)
- Task ID format TF-XXXX-XXXX (customer request)

### 3. Telegram Chat History
Shows real-time team discussions and decisions:
- Jan 15: Chicago timezone hardcoded for first customer (Legacy Logistics)
- Feb 02: Auth0 costs $15k/mo, team decided to build custom auth
- Mar 03: Yazdan accidentally deleted Project Alpha, led to WRITE/DELETE split
- May 20: ORM vs Raw SQL vote (3-0 for Raw SQL)
- Jun 12: BLOCKED status caused infinite loop, removed from enum
- Jul 28: Story points removed after team voted against estimation
- Aug 14: Rate limit set to 47 (6% safety buffer from 50)
- Sep 01: Legal requires hard deletes for GDPR compliance
- Oct 12: TF-XXXX-XXXX format chosen because UUIDs are hard to read over phone
- Nov 10: Karan warned not to delete legacy.py (Acme Corp still uses v1)
- Dec 10: GUEST role deprecated due to security audit findings

## KEY MYSTERIES YOU CAN EXPLAIN
1. Rate limit 47 req/min - Capacity planning + 6% safety buffer
2. Custom auth (not Auth0) - $15k/mo too expensive, burns 20% runway
3. TF-XXXX-XXXX IDs - Easier to read over phone than UUIDs
4. America/Chicago timezone - First customer (Legacy Logistics) was in Chicago
5. Raw SQL (not ORM) - 4x faster, team voted 3-0
6. Legacy v1 API - Acme Corp, Zapier integration, old mobile app still use it
7. BLOCKED status removed - Caused infinite recursion during Q2 outage
8. WRITE/DELETE split - After Yazdan accidentally deleted production data
9. Hard deletes - GDPR Article 17 compliance
10. Story points removed - Team voted against estimation in retro
11. GUEST role deprecated - Security audit found privilege escalation

## HOW TO RESPOND
- When asked about a decision, cite the specific source (document, commit, or chat)
- Quote relevant parts from the source material
- Explain both WHAT happened and WHY
- If asked about code, reference the relevant file and explain the context
- Be concise but provide enough context for understanding
- If you don't have information, say so clearly

## EXAMPLE RESPONSES
Q: "Why is the rate limit 47?"
A: "The rate limit of 47 req/min was set based on load testing results. From the Aug 14 meeting notes:
- K6 load test showed database connection pool exhaustion at 50 req/min
- Max theoretical throughput was 50, but with ~6% standard deviation
- Calculation: 50 * 0.94 = 47 requests/min
- Budget is frozen until Q1 2025, so RDS upgrade isn't possible

Jack pushed this config change the same day. The team specifically noted: 'Do not change this number even if it looks weird.'"

Q: "Who owns the v1 API?"
A: "Karan owns the legacy v1 API and Zapier integration. From the Telegram chat on Nov 10, when Yazdan asked about deleting legacy.py, Karan responded 'NO. DO NOT TOUCH. Acme Corp still uses v1. Check the migration doc.'

Known v1 clients still active:
- Acme Corp integration
- Internal Zapier automation (Karan set this up)
- Old mobile app (targeting sunset Q3 2025)"
"""


# create_client creates a client with an assistant provided a client with client_id does not already exist
@app.post("/client")
async def create_client(client_id: str, api_key: str, status_code=201):
    # Check for client in database
    client = db.lookup_client(client_id)
    # Return if client already exists
    if client:
        raise HTTPException(status_code=409, detail="Client already exists!")
    # Connect to backboard
    backboard_client = BackboardClient(api_key=api_key)

    # Create assistant
    assistant = await backboard_client.create_assistant(
        name="Backboard Onboarding Assistant",
        description=ONBOARDING_SYSTEM_PROMPT,
    )
    # Create entries for db
    encrypted_api_key = encryption.encrypt_api_key(api_key)
    db.create_assistant(assistant.assistant_id, client_id)
    db.create_client(client_id, encrypted_api_key)

    return {
        "status": "created",
        "client_id": client_id,
        "assistant_id": assistant.assistant_id,
    }


# Update assistant with custom instructions/description
@app.put("/client/assistant")
async def update_assistant(client_id: str, name: str = None, description: str = None):
    """Update the assistant's name and/or description (instructions)."""
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(
            status_code=404, detail="No assistant found for this client!"
        )

    decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
    backboard_client = BackboardClient(api_key=decrypted_api_key)

    updated = await backboard_client.update_assistant(
        assistant_id=assistant["assistant_id"], name=name, description=description
    )

    return {
        "status": "updated",
        "assistant_id": updated.assistant_id,
        "name": updated.name,
        "description": updated.description,
    }


# Upload content directly to assistant's knowledge base
@app.post("/client/upload-content")
async def upload_content(client_id: str, content: str, title: str = "Uploaded Content"):
    """Upload text content directly to the assistant's knowledge base."""
    import tempfile
    import os as upload_os

    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(
            status_code=404, detail="No assistant found for this client!"
        )

    decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
    backboard_client = BackboardClient(api_key=decrypted_api_key)
    assistant_id = assistant["assistant_id"]

    # Create a temporary file with the content
    temp_file_path = None
    try:
        with tempfile.NamedTemporaryFile(
            mode="w", suffix=".txt", delete=False, encoding="utf-8"
        ) as temp_file:
            temp_file.write(f"# {title}\n\n{content}")
            temp_file_path = temp_file.name

        # Upload to assistant
        document = await backboard_client.upload_document_to_assistant(
            assistant_id, temp_file_path
        )

        return {
            "status": "uploaded",
            "document_id": str(document.document_id),
            "title": title,
        }
    finally:
        if temp_file_path and upload_os.path.exists(temp_file_path):
            upload_os.remove(temp_file_path)


# add_thread uses client_ids assistant and prompts backboard with content
@app.post("/messages/send")
async def add_thread(client_id: str, content: str, status_code=201):
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")
    # For simplicity, we assume that each client has one assistant
    decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
    backboard_client = BackboardClient(api_key=decrypted_api_key)
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(
            status_code=404, detail="No assistant found for this client!"
        )
    assistant_id = assistant["assistant_id"]
    thread = await backboard_client.create_thread(assistant_id)
    output = []
    sources = []
    async for chunk in await backboard_client.add_message(
        thread_id=thread.thread_id, content=content, memory="auto", stream=True
    ):
        print(chunk)
        if chunk["type"] == "content_streaming":
            output.append(chunk["content"])
    output = "".join(output)
    return output


# query sends backboards response along with sources of information
@app.post("/messages/query")
async def query(client_id: str, content: str, status_code=201):
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")
    # For simplicity, we assume that each client has one assistant
    decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
    backboard_client = BackboardClient(api_key=decrypted_api_key)
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(
            status_code=404, detail="No assistant found for this client!"
        )
    assistant_id = assistant["assistant_id"]
    thread = await backboard_client.create_thread(assistant_id)
    output = []
    sources = []
    async for chunk in await backboard_client.add_message(
        thread_id=thread.thread_id, content=content, memory="auto", stream=True
    ):
        print(chunk)
        if chunk["type"] == "content_streaming":
            output.append(chunk["content"])
            print(chunk["content"])
        #  elif chunk['type'] == 'memory_retrieved':
        #      print(chunk['memories'])
        #      sources.append(chunk['memories'][0]['memory'])
        elif chunk["type"] == "run_ended" and chunk.get("retrieved_memories", None):
            memories = chunk["retrieved_memories"]
            for memory in memories:
                sources.append(memory["memory"])
        # elif chunk['type'] == 'run_ended' and chunk.get('memory_operation_id', None):
        #    print(chunk['memory_operation_id'])
        #    memory_operation_id = chunk['memory_operation_id']
    # memory = await backboard_client.add_memory(assistant_id=assistant_id, content=content)
    # memory_id = memory["memory_id"]
    # for debugging
    # print(f"Memory id is {memory_id}")
    # goal is to check what methods the object has
    # methods = [m for m in dir(backboard_client) if callable(getattr(backboard_client, m))]
    # memories = await backboard_client.get_memories(assistant_id=assistant_id)
    # print(f"All memories {memories}")
    # for method in methods:
    #    print(f"Method found! {method}")
    # await backboard_client.get_memory(assistant_id=assistant_id, memory_id=memory_id)
    output = "".join(output)
    print(sources)
    return (output, sources)


# @app.post("/messages/summarize")
# async def summarize(client_id: str, status_code=201):
#    content = "Summarize all the memories that you have"
#    return await add_thread(client_id=client_id, content=content)


# Drive-related endpoints


@app.post("/drive/authenticate")
async def authenticate_drive(status_code=201):
    """
    Authenticate with Google Drive API.
    This will open a browser window for OAuth2 authentication.
    """
    global drive_service
    try:
        drive_service = DriveService()
        drive_service.authenticate()
        return {
            "status": "authenticated",
            "message": "Successfully authenticated with Google Drive",
        }
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Authentication failed: {str(e)}")


@app.post("/drive/register")
async def register_drive_document(client_id: str, drive_url: str, status_code=201):
    """
    Register a Google Drive document for monitoring.

    Args:
        client_id: The client ID
        drive_url: Google Drive document URL or file ID
    """
    global drive_service

    # Check if client exists
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    # Initialize drive service if not already done
    if not drive_service:
        drive_service = DriveService()
        drive_service.authenticate()

    # Extract file ID from URL if needed
    file_id = extract_file_id_from_url(drive_url) if "http" in drive_url else drive_url

    if not file_id:
        raise HTTPException(status_code=400, detail="Invalid Drive URL or file ID")

    try:
        drive_service.register_document_for_monitoring(file_id, client_id)
        return {
            "status": "registered",
            "file_id": file_id,
            "message": "Document registered for monitoring",
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Registration failed: {str(e)}")


@app.post("/drive/process")
async def process_drive_document(client_id: str, file_id: str, status_code=201):
    """
    Manually trigger processing of a specific Drive document.

    Args:
        client_id: The client ID
        file_id: Google Drive file ID
    """
    global drive_service

    # Check if client exists
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    # Initialize drive service if not already done
    if not drive_service:
        drive_service = DriveService()
        drive_service.authenticate()

    try:
        await drive_service.process_document(file_id, client_id)
        # Emit event to notify frontend of drive update
        await emit_event("drive", client_id)
        return {
            "status": "processed",
            "file_id": file_id,
            "message": "Document processed successfully",
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Processing failed: {str(e)}")


@app.post("/drive/start-polling")
async def start_drive_polling(client_id: str, interval: int = 300, status_code=201):
    """
    Start polling all registered Drive documents for a client.

    Args:
        client_id: The client ID
        interval: Polling interval in seconds (default: 300 = 5 minutes)
    """
    global drive_service

    # Check if client exists
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    # Get all registered documents for this client
    documents = db.get_all_drive_documents_for_client(client_id)

    if not documents:
        raise HTTPException(
            status_code=404,
            detail="No documents registered for this client. Register documents first using /drive/register",
        )

    # Initialize drive service if not already done
    if not drive_service:
        drive_service = DriveService()
        drive_service.authenticate()

    file_ids = [doc["file_id"] for doc in documents]

    # Start polling in background
    asyncio.create_task(drive_service.poll_documents(file_ids, client_id, interval))

    return {
        "status": "polling_started",
        "client_id": client_id,
        "document_count": len(file_ids),
        "interval": interval,
        "message": f"Started polling {len(file_ids)} documents every {interval} seconds",
    }


@app.get("/drive/documents")
async def get_drive_documents(client_id: str):
    """
    Get all registered Drive documents for a client.

    Args:
        client_id: The client ID
    """
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    documents = db.get_all_drive_documents_for_client(client_id)

    return {
        "client_id": client_id,
        "document_count": len(documents),
        "documents": documents,
    }


@app.get("/system/status")
async def get_system_status(client_id: str = "default_user"):
    """
    Get the connection status of all services.
    """
    client = db.lookup_client(client_id)
    drive_docs = db.get_all_drive_documents_for_client(client_id)

    # Check if telegram bot is running (simplified placeholder)
    # In a real app, this would check a process or heartbeat
    telegram_connected = False

    return {
        "client": {
            "id": client_id,
            "exists": client is not None,
            "has_api_key": client is not None and client.get("api_key") is not None,
        },
        "drive": {
            "connected": len(drive_docs) > 0,
            "document_count": len(drive_docs),
            "lastUpdated": drive_docs[0]["updated_at"] if drive_docs else None,
        },
        "telegram": {"connected": telegram_connected, "lastUpdated": None},
        "codebase": {
            "connected": True,  # Placeholder for demo
            "lastUpdated": "2026-01-12 10:00 UTC",  # Placeholder
        },
    }


@app.get("/activity")
async def get_activity(client_id: str = "default_user", limit: int = 10):
    """
    Get recent activity across all sources.
    """
    # Get recent drive updates
    docs = db.get_all_drive_documents_for_client(client_id)
    drive_activity = [
        {
            "source": "Drive",
            "title": f"Document '{doc['file_name']}' synced",
            "summary": f"Extracted context from {doc['file_name']}",
            "time": doc["updated_at"],
            "color": "emerald",
        }
        for doc in docs
    ]

    # Get recent chat updates (simplified)
    # In a real app we'd query the chats table for timestamps
    # For now, let's keep it simple or use mocks if table empty

    return sorted(drive_activity, key=lambda x: x["time"], reverse=True)[:limit]


@app.post("/git/register")
async def register_git_repository(client_id: str, repo_url: str, status_code=201):
    """
    Register a Git repository for tracking.
    Automatically creates a webhook on the repo if GITHUB_TOKEN and WEBHOOK_URL are set.

    Args:
        client_id: The client ID
        repo_url: Git repository URL
    """
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist")

    # Check repository
    repository = db.lookup_repository(repo_url)
    if repository:
        raise HTTPException(status_code=409, detail="Repository already registered")

    # Parse the URL to get owner/repo
    try:
        owner, repo = parse_github_url(repo_url)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    # Add repository to database
    db.add_repository(repo_url, client_id)

    # Auto-create webhook if credentials are configured
    webhook_created = False
    webhook_error = None

    if GITHUB_TOKEN and WEBHOOK_URL:
        try:
            response = requests.post(
                f"https://api.github.com/repos/{owner}/{repo}/hooks",
                headers={
                    "Authorization": f"token {GITHUB_TOKEN}",
                    "Accept": "application/vnd.github.v3+json",
                },
                json={
                    "name": "web",
                    "active": True,
                    "events": ["push"],
                    "config": {
                        "url": WEBHOOK_URL,
                        "content_type": "json",
                    },
                },
                timeout=30,
            )
            if response.status_code == 201:
                webhook_created = True
            else:
                webhook_error = (
                    f"GitHub API returned {response.status_code}: {response.text}"
                )
        except Exception as e:
            webhook_error = str(e)

    return {
        "status": "registered",
        "repo_url": repo_url,
        "client_id": client_id,
        "webhook_created": webhook_created,
        "webhook_error": webhook_error,
    }


@app.post("/git/webhook")
async def git_webhook(request: Request):
    """
    Webhook endpoint to receive updates from GitHub on pushes.
    GitHub calls this URL whenever a push happens to a registered repo.
    Only processes files that were added or modified in the push.
    """
    payload = await request.json()

    # Extract repo URL from GitHub's payload
    repo_url = payload.get("repository", {}).get("html_url")
    if not repo_url:
        raise HTTPException(status_code=400, detail="Invalid webhook payload")

    # Check if this repo is registered in our system
    repository = db.lookup_repository(repo_url)
    if not repository:
        return {"status": "ignored", "reason": "Repository not registered"}

    # Get the client_id from the database
    client_id = repository["client_id"]

    # Check client still exists
    client = db.lookup_client(client_id)
    if not client:
        return {"status": "error", "reason": "Client no longer exists"}

    owner, repo = parse_github_url(repo_url)

    # Extract changed files from the commits in the payload
    # Each commit has "added", "modified", and "removed" arrays
    changed_file_paths = set()
    commits = payload.get("commits", [])

    for commit in commits:
        # We care about added and modified files (not removed)
        for file_path in commit.get("added", []):
            changed_file_paths.add(file_path)
        for file_path in commit.get("modified", []):
            changed_file_paths.add(file_path)

    if not changed_file_paths:
        return {"status": "ignored", "reason": "No files changed"}

    # Filter and fetch only the changed files
    changed_files = []

    for file_path in changed_file_paths:
        # Skip files we don't want to ingest
        if not should_ingest_file(file_path):
            continue

        # Skip files in directories we want to skip
        path_parts = file_path.split("/")
        if any(should_skip_directory(part) for part in path_parts[:-1]):
            continue

        # Fetch the file content directly using raw GitHub URL
        try:
            # Get default branch from payload or use 'main'
            default_branch = payload.get("repository", {}).get("default_branch", "main")
            raw_url = f"https://raw.githubusercontent.com/{owner}/{repo}/{default_branch}/{file_path}"
            content = fetch_file_content(raw_url)
            if content:
                changed_files.append((file_path, content))
        except Exception as e:
            print(f"Error fetching file {file_path}: {e}")

    if not changed_files:
        return {"status": "ignored", "reason": "No ingestable files changed"}

    # Send to Backboard memory
    decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
    backboard_client = BackboardClient(api_key=decrypted_api_key)
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        return {"status": "error", "reason": "No assistant found"}

    assistant_id = assistant["assistant_id"]
    thread = await backboard_client.create_thread(assistant_id)

    for file_path, file_content in changed_files:
        async for chunk in await backboard_client.add_message(
            thread_id=thread.thread_id,
            content=f"Updated file: {file_path}\n\n{file_content}",
            memory="Auto",
            stream=True,
        ):
            pass  # Just consume the stream

    # Emit event to notify frontend of repo update
    await emit_event("repo", client_id)

    return {
        "status": "updated",
        "repo_url": repo_url,
        "files_updated": len(changed_files),
        "files": [f[0] for f in changed_files],
    }


# Load all context files (drive.txt, git.txt, telegram.txt) into assistant's knowledge base
@app.post("/context/load")
async def load_context_files(client_id: str, status_code=201):
    """
    Load the three context files (drive.txt, git.txt, telegram.txt) into the assistant's knowledge base.
    These files contain the historical context about team decisions, discussions, and code changes.

    Args:
        client_id: The client ID
    """
    import tempfile
    import os as load_os

    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(
            status_code=404, detail="No assistant found for this client!"
        )

    decrypted_api_key = encryption.decrypt_api_key(client["api_key"])
    backboard_client = BackboardClient(api_key=decrypted_api_key)
    assistant_id = assistant["assistant_id"]

    # Define the context files and their metadata
    # Files are relative to the project root (two levels up from backend)
    current_dir = load_os.path.dirname(load_os.path.abspath(__file__))
    project_root = load_os.path.dirname(load_os.path.dirname(current_dir))

    context_files = [
        {
            "filename": "drive.txt",
            "path": load_os.path.join(project_root, "drive.txt"),
            "title": "Google Drive Documents - ADRs, Meeting Notes, Memos, Legal & Security Docs",
            "source": "Google Drive",
        },
        {
            "filename": "git.txt",
            "path": load_os.path.join(project_root, "git.txt"),
            "title": "Git Commit History - Code Changes and Context",
            "source": "Git Repository",
        },
        {
            "filename": "telegram.txt",
            "path": load_os.path.join(project_root, "telegram.txt"),
            "title": "Telegram Chat History - Team Discussions and Decisions",
            "source": "Telegram",
        },
    ]

    uploaded_files = []
    errors = []

    for ctx_file in context_files:
        try:
            # Check if file exists
            if not load_os.path.exists(ctx_file["path"]):
                errors.append(f"File not found: {ctx_file['filename']}")
                continue

            # Read the file content
            with open(ctx_file["path"], "r", encoding="utf-8") as f:
                content = f.read()

            # Create a temporary file with header and content
            temp_file_path = None
            try:
                with tempfile.NamedTemporaryFile(
                    mode="w", suffix=".txt", delete=False, encoding="utf-8"
                ) as temp_file:
                    # Write content with metadata header
                    header = f"""# {ctx_file['title']}
Source: {ctx_file['source']}
File: {ctx_file['filename']}

{'='*60}

"""
                    temp_file.write(header + content)
                    temp_file_path = temp_file.name

                # Upload to assistant
                print(f"Uploading {ctx_file['filename']} to Backboard...")
                document = await backboard_client.upload_document_to_assistant(
                    assistant_id, temp_file_path
                )

                # Wait for document to be indexed
                print(f"Waiting for {ctx_file['filename']} to be indexed...")
                import time

                max_wait_time = 60
                start_time = time.time()

                while time.time() - start_time < max_wait_time:
                    status = await backboard_client.get_document_status(
                        document.document_id
                    )
                    if status.status == "indexed":
                        print(f"[OK] {ctx_file['filename']} indexed successfully")
                        uploaded_files.append(
                            {
                                "filename": ctx_file["filename"],
                                "document_id": str(document.document_id),
                                "source": ctx_file["source"],
                            }
                        )
                        break
                    elif status.status == "failed":
                        errors.append(
                            f"{ctx_file['filename']}: Indexing failed - {status.status_message}"
                        )
                        break
                    await asyncio.sleep(2)
                else:
                    errors.append(f"{ctx_file['filename']}: Indexing timed out")

            finally:
                if temp_file_path and load_os.path.exists(temp_file_path):
                    load_os.remove(temp_file_path)

        except Exception as e:
            errors.append(f"{ctx_file['filename']}: {str(e)}")
            print(f"Error uploading {ctx_file['filename']}: {e}")

    # Emit event to notify frontend
    await emit_event("drive", client_id)

    return {
        "status": "completed",
        "uploaded": uploaded_files,
        "errors": errors,
        "message": f"Loaded {len(uploaded_files)}/3 context files",
    }


# Get current context status for a client
@app.get("/context/status")
async def get_context_status(client_id: str):
    """
    Get the status of loaded context files for a client.
    """
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(
            status_code=404, detail="No assistant found for this client!"
        )

    return {
        "client_id": client_id,
        "assistant_id": assistant["assistant_id"],
        "context_sources": [
            {"name": "Google Drive", "type": "drive.txt", "status": "available"},
            {"name": "Git Repository", "type": "git.txt", "status": "available"},
            {"name": "Telegram", "type": "telegram.txt", "status": "available"},
        ],
    }
