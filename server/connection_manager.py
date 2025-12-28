"""
WebSocket connection management.
Handles connection lifecycle, authentication, and cleanup.
"""
import asyncio
import websockets
from typing import Dict, Set, Optional
import logging

from .game.state import get_game_state
from .game.entities import Player
from websockets.protocol import State

logger = logging.getLogger(__name__)


class ConnectionManager:
    """
    Manages WebSocket connections and player sessions.
    """

    def __init__(self):
        self._connections: Dict[websockets.WebSocketServerProtocol, Player] = {}
        self._players_by_id: Dict[int, Player] = {}
        self._lock = asyncio.Lock()

    async def register(self, websocket: websockets.WebSocketServerProtocol) -> Player:
        """
        Register a new connection.

        Args:
            websocket: The WebSocket connection

        Returns:
            The Player object created for this connection
        """
        async with self._lock:
            game_state = get_game_state()

            # Create temporary player name
            player_id = game_state.next_player_id
            temp_name = f"Player_{player_id}"

            player = game_state.add_player(websocket, temp_name)
            self._connections[websocket] = player
            self._players_by_id[player.id] = player

            logger.info(f"Registered connection for {temp_name} (ID: {player.id})")

            return player

    async def unregister(self, websocket: websockets.WebSocketServerProtocol):
        """
        Unregister a connection and clean up.

        Args:
            websocket: The WebSocket connection
        """
        async with self._lock:
            if websocket not in self._connections:
                return

            player = self._connections[websocket]
            player_name = player.name

            # Remove from game state
            game_state = get_game_state()
            game_state.remove_player(websocket)

            # Remove from tracking
            del self._connections[websocket]
            if player.id in self._players_by_id:
                del self._players_by_id[player.id]

            logger.info(f"Unregistered {player_name} (ID: {player.id})")

    def get_player(self, websocket: websockets.WebSocketServerProtocol) -> Optional[Player]:
        """
        Get player by websocket.

        Args:
            websocket: The WebSocket connection

        Returns:
            Player object or None
        """
        return self._connections.get(websocket)

    def get_player_by_id(self, player_id: int) -> Optional[Player]:
        """
        Get player by ID.

        Args:
            player_id: The player ID

        Returns:
            Player object or None
        """
        return self._players_by_id.get(player_id)

    def get_all_players(self) -> list[Player]:
        """Get all connected players."""
        return list(self._connections.values())

    def get_all_connections(self) -> list[websockets.WebSocketServerProtocol]:
        """Get all active WebSocket connections."""
        return list(self._connections.keys())

    def is_connected(self, websocket: websockets.WebSocketServerProtocol) -> bool:
        """Check if websocket is connected."""
        return websocket in self._connections

    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return len(self._connections)

    async def broadcast(self, message: dict, exclude: Optional[Set[websockets.WebSocketServerProtocol]] = None):
        """
        Broadcast a message to all connections.

        Args:
            message: Message dict to send
            exclude: Set of websockets to exclude from broadcast
        """
        exclude = exclude or set()

        tasks = []
        for websocket in self._connections:
            if websocket not in exclude:
                # Check if websocket is open (works with both old and new websockets library)
                is_open = False
                if hasattr(websocket, 'state'):
                    is_open = websocket.state == State.OPEN
                elif hasattr(websocket, 'open'):
                    is_open = websocket.open

                if is_open:
                    tasks.append(self._send_safe(websocket, message))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def _send_safe(self, websocket: websockets.WebSocketServerProtocol, message: dict):
        """
        Safely send a message, handling errors.

        Args:
            websocket: The WebSocket connection
            message: Message dict to send
        """
        try:
            import json
            await websocket.send(json.dumps(message))
        except websockets.exceptions.ConnectionClosed:
            logger.warning(f"Connection closed while sending message")
        except Exception as e:
            logger.error(f"Error sending message: {e}")


# Global connection manager instance
_connection_manager = None


def get_connection_manager() -> ConnectionManager:
    """Get the global connection manager instance."""
    global _connection_manager
    if _connection_manager is None:
        _connection_manager = ConnectionManager()
    return _connection_manager


def reset_connection_manager():
    """Reset the global connection manager (useful for testing)."""
    global _connection_manager
    _connection_manager = ConnectionManager()
