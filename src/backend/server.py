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
from backboard.exceptions import BackboardAPIError
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
import db
from drive_service import DriveService, extract_file_id_from_url
from git_service import parse_github_url, fetch_repo_contents, fetch_file_content, should_ingest_file, should_skip_directory
from events import emit_event, event_stream
from tools import (
    get_backboard_tools,
    handle_create_file,
    handle_get_recent_context,
    handle_generate_mermaid_graph
)

app = FastAPI()

def get_or_create_client(client_id: str):
    """Helper to ensure a client exists, specifically for local testing with default_user."""
    client = db.lookup_client(client_id)
    if not client and client_id == "default_user":
        # Check if we have a real key in .env, otherwise use mock
        real_key = os.getenv("BACKBOARD_API_KEY")
        key_to_use = real_key if real_key else "mock_key_for_local_testing"
        
        try:
            encrypted_key = encryption.encrypt_api_key(key_to_use)
        except ValueError:
            encrypted_key = key_to_use
            
        db.create_client("default_user", encrypted_key)
        # Also create a mock assistant for the default user (must be valid UUID format)
        db.create_assistant("00000000-0000-0000-0000-000000000000", "default_user")
        client = db.lookup_client(client_id)
    return client

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
        }
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
    # Create assistant with tools
    tools = get_backboard_tools()
    assistant = await backboard_client.create_assistant(
        name="Test Assistant",
        description="You are a helpful assistant designed to understand code and help with onboarding. You can create files, retrieve recent context, and generate visualizations.",
        tools=tools
    )
    # Create entries for db
    db.create_assistant(assistant.assistant_id, client_id)
    db.create_client(client_id, api_key)

    return {
        "status": "created",
        "client_id": client_id,
        "assistant_id": assistant.assistant_id,
    }


# add_thread uses client_ids assistant and prompts backboard with content
@app.post("/messages/send")
async def add_thread(client_id: str, content: str, status_code=201):
    import json
    
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")
    # For simplicity, we assume that each client has one assistant
    backboard_client = BackboardClient(api_key=client["api_key"])
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(
            status_code=404, detail="No assistant found for this client!"
        )
    assistant_id = assistant["assistant_id"]

    # Create thread and send message
    thread = await backboard_client.create_thread(assistant_id)
    response = await backboard_client.add_message(
        thread_id=thread.thread_id,
        content=content,
        memory="auto",
        stream=False
    )
    
    # Check if Backboard requires tool calls
    # Handle both dict and object response structures
    response_status = response.status if hasattr(response, 'status') else response.get('status') if isinstance(response, dict) else None
    response_tool_calls = response.tool_calls if hasattr(response, 'tool_calls') else response.get('tool_calls') if isinstance(response, dict) else None
    response_run_id = response.run_id if hasattr(response, 'run_id') else response.get('run_id') if isinstance(response, dict) else None
    
    if response_status == "REQUIRES_ACTION" and response_tool_calls:
        tool_outputs = []
        
        # Process each tool call
        for tc in response_tool_calls:
            # Handle both dict and object tool call structures
            if isinstance(tc, dict):
                tc_function = tc.get('function', {})
                tool_name = tc_function.get('name') if isinstance(tc_function, dict) else None
                args = tc_function.get('parsed_arguments', {}) if isinstance(tc_function, dict) else {}
                tc_id = tc.get('id')
            else:
                if not hasattr(tc, 'function'):
                    continue
                tool_name = tc.function.name if hasattr(tc.function, 'name') else None
                args = getattr(tc.function, 'parsed_arguments', {})
                tc_id = tc.id if hasattr(tc, 'id') else None
            
            if not tool_name or not tc_id:
                continue
            
            try:
                # Execute the appropriate tool
                if tool_name == "create_file":
                    filename = args.get("filename", "docs/ONBOARDING.md") if isinstance(args, dict) else getattr(args, 'get', lambda k, d: d)("filename", "docs/ONBOARDING.md")
                    result = await handle_create_file(
                        client_id, filename, backboard_client, assistant_id, user_query=content
                    )
                    tool_outputs.append({
                        "tool_call_id": tc_id,
                        "output": json.dumps(result)
                    })
                    
                elif tool_name == "get_recent_context":
                    hours = args.get("hours", 24) if isinstance(args, dict) else getattr(args, 'get', lambda k, d: d)("hours", 24)
                    result = await handle_get_recent_context(
                        client_id, backboard_client, assistant_id, hours
                    )
                    tool_outputs.append({
                        "tool_call_id": tc_id,
                        "output": json.dumps(result)
                    })
                    
                elif tool_name == "generate_mermaid_graph":
                    topic = args.get("topic", "feature lineage") if isinstance(args, dict) else getattr(args, 'get', lambda k, d: d)("topic", "feature lineage")
                    result = await handle_generate_mermaid_graph(
                        client_id, topic, backboard_client, assistant_id
                    )
                    tool_outputs.append({
                        "tool_call_id": tc_id,
                        "output": json.dumps(result)
                    })
                else:
                    # Unknown tool - return error
                    tool_outputs.append({
                        "tool_call_id": tc_id,
                        "output": json.dumps({"error": f"Unknown tool: {tool_name}"})
                    })
            except Exception as e:
                # Tool execution failed - return error
                print(f"Error executing tool {tool_name}: {e}")
                import traceback
                traceback.print_exc()
                tool_outputs.append({
                    "tool_call_id": tc_id,
                    "output": json.dumps({"error": f"Tool execution failed: {str(e)}"})
                })
        
        # Submit tool outputs back to Backboard
        if tool_outputs:
            try:
                if not response_run_id:
                    raise ValueError("Response missing run_id")
                
                final_response = await backboard_client.submit_tool_outputs(
                    thread_id=thread.thread_id,
                    run_id=response_run_id,
                    tool_outputs=tool_outputs
                )
                return final_response.content if hasattr(final_response, 'content') else final_response.get('content') if isinstance(final_response, dict) else str(final_response)
            except Exception as e:
                print(f"Error submitting tool outputs: {e}")
                import traceback
                traceback.print_exc()
                return {"error": f"Failed to submit tool outputs: {str(e)}"}
    
    # Normal response (no tool calls needed)
    return response.content if hasattr(response, 'content') else response.get('content') if isinstance(response, dict) else str(response)

