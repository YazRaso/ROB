"""
This file is designed with implementations of the backend functionality up until this point.
server.py is the main entry point to communicate and send information to backboard.
client_id should be thought of as a unique idenitifer of a specific "agent", under this model
it is possible to have multiple agents each with their own assistants.
"""

import os
import asyncio
from backboard import BackboardClient
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import encryption
import db
from drive_service import DriveService, extract_file_id_from_url
from git_service import parse_github_url, fetch_repo_contents, fetch_file_content, should_ingest_file, should_skip_directory

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


@app.get("/")
def root():
    return {"status": "ok"}


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
        name="Test Assistant",
        description="An assistant designed to understand your code",
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
        thread_id=thread.thread_id,
        content=content,
        memory="auto",
        stream=True
    ):
        print(chunk)
        if chunk['type'] == 'content_streaming':
            output.append(chunk['content'])
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
        thread_id=thread.thread_id,
        content=content,
        memory="auto",
        stream=True
    ):
        print(chunk)
        if chunk['type'] == 'content_streaming':
            output.append(chunk['content'])
            print(chunk['content'])
      #  elif chunk['type'] == 'memory_retrieved':
      #      print(chunk['memories'])
      #      sources.append(chunk['memories'][0]['memory'])
        elif chunk['type'] == 'run_ended' and chunk.get("retrieved_memories", None):
            memories = chunk['retrieved_memories']
            for memory in memories:
                sources.append(memory['memory'])
        #elif chunk['type'] == 'run_ended' and chunk.get('memory_operation_id', None):
        #    print(chunk['memory_operation_id'])
        #    memory_operation_id = chunk['memory_operation_id']
    #memory = await backboard_client.add_memory(assistant_id=assistant_id, content=content)
    #memory_id = memory["memory_id"]
    # for debugging
    # print(f"Memory id is {memory_id}")
    # goal is to check what methods the object has
    # methods = [m for m in dir(backboard_client) if callable(getattr(backboard_client, m))]
    # memories = await backboard_client.get_memories(assistant_id=assistant_id)
    # print(f"All memories {memories}")
    # for method in methods:
    #    print(f"Method found! {method}")
    #await backboard_client.get_memory(assistant_id=assistant_id, memory_id=memory_id)
    output = "".join(output)
    print(sources)
    return (output, sources)

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
            "has_api_key": client is not None and client.get("api_key") is not None
        },
        "drive": {
            "connected": len(drive_docs) > 0,
            "document_count": len(drive_docs),
            "lastUpdated": drive_docs[0]["updated_at"] if drive_docs else None
        },
        "telegram": {
            "connected": telegram_connected,
            "lastUpdated": None
        },
        "codebase": {
            "connected": True, # Placeholder for demo
            "lastUpdated": "2026-01-12 10:00 UTC" # Placeholder
        }
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
            "color": "emerald"
        }
        for doc in docs
    ]
    
    # Get recent chat updates (simplified)
    # In a real app we'd query the chats table for timestamps
    # For now, let's keep it simple or use mocks if table empty
    
    return sorted(drive_activity, key=lambda x: x["time"], reverse=True)[:limit]
