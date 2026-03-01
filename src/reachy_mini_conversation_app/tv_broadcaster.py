"""WebSocket broadcaster for TV display."""

import asyncio
import json
import logging
from typing import Set
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class TVDisplayBroadcaster:
    """Broadcasts conversation events to connected TV displays via WebSocket."""

    def __init__(self):
        """Initialize the broadcaster."""
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()

    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection."""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"TV display connected. Total connections: {len(self.active_connections)}")

    async def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection."""
        async with self._lock:
            self.active_connections.discard(websocket)
        logger.info(f"TV display disconnected. Total connections: {len(self.active_connections)}")

    async def broadcast(self, event_type: str, data: dict) -> None:
        """Broadcast an event to all connected TV displays."""
        if not self.active_connections:
            return

        message = json.dumps({
            "type": event_type,
            "data": data
        })

        # Create a copy of connections to avoid modification during iteration
        async with self._lock:
            connections = list(self.active_connections)

        disconnected = []
        for websocket in connections:
            try:
                await websocket.send_text(message)
            except WebSocketDisconnect:
                disconnected.append(websocket)
            except Exception as e:
                logger.warning(f"Error broadcasting to TV display: {e}")
                disconnected.append(websocket)

        # Clean up disconnected websockets
        if disconnected:
            async with self._lock:
                for ws in disconnected:
                    self.active_connections.discard(ws)


# Global broadcaster instance
tv_broadcaster = TVDisplayBroadcaster()
