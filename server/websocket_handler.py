"""
Main WebSocket handler.
Coordinates connection management, message routing, and lifecycle.
"""
import asyncio
import websockets
import logging

from .connection_manager import get_connection_manager
from .message_router import get_message_router
from .message_sender import get_message_sender

logger = logging.getLogger(__name__)


class WebSocketHandler:
    """
    Main WebSocket handler coordinating all WebSocket operations.
    """

    def __init__(self):
        self.connection_manager = get_connection_manager()
        self.message_router = get_message_router()
        self.message_sender = get_message_sender()

    async def handle_connection(self, websocket: websockets.WebSocketServerProtocol):
        """
        Handle a new WebSocket connection lifecycle.

        Args:
            websocket: The WebSocket connection
        """
        player = None

        try:
            # Register connection
            player = await self.connection_manager.register(websocket)

            # Send welcome message
            await self.message_sender.send_welcome(player)

            # Send current admin message if it exists
            from .admin_message import get_admin_watcher
            admin_watcher = get_admin_watcher()
            current_message = admin_watcher.get_current_message()
            if current_message:
                logger.info(f"Sending initial admin message to {player.name}")
                await self.message_sender.send_admin_message(player, current_message)
            else:
                logger.debug(f"No admin message to send to {player.name}")

            # Main message loop
            async for raw_message in websocket:
                await self.message_router.route(player, raw_message)

        except websockets.exceptions.ConnectionClosed:
            logger.info(f"Connection closed for {player.name if player else 'unknown'}")

        except Exception as e:
            logger.error(f"Error handling connection: {e}", exc_info=True)

        finally:
            # Cleanup
            if websocket:
                await self.connection_manager.unregister(websocket)

    async def broadcast_to_all(self, message: dict, exclude_players: set = None):
        """
        Broadcast a message to all connected clients.

        Args:
            message: Message dict to broadcast
            exclude_players: Set of player objects to exclude
        """
        exclude_websockets = set()
        if exclude_players:
            for player in exclude_players:
                exclude_websockets.add(player.websocket)

        await self.connection_manager.broadcast(message, exclude=exclude_websockets)

    async def send_update_to_all(self, force_full: bool = False):
        """
        Send game state updates to all connected players.

        Args:
            force_full: If True, send full update; otherwise send delta
        """
        players = self.connection_manager.get_all_players()

        tasks = []
        for player in players:
            if force_full:
                task = self.message_sender.send_full_update(player)
            else:
                task = self.message_sender.send_delta_update(player)
            tasks.append(task)

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    async def send_timer_tick_to_all(self):
        """Send timer tick to all connected players."""
        players = self.connection_manager.get_all_players()

        tasks = []
        for player in players:
            tasks.append(self.message_sender.send_timer_tick(player))

        if tasks:
            await asyncio.gather(*tasks, return_exceptions=True)

    def get_connection_count(self) -> int:
        """Get number of active connections."""
        return self.connection_manager.get_connection_count()


# Global WebSocket handler instance
_websocket_handler = None


def get_websocket_handler() -> WebSocketHandler:
    """Get the global WebSocket handler instance."""
    global _websocket_handler
    if _websocket_handler is None:
        _websocket_handler = WebSocketHandler()
    return _websocket_handler


def reset_websocket_handler():
    """Reset the global WebSocket handler (useful for testing)."""
    global _websocket_handler
    _websocket_handler = WebSocketHandler()
