"""
Lobby chat handlers for player communication in the lobby.
"""
import logging
from typing import Optional
from ..auth import get_auth_manager
from ..message_sender import get_message_sender

logger = logging.getLogger(__name__)

# Store recent lobby messages (in-memory for now)
_recent_lobby_messages = []
MAX_LOBBY_MESSAGES = 100


async def handle_lobby_chat(websocket, data: dict):
    """
    Handle LOBBY_CHAT message.
    Broadcasts chat message to all players in the lobby.

    Message format:
    {
        "type": "LOBBY_CHAT",
        "token": "session_token",
        "text": "Hello everyone!"
    }
    """
    auth_manager = get_auth_manager()
    sender = get_message_sender()

    # Validate session
    token = data.get("token")
    if not token:
        await sender.send_error_ws(websocket, "No session token provided")
        return

    account = auth_manager.validate_session(token)
    if not account:
        await sender.send_error_ws(websocket, "Invalid session")
        return

    # Get message text
    text = data.get("text", "").strip()
    if not text:
        return

    # Limit message length
    if len(text) > 500:
        text = text[:500]

    # Create message
    chat_message = {
        "type": "LOBBY_CHAT",
        "username": account.username,
        "text": text,
        "timestamp": None  # Client will add local timestamp
    }

    # Store in recent messages
    _recent_lobby_messages.append(chat_message)
    if len(_recent_lobby_messages) > MAX_LOBBY_MESSAGES:
        _recent_lobby_messages.pop(0)

    # Broadcast to all connected websockets in lobby
    # For now, we'll send to the specific websocket
    # In the future, track all lobby connections and broadcast to all
    await sender.send_message_ws(websocket, chat_message)

    logger.info(f"Lobby chat from {account.username}: {text[:50]}")