# query sends backboards response along with sources of information
@app.post("/messages/query")
async def query(client_id: str, content: str, status_code=201):
    client = get_or_create_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")
    # For simplicity, we assume that each client has one assistant
    backboard_client = BackboardClient(api_key=client["api_key"])
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(
            status_code=404, detail="No assistant found for this client!"
        )
    assistant_id = assistant["assistant_id"]
    try:
        thread = await backboard_client.create_thread(assistant_id)
        output = []
        sources = []
        async for chunk in await backboard_client.add_message(
            thread_id=thread.thread_id,
            content=content,
            memory="auto",
            stream=True
        ):
            if chunk['type'] == 'content_streaming':
                output.append(chunk['content'])
            elif chunk['type'] == 'run_ended' and chunk.get("retrieved_memories", None):
                memories = chunk['retrieved_memories']
                for memory in memories:
                    sources.append(memory['memory'])
        
        output = "".join(output)
        return (output, sources)
    except BackboardAPIError as e:
        msg = f"Local Server Message: I detected that no real Backboard API Key is configured. Please add `BACKBOARD_API_KEY` to your `.env` file to enable real AI responses!" if "API Key" in str(e) else f"Local Server Error: {str(e)}"
        return (msg, [])
    except Exception as e:
        return (f"Local Server unexpected error: {str(e)}", [])

#@app.post("/messages/summarize")
#async def summarize(client_id: str, status_code=201):
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
    client = get_or_create_client(client_id)

    drive_docs = db.get_all_drive_documents_for_client(client_id)
    
    # Get last updated times from activity log
    activity = db.get_recent_activity(client_id, limit=50)
    
    def get_last_time(source_name):
        for log in activity:
            if log["source"] == source_name:
                return log["created_at"]
        return None

    # Check if telegram bot is running (simplified placeholder)
    telegram_connected = False 

    return {
        "client": {
            "id": client_id,
            "exists": client is not None,
            "has_api_key": client is not None and client.get("api_key") is not None
        },
        "drive": {
            "connected": len(drive_docs) > 0,
            "document_count": len(drive_docs),
            "lastUpdated": get_last_time("Drive") or (drive_docs[0]["updated_at"] if drive_docs else None)
        },
        "telegram": {
            "connected": telegram_connected or get_last_time("Telegram") is not None,
            "lastUpdated": get_last_time("Telegram")
        },
        "codebase": {
            "connected": get_last_time("GitHub") is not None,
            "lastUpdated": get_last_time("GitHub")
        }
    }

