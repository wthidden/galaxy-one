"""
Message routing and handler dispatch.
Routes incoming WebSocket messages to appropriate handlers.
"""
import json
import logging
from typing import Dict, Callable, Awaitable, Any

from .game.entities import Player

logger = logging.getLogger(__name__)


class MessageRouter:
    """
    Routes incoming messages to registered handlers.
    """

    def __init__(self):
        self._handlers: Dict[str, Callable[[Player, dict], Awaitable[None]]] = {}

    def register_handler(self, message_type: str, handler: Callable[[Player, dict], Awaitable[None]]):
        """
        Register a handler for a message type.

        Args:
            message_type: The message type to handle (e.g., "command", "chat")
            handler: Async function(player, data) to handle message
        """
        if message_type in self._handlers:
            logger.warning(f"Overwriting handler for message type: {message_type}")

        self._handlers[message_type] = handler
        logger.debug(f"Registered handler for message type: {message_type}")

    def unregister_handler(self, message_type: str):
        """
        Unregister a handler.

        Args:
            message_type: The message type
        """
        if message_type in self._handlers:
            del self._handlers[message_type]
            logger.debug(f"Unregistered handler for message type: {message_type}")

    async def route(self, player: Player, raw_message: str):
        """
        Route a raw message to the appropriate handler.

        Args:
            player: The player who sent the message
            raw_message: The raw JSON message string
        """
        try:
            data = json.loads(raw_message)
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON from {player.name}: {e}")
            return

        message_type = data.get("type")
        if not message_type:
            logger.warning(f"Message from {player.name} missing 'type' field")
            return

        handler = self._handlers.get(message_type)
        if not handler:
            logger.warning(f"No handler for message type: {message_type}")
            return

        try:
            await handler(player, data)
        except Exception as e:
            logger.error(f"Error in handler for {message_type}: {e}", exc_info=True)

    def has_handler(self, message_type: str) -> bool:
        """Check if a handler is registered for a message type."""
        return message_type in self._handlers

    def get_registered_types(self) -> list[str]:
        """Get list of all registered message types."""
        return list(self._handlers.keys())


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
