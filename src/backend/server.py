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
import encryption
import db

app = FastAPI()

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
        description="An assistant designed to understand your code"
    )
    # Create entries for db
    encrypted_api_key = encryption.encrypt_api_key(api_key)
    db.create_assistant(assistant.assistant_id, client_id)
    db.create_client(client_id, encrypted_api_key)

# add_thread uses client_ids assistant and prompts backboard with content
# memories are added manually
@app.post("/messages/send")
async def add_thread(client_id: str, content: str, status_code=201):
    client = db.lookup_client(client_id)
    if not client:
        raise HTTPException(status_code=404, detail="Client does not exist!")
    # For simplicity, we assume that each client has one assistant
    decrypted_api_key = encryption.decrypt_api_key(client['api_key'])
    backboard_client = BackboardClient(api_key=decrypted_api_key)
    assistant = db.lookup_assistant(client_id)
    assistant_id = assistant['assistant_id']
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

@app.post("/messages/summarize")
async def summarize(client_id: str, status_code=201):
    content = "Summarize all the memories that you have"
    return await add_thread(client_id=client_id, content=content)