@app.get("/activity")
async def get_activity(client_id: str = "default_user", limit: int = 10):
    """
    Get recent activity across all sources.
    """
    activity = db.get_recent_activity(client_id, limit)
    
    # Format for frontend if necessary (e.g., converting time to friendly format)
    # The frontend expects { source, title, summary, time, color }
    formatted_activity = [
        {
            "source": log["source"],
            "title": log["title"],
            "summary": log["summary"],
            "time": log["created_at"], # We can format this if needed
            "color": log["color"]
        }
        for log in activity
    ]
    
    return formatted_activity


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
                webhook_error = f"GitHub API returned {response.status_code}: {response.text}"
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
    backboard_client = BackboardClient(api_key=client["api_key"])
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        return {"status": "error", "reason": "No assistant found"}

    assistant_id = assistant["assistant_id"]
    try:
        thread = await backboard_client.create_thread(assistant_id)
    except BackboardAPIError as e:
        print(f"Error creating thread for git webhook: {e}")
        return {"status": "error", "reason": f"Backboard API Error: {str(e)}"}
    except Exception as e:
        print(f"Unexpected error in git webhook: {e}")
        return {"status": "error", "reason": f"Unexpected error: {str(e)}"}

    for file_path, file_content in changed_files:
        async for chunk in await backboard_client.add_message(
            thread_id=thread.thread_id,
            content=f"Updated file: {file_path}\n\n{file_content}",
            memory="Auto",
            stream=True,
        ):
            pass  # Just consume the stream

    # Log activity for dashboard
    db.log_activity(
        client_id=client_id,
        source="GitHub",
        title=f"New push to {repo}",
        summary=f"Processed {len(changed_files)} files: {', '.join([f[0] for f in changed_files[:3]])}{'...' if len(changed_files) > 3 else ''}",
        color="blue"
    )

    # Emit event to notify frontend of repo update
    await emit_event("repo", client_id)

    return {
        "status": "updated",
        "repo_url": repo_url,
        "files_updated": len(changed_files),
        "files": [f[0] for f in changed_files],
    }


# Tool endpoints

@app.post("/tools/create_file")
async def create_file_tool(
    client_id: str,
    filename: str,
    content: str,
    status_code=201
):
    """
    Tool endpoint: create_file
    Creates a new file in the user's workspace.
    
    This endpoint is called by the frontend when the LLM requests file creation.
    The actual file creation happens in the VS Code extension or web frontend.
    """
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")
    
    # Validate and sanitize filename to prevent path traversal
    if not filename or not filename.strip():
        raise HTTPException(status_code=400, detail="Filename cannot be empty")
    
    # Normalize the path
    normalized_path = os.path.normpath(filename)
    
    # Reject absolute paths
    if os.path.isabs(normalized_path):
        raise HTTPException(status_code=400, detail="Absolute paths are not allowed")
    
    # Reject paths containing '..' (path traversal)
    if '..' in normalized_path.split(os.sep):
        raise HTTPException(status_code=400, detail="Path traversal (..) is not allowed")
    
    # Reject paths with path separators outside allowed patterns
    # Allow forward slashes for cross-platform compatibility, but validate segments
    segments = normalized_path.replace('\\', '/').split('/')
    for segment in segments:
        if segment in ('..', '.') or os.sep in segment or (os.altsep and os.altsep in segment):
            raise HTTPException(status_code=400, detail="Invalid path segment")
    
    # Limit filename length
    if len(normalized_path) > 255:
        raise HTTPException(status_code=400, detail="Filename too long (max 255 characters)")
    
    # Use the sanitized filename
    sanitized_filename = normalized_path.replace('\\', '/')  # Normalize to forward slashes

    backboard_client = BackboardClient(api_key=client["api_key"])
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(status_code=404, detail="No assistant found!")
    
    result = await handle_create_file(
        client_id, sanitized_filename, backboard_client, assistant["assistant_id"], user_query=content
    )
    
    return result


@app.post("/tools/get_recent_context")
async def get_recent_context_tool(
    client_id: str,
    hours: int = 24,
    status_code=200
):
    """
    Tool endpoint: get_recent_context
    Retrieves RAG chunks ingested within the last X hours, grouped by source.
    """
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    backboard_client = BackboardClient(api_key=client["api_key"])
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(status_code=404, detail="No assistant found!")

    result = await handle_get_recent_context(
        client_id, backboard_client, assistant["assistant_id"], hours
    )
    
    return result


@app.post("/tools/generate_mermaid_graph")
async def generate_mermaid_graph_tool(
    client_id: str,
    topic: str,
    status_code=200
):
    """
    Tool endpoint: generate_mermaid_graph
    Generates a Mermaid.js syntax string that maps the lineage of a feature.
    """
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")

    backboard_client = BackboardClient(api_key=client["api_key"])
    assistant = db.lookup_assistant(client_id)
    if not assistant:
        raise HTTPException(status_code=404, detail="No assistant found!")

    result = await handle_generate_mermaid_graph(
        client_id, topic, backboard_client, assistant["assistant_id"]
    )
    
    return result


@app.get("/tools/definitions")
async def get_tool_definitions():
    """
    Get all tool definitions for Backboard.
    """
    return {
        "tools": get_backboard_tools()
    }
