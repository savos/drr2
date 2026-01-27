import asyncio
import json
import uuid
from typing import Any, AsyncGenerator, Dict, List


class Hotwire:
    """Minimal in-memory pub/sub for Server-Sent Events."""

    def __init__(self) -> None:
        self._queues: List[asyncio.Queue] = []

    async def connect(self) -> asyncio.Queue:
        """Register a new listener and return its queue."""
        queue: asyncio.Queue = asyncio.Queue()
        self._queues.append(queue)
        return queue

    def disconnect(self, queue: asyncio.Queue) -> None:
        """Remove a listener's queue."""
        try:
            self._queues.remove(queue)
        except ValueError:
            pass

    async def broadcast(self, event: str, data: Dict[str, Any]) -> None:
        """Send data to all connected listeners."""
        message = {"event": event, "data": json.dumps(data)}
        for queue in list(self._queues):
            await queue.put(message)

    async def contact_email_verification(self, contact_id: uuid.UUID, verified_email: int) -> None:
        """Broadcast a contact's email verification status."""
        await self.broadcast(
            "client_update_email_verification",
            {"id": str(contact_id), "verified_email": verified_email},
        )


hotwire = Hotwire()


async def event_generator(queue: asyncio.Queue) -> AsyncGenerator[str, None]:
    """Yield formatted SSE messages for a given listener queue."""
    try:
        while True:
            message = await queue.get()
            yield f"event: {message['event']}\ndata: {message['data']}\n\n"
    finally:
        hotwire.disconnect(queue)
