"""
Tests for events.py - Server-Sent Events system for source notifications.
"""
import os
import sys
import pytest
import asyncio
import json
from unittest.mock import patch, MagicMock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src', 'backend'))

from events import emit_event, event_stream, event_queues


class TestEmitEvent:
    """Tests for the emit_event function."""

    @pytest.fixture(autouse=True)
    def clear_queues(self):
        """Clear event queues before each test."""
        event_queues.clear()
        yield
        event_queues.clear()

    @pytest.mark.asyncio
    async def test_emit_event_with_valid_source_drive(self):
        """Test emitting an event with 'drive' source."""
        queue = asyncio.Queue()
        event_queues.append(queue)

        await emit_event("drive", "test_client")

        event = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert event["source"] == "drive"
        assert event["client_id"] == "test_client"
        assert "timestamp" in event

    @pytest.mark.asyncio
    async def test_emit_event_with_valid_source_repo(self):
        """Test emitting an event with 'repo' source."""
        queue = asyncio.Queue()
        event_queues.append(queue)

        await emit_event("repo", "test_client")

        event = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert event["source"] == "repo"

    @pytest.mark.asyncio
    async def test_emit_event_with_valid_source_telegram(self):
        """Test emitting an event with 'telegram' source."""
        queue = asyncio.Queue()
        event_queues.append(queue)

        await emit_event("telegram")

        event = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert event["source"] == "telegram"

    @pytest.mark.asyncio
    async def test_emit_event_without_client_id(self):
        """Test emitting an event without a client_id."""
        queue = asyncio.Queue()
        event_queues.append(queue)

        await emit_event("drive")

        event = await asyncio.wait_for(queue.get(), timeout=1.0)
        assert event["source"] == "drive"
        assert "client_id" not in event

    @pytest.mark.asyncio
    async def test_emit_event_with_invalid_source_raises_error(self):
        """Test that emitting with an invalid source raises ValueError."""
        with pytest.raises(ValueError) as exc_info:
            await emit_event("invalid_source")

        assert "Invalid source" in str(exc_info.value)
        assert "invalid_source" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_emit_event_broadcasts_to_multiple_queues(self):
        """Test that events are broadcast to all connected queues."""
        queue1 = asyncio.Queue()
        queue2 = asyncio.Queue()
        queue3 = asyncio.Queue()
        event_queues.extend([queue1, queue2, queue3])

        await emit_event("drive", "client_123")

        # All queues should receive the event
        for queue in [queue1, queue2, queue3]:
            event = await asyncio.wait_for(queue.get(), timeout=1.0)
            assert event["source"] == "drive"
            assert event["client_id"] == "client_123"

    @pytest.mark.asyncio
    async def test_emit_event_timestamp_format(self):
        """Test that the timestamp is in ISO format."""
        queue = asyncio.Queue()
        event_queues.append(queue)

        await emit_event("telegram")

        event = await asyncio.wait_for(queue.get(), timeout=1.0)
        # Should be valid ISO format (datetime.isoformat())
        from datetime import datetime
        timestamp = event["timestamp"]
        # This should not raise an error
        datetime.fromisoformat(timestamp)


class TestEventStream:
    """Tests for the event_stream async generator."""

    @pytest.fixture(autouse=True)
    def clear_queues(self):
        """Clear event queues before each test."""
        event_queues.clear()
        yield
        event_queues.clear()

    @pytest.mark.asyncio
    async def test_event_stream_registers_queue(self):
        """Test that event_stream adds a queue to event_queues."""
        assert len(event_queues) == 0

        stream = event_stream()
        # Start the generator
        task = asyncio.create_task(stream.__anext__())

        # Give it time to register
        await asyncio.sleep(0.1)

        assert len(event_queues) == 1

        # Cancel the task and cleanup
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    @pytest.mark.asyncio
    async def test_event_stream_yields_sse_format(self):
        """Test that event_stream yields data in SSE format."""
        stream = event_stream()

        # Start consuming the stream
        async def consume():
            async for data in stream:
                return data

        task = asyncio.create_task(consume())

        # Give stream time to start
        await asyncio.sleep(0.1)

        # Emit an event
        await emit_event("drive", "client_1")

        # Get the result
        result = await asyncio.wait_for(task, timeout=1.0)

        # Should be SSE formatted
        assert result.startswith("data: ")
        assert result.endswith("\n\n")

        # Parse the JSON data
        json_str = result[6:-2]  # Remove "data: " prefix and "\n\n" suffix
        data = json.loads(json_str)
        assert data["source"] == "drive"
        assert data["client_id"] == "client_1"

    @pytest.mark.asyncio
    async def test_event_stream_cleanup_on_disconnect(self):
        """Test that the queue is removed when the stream ends."""
        stream = event_stream()

        # Start and then stop the stream
        task = asyncio.create_task(stream.__anext__())
        await asyncio.sleep(0.1)

        assert len(event_queues) == 1

        # Cancel (simulating client disconnect)
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

        # The cleanup happens in the finally block
        # We need to properly close the generator
        await stream.aclose()

        assert len(event_queues) == 0
