"""Manager for websocket connections."""

from typing import Any

from fastapi import WebSocket


class ConnectionManager:
    """Class for managin connections to several websockets in a given chat.

    Attributes:
        active_connections: A list of active connections (users currently being online)
                        represented with a list of instances of the fastapi.WebSocket class.
    """

    def __init__(self) -> None:
        """Initialize the class."""
        self.active_connections: list[WebSocket] = []

    async def connect(self, websocket: WebSocket) -> None:
        """Accept the connection and add it to the list.

        Args:
            websocket: An instance of the fastapi.WebSocket class,
                representing a new connection from the frontend that is meant
                to be added to the list of active connections.
        """
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket) -> None:
        """Remove the given websocket from the list.

        Args:
            websocket: An instance of the fastapi.WebSocket class,
                representing a terminated connection from the frontend that is
                meant to be removed from the list of active connections.
        """
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict[str, Any]) -> None:
        """Send a given message to all connected clients.

        Args:
            message: A dictionary with JSON data that is meant
                to be sent to all the connected clients.
        """
        for connection in self.active_connections:
            await connection.send_json(message)
