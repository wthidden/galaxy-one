"""
Message routing and handler dispatch.
Routes incoming WebSocket messages to appropriate handlers.
"""
import json
import logging
from typing import Dict, Callable, Awaitable, Any, Optional
import websockets

from .game.entities import Player

logger = logging.getLogger(__name__)


class MessageRouter:
    """
    Routes incoming messages to registered handlers.
    Supports both websocket-level (pre-auth) and player-level handlers.
    """

    def __init__(self):
        # Handlers that work with Player objects (game commands)
        self._player_handlers: Dict[str, Callable[[Player, dict], Awaitable[None]]] = {}

        # Handlers that work with raw websockets (auth, lobby)
        self._websocket_handlers: Dict[str, Callable[[websockets.WebSocketServerProtocol, dict], Awaitable[None]]] = {}

    def register_handler(self, message_type: str, handler: Callable[[Player, dict], Awaitable[None]]):
        """
        Register a player-level handler for a message type.

        Args:
            message_type: The message type to handle (e.g., "command", "chat")
            handler: Async function(player, data) to handle message
        """
        if message_type in self._player_handlers:
            logger.warning(f"Overwriting player handler for message type: {message_type}")

        self._player_handlers[message_type] = handler
        logger.debug(f"Registered player handler for message type: {message_type}")

    def register_websocket_handler(self, message_type: str, handler: Callable[[websockets.WebSocketServerProtocol, dict], Awaitable[None]]):
        """
        Register a websocket-level handler (for pre-auth messages).

        Args:
            message_type: The message type to handle (e.g., "SIGNUP", "LOGIN")
            handler: Async function(websocket, data) to handle message
        """
        if message_type in self._websocket_handlers:
            logger.warning(f"Overwriting websocket handler for message type: {message_type}")

        self._websocket_handlers[message_type] = handler
        logger.debug(f"Registered websocket handler for message type: {message_type}")

    def unregister_handler(self, message_type: str):
        """
        Unregister a handler.

        Args:
            message_type: The message type
        """
        if message_type in self._player_handlers:
            del self._player_handlers[message_type]
            logger.debug(f"Unregistered player handler for message type: {message_type}")
        if message_type in self._websocket_handlers:
            del self._websocket_handlers[message_type]
            logger.debug(f"Unregistered websocket handler for message type: {message_type}")

    async def route(self, player: Optional[Player], websocket: websockets.WebSocketServerProtocol, raw_message: str):
        """
        Route a raw message to the appropriate handler.

        Args:
            player: The player who sent the message (may be None for pre-auth)
            websocket: The websocket connection
            raw_message: The raw JSON message string
        """
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError as e:
            player_name = player.name if player else "unknown"
            logger.error(f"Invalid JSON from {player_name}: {e}")
            return

        message_type = data.get("type")
        if not message_type:
            player_name = player.name if player else "unknown"
            logger.warning(f"Message from {player_name} missing 'type' field")
            return

        # Check websocket-level handlers first (pre-auth messages)
        ws_handler = self._websocket_handlers.get(message_type)
        if ws_handler:
            try:
                await ws_handler(websocket, data)
                return
            except Exception as e:
                logger.error(f"Error in websocket handler for {message_type}: {e}", exc_info=True)
                return

        # Check player-level handlers (requires authenticated player)
        player_handler = self._player_handlers.get(message_type)
        if player_handler:
            if not player:
                logger.warning(f"Message type {message_type} requires authenticated player")
                return

            try:
                await player_handler(player, data)
                return
            except Exception as e:
                logger.error(f"Error in player handler for {message_type}: {e}", exc_info=True)
                return

        # No handler found
        logger.warning(f"No handler for message type: {message_type}")

    def has_handler(self, message_type: str) -> bool:
        """Check if a handler is registered for a message type."""
        return message_type in self._player_handlers or message_type in self._websocket_handlers

    def get_registered_types(self) -> list[str]:
        """Get list of all registered message types."""
        return list(set(list(self._player_handlers.keys()) + list(self._websocket_handlers.keys())))


# Global message router instance
_message_router = None


def get_message_router() -> MessageRouter:
    """Get the global message router instance."""
    global _message_router
    if _message_router is None:
        _message_router = MessageRouter()
    return _message_router


def reset_message_router():
    """Reset the global message router (useful for testing)."""
    global _message_router
    _message_router = MessageRouter()
