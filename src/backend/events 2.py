"""
Event system for notifying the frontend when data is added from different sources.
Uses Server-Sent Events (SSE) for real-time notifications.

Sources:
- drive: Google Drive document updates
- repo: GitHub repository file uploads
- telegram: Telegram chat messages
"""

import asyncio
import json
from typing import AsyncGenerator, Optional
from datetime import datetime

# Event queue for SSE - stores events that will be sent to connected clients
event_queues: list[asyncio.Queue] = []


async def emit_event(source: str, client_id: Optional[str] = None):
    """
    Emit an event to all connected SSE clients.

    Args:
        source: The source of the data - must be one of: "drive", "repo", "telegram"
        client_id: Optional client ID associated with the event
    """
    if source not in ("drive", "repo", "telegram"):
        raise ValueError(f"Invalid source: {source}. Must be one of: drive, repo, telegram")

    event_data = {
        "source": source,
        "timestamp": datetime.utcnow().isoformat(),
    }

    if client_id:
        event_data["client_id"] = client_id

    # Send event to all connected clients
    for queue in event_queues:
        await queue.put(event_data)


async def event_stream() -> AsyncGenerator[str, None]:
    """
    Generator that yields SSE-formatted events.
    Used by the /events endpoint.
    """
    queue: asyncio.Queue = asyncio.Queue()
    event_queues.append(queue)

    try:
        while True:
            # Wait for an event
            event_data = await queue.get()
            # Format as SSE
            yield f"data: {json.dumps(event_data)}\n\n"
    finally:
        # Clean up when client disconnects
        event_queues.remove(queue)
