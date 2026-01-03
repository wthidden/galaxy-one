"""
StarWeb Game Server - Main Entry Point

Modular architecture with:
- Event-driven communication
- Clean WebSocket management
- Separated game mechanics
- Delta updates for efficiency
"""
import asyncio
import websockets
import http.server
import socketserver
import threading
import os
import logging
import time

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Import core systems
from .websocket_handler import get_websocket_handler
from .message_router import get_message_router
from .game.state import get_game_state
from .game.command_handlers import handle_command_message
from .events.handlers import register_all_handlers
from .admin_message import get_admin_watcher


class StarWebHTTPHandler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP handler with document download endpoints."""

    def do_GET(self):
        """Handle GET requests with custom routes."""
        # Document download routes
        documents = {
            '/manual': ('PLAYER_MANUAL.md', 'StarWeb_Player_Manual.md'),
            '/commands': ('COMMANDS.md', 'StarWeb_Commands.md'),
            '/characters': ('CHARACTER_GUIDE.md', 'StarWeb_Character_Guide.md')
        }

        if self.path in documents:
            source_file, download_name = documents[self.path]
            try:
                file_path = os.path.join(os.getcwd(), source_file)
                with open(file_path, 'rb') as f:
                    content = f.read()

                self.send_response(200)
                self.send_header('Content-Type', 'text/markdown; charset=utf-8')
                self.send_header('Content-Disposition', f'attachment; filename="{download_name}"')
                self.send_header('Content-Length', str(len(content)))
                self.end_headers()
                self.wfile.write(content)
                return
            except FileNotFoundError:
                self.send_error(404, f"Document not found: {source_file}")
                return
            except Exception as e:
                logger.error(f"Error serving {source_file}: {e}")
                self.send_error(500, "Internal server error")
                return

        # Default handling for other paths
        super().do_GET()


def run_http_server():
    """Run HTTP server for serving static files."""
    PORT = 8000

    # Change to parent directory to serve files
    parent_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    os.chdir(parent_dir)

    Handler = StarWebHTTPHandler
    socketserver.TCPServer.allow_reuse_address = True

    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        logger.info(f"HTTP Server serving at http://0.0.0.0:{PORT}")
        httpd.serve_forever()


async def timer_loop():
    """
    Main game timer loop.
    - Sends timer ticks every second
    - Processes turns when time expires
    """
    from .game.turn_processor import process_turn

    ws_handler = get_websocket_handler()
    game_state = get_game_state()

    logger.info("Timer loop started")

    while True:
        await asyncio.sleep(1)

        if time.time() >= game_state.turn_end_time:
            # Time expired - process turn
            logger.info("Turn timer expired, processing turn...")
            await process_turn()
        else:
            # Send timer tick to all players
            try:
                await ws_handler.send_timer_tick_to_all()
            except Exception as e:
                logger.error(f"Error sending timer tick: {e}")


async def admin_message_loop():
    """
    Watch admin message file and broadcast changes to all players.
    """
    from .message_sender import get_message_sender

    admin_watcher = get_admin_watcher()
    sender = get_message_sender()
    game_state = get_game_state()

    async def broadcast_admin_message(message):
        """Broadcast admin message to all players"""
        logger.info(f"Broadcasting admin message to all players")
        for player in game_state.players.values():
            try:
                await sender.send_admin_message(player, message)
            except Exception as e:
                logger.error(f"Error sending admin message to {player.name}: {e}")

    # Start watching
    await admin_watcher.watch(broadcast_admin_message)


async def main():
    """
    Main server initialization and startup.
    """
    logger.info("="*60)
    logger.info("StarWeb Game Server Starting...")
    logger.info("="*60)

    # Initialize game state
    game_state = get_game_state()

    # Try to load saved game state
    from .game.persistence import get_persistence
    persistence = get_persistence()
    if persistence.load_state(game_state):
        logger.info(f"Loaded saved game state: Turn {game_state.game_turn}")
        logger.info(f"  - {len(game_state.worlds)} worlds")
        logger.info(f"  - {len(game_state.fleets)} fleets")
        logger.info(f"  - {len(game_state.artifacts)} artifacts")
        logger.info(f"  - {len(game_state._persistent_players)} persistent players")
    else:
        logger.info(f"Initialized new game map with {len(game_state.worlds)} worlds")
        logger.info(f"Created {len(game_state.fleets)} neutral fleets")
        logger.info(f"Placed {len(game_state.artifacts)} artifacts")

    # Load accounts and sessions
    logger.info("Loading accounts and sessions...")
    from .auth import get_auth_manager, get_session_manager
    from .persistence.accounts import get_account_persistence

    auth_manager = get_auth_manager()
    session_manager = get_session_manager()
    account_persistence = get_account_persistence()

    # Load saved accounts
    accounts_data = account_persistence.load_accounts()
    auth_manager.load_accounts(accounts_data)

    # Load saved sessions
    sessions_data = account_persistence.load_sessions()
    session_manager.load_sessions(sessions_data)

    # Cleanup expired sessions
    session_manager.cleanup_expired_sessions()

    # Register message handlers
    logger.info("Registering message handlers...")
    message_router = get_message_router()

    # Auth handlers (websocket-level, pre-auth)
    from .auth.auth_handlers import handle_signup, handle_login, handle_logout, handle_validate_session
    message_router.register_websocket_handler("SIGNUP", handle_signup)
    message_router.register_websocket_handler("LOGIN", handle_login)
    message_router.register_websocket_handler("LOGOUT", handle_logout)
    message_router.register_websocket_handler("VALIDATE_SESSION", handle_validate_session)

    # Lobby handlers (websocket-level, authenticated)
    from .lobby import (
        handle_list_games,
        handle_create_game,
        handle_join_game,
        handle_leave_game,
        handle_get_game_info,
        handle_enter_game,
        handle_lobby_chat
    )
    message_router.register_websocket_handler("LIST_GAMES", handle_list_games)
    message_router.register_websocket_handler("CREATE_GAME", handle_create_game)
    message_router.register_websocket_handler("JOIN_GAME", handle_join_game)
    message_router.register_websocket_handler("LEAVE_GAME", handle_leave_game)
    message_router.register_websocket_handler("GET_GAME_INFO", handle_get_game_info)
    message_router.register_websocket_handler("ENTER_GAME", handle_enter_game)
    message_router.register_websocket_handler("LOBBY_CHAT", handle_lobby_chat)

    # Admin handlers (websocket-level, require admin auth)
    from .admin.admin_handlers import (
        handle_admin_list_users,
        handle_admin_create_user,
        handle_admin_delete_user,
        handle_admin_reset_password,
        handle_admin_list_games,
        handle_admin_force_start_game,
        handle_admin_kick_player,
        handle_admin_broadcast,
        handle_admin_view_audit
    )
    message_router.register_websocket_handler("ADMIN_LIST_USERS", handle_admin_list_users)
    message_router.register_websocket_handler("ADMIN_CREATE_USER", handle_admin_create_user)
    message_router.register_websocket_handler("ADMIN_DELETE_USER", handle_admin_delete_user)
    message_router.register_websocket_handler("ADMIN_RESET_PASSWORD", handle_admin_reset_password)
    message_router.register_websocket_handler("ADMIN_LIST_GAMES", handle_admin_list_games)
    message_router.register_websocket_handler("ADMIN_FORCE_START_GAME", handle_admin_force_start_game)
    message_router.register_websocket_handler("ADMIN_KICK_PLAYER", handle_admin_kick_player)
    message_router.register_websocket_handler("ADMIN_BROADCAST", handle_admin_broadcast)
    message_router.register_websocket_handler("ADMIN_VIEW_AUDIT", handle_admin_view_audit)

    # Game handlers (player-level, require game membership)
    message_router.register_handler("command", handle_command_message)

    # Register bug report handler
    from .bug_reporter import get_bug_reporter
    bug_reporter = get_bug_reporter()
    message_router.register_handler("bug_report", bug_reporter.handle_bug_report)

    # Register event handlers
    logger.info("Registering event handlers...")
    register_all_handlers()

    # Start HTTP server in background thread
    logger.info("Starting HTTP server...")
    http_thread = threading.Thread(
        target=run_http_server,
        daemon=True
    )
    http_thread.start()

    # Start timer loop
    logger.info("Starting game timer...")
    asyncio.create_task(timer_loop())

    # Start admin message watcher
    logger.info("Starting admin message watcher...")
    asyncio.create_task(admin_message_loop())

    # Start WebSocket server
    ws_handler = get_websocket_handler()
    logger.info("Starting WebSocket server on ws://0.0.0.0:8765")
    logger.info("="*60)
    logger.info("Server ready! Players can connect.")
    logger.info("="*60)

    # Setup graceful shutdown
    shutdown_event = asyncio.Event()

    def handle_shutdown(signum, frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Received signal {signum}, initiating graceful shutdown...")
        shutdown_event.set()

    import signal
    signal.signal(signal.SIGTERM, handle_shutdown)
    signal.signal(signal.SIGINT, handle_shutdown)

    # Start WebSocket server
    async with websockets.serve(ws_handler.handle_connection, "0.0.0.0", 8765):
        # Wait for shutdown signal
        await shutdown_event.wait()

    # Graceful shutdown
    logger.info("Shutting down gracefully...")

    # Save final game state
    logger.info("Saving final game state...")
    persistence.save_state(game_state)

    # Save accounts and sessions
    logger.info("Saving accounts and sessions...")
    from .auth import get_auth_manager, get_session_manager
    from .persistence.accounts import get_account_persistence

    auth_manager = get_auth_manager()
    session_manager = get_session_manager()
    account_persistence = get_account_persistence()

    account_persistence.save_accounts(auth_manager.get_all_accounts())
    account_persistence.save_sessions(session_manager.get_all_sessions())

    logger.info("Shutdown complete")
    logger.info("="*60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("\nServer stopped by user.")
    except Exception as e:
        logger.error(f"Server error: {e}", exc_info=True)
