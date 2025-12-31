"""
Authentication message handlers.
"""
import logging
from .auth_manager import get_auth_manager
from ..message_sender import get_message_sender

logger = logging.getLogger(__name__)


async def handle_signup(websocket, data: dict):
    """
    Handle SIGNUP message.

    Message format:
    {
        "type": "SIGNUP",
        "username": "player123",
        "password": "securepass",
        "email": "player@example.com"  (optional)
    }
    """
    auth_manager = get_auth_manager()
    sender = get_message_sender()

    username = data.get("username")
    password = data.get("password")
    email = data.get("email")

    if not username or not password:
        await sender.send_error_ws(websocket, "Username and password required")
        return

    # Attempt signup
    success, message, session = auth_manager.signup(username, password, email)

    if not success:
        await sender.send_error_ws(websocket, message)
        return

    # Send success response with token
    await sender.send_message_ws(websocket, {
        "type": "AUTH_SUCCESS",
        "token": session.token,
        "player_id": session.player_id,
        "username": username,
        "message": message
    })

    logger.info(f"Signup successful: {username}")


async def handle_login(websocket, data: dict):
    """
    Handle LOGIN message.

    Message format:
    {
        "type": "LOGIN",
        "username": "player123",
        "password": "securepass"
    }
    """
    auth_manager = get_auth_manager()
    sender = get_message_sender()

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        await sender.send_error_ws(websocket, "Username and password required")
        return

    # Attempt login
    success, message, session = auth_manager.login(username, password)

    if not success:
        await sender.send_error_ws(websocket, message)
        return

    # Send success response with token
    await sender.send_message_ws(websocket, {
        "type": "AUTH_SUCCESS",
        "token": session.token,
        "player_id": session.player_id,
        "username": username,
        "message": message
    })

    logger.info(f"Login successful: {username}")


async def handle_logout(websocket, data: dict):
    """
    Handle LOGOUT message.

    Message format:
    {
        "type": "LOGOUT",
        "token": "session_token"
    }
    """
    auth_manager = get_auth_manager()
    sender = get_message_sender()

    token = data.get("token")

    if not token:
        await sender.send_error_ws(websocket, "No session token provided")
        return

    # Attempt logout
    success, message = auth_manager.logout(token)

    if not success:
        await sender.send_error_ws(websocket, message)
        return

    # Send success response
    await sender.send_message_ws(websocket, {
        "type": "LOGOUT_SUCCESS",
        "message": message
    })

    logger.info(f"Logout successful for token: {token[:8]}...")


async def handle_validate_session(websocket, data: dict):
    """
    Handle VALIDATE_SESSION message.
    Check if a session token is still valid.

    Message format:
    {
        "type": "VALIDATE_SESSION",
        "token": "session_token"
    }
    """
    auth_manager = get_auth_manager()
    sender = get_message_sender()

    token = data.get("token")

    if not token:
        await sender.send_error_ws(websocket, "No session token provided")
        return

    # Validate session
    account = auth_manager.validate_session(token)

    if not account:
        await sender.send_message_ws(websocket, {
            "type": "SESSION_INVALID"
        })
        return

    # Send success response
    await sender.send_message_ws(websocket, {
        "type": "SESSION_VALID",
        "player_id": account.id,
        "username": account.username
    })
