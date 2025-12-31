"""
Lobby message handlers for game management.
"""
import logging
from typing import Optional
from ..auth import get_auth_manager
from ..game_manager import get_game_manager
from ..message_sender import get_message_sender

logger = logging.getLogger(__name__)


async def handle_list_games(websocket, data: dict):
    """
    Handle LIST_GAMES message.
    Returns list of games player is in and available games to join.

    Message format:
    {
        "type": "LIST_GAMES",
        "token": "session_token"
    }
    """
    auth_manager = get_auth_manager()
    game_manager = get_game_manager()
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

    # Get player's games
    my_games = game_manager.get_player_games(account.id)
    my_games_info = [game.to_lobby_info() for game in my_games]

    # Get available games
    available_games = game_manager.get_available_games(account.id)
    available_games_info = [game.to_lobby_info() for game in available_games]

    # Send response
    await sender.send_message_ws(websocket, {
        "type": "GAMES_LIST",
        "my_games": my_games_info,
        "available_games": available_games_info
    })


async def handle_create_game(websocket, data: dict):
    """
    Handle CREATE_GAME message.

    Message format:
    {
        "type": "CREATE_GAME",
        "token": "session_token",
        "name": "Game Name",
        "character_type": "Empire Builder",
        "character_name": "Emperor",
        "max_players": 6,
        "map_size": 100
    }
    """
    auth_manager = get_auth_manager()
    game_manager = get_game_manager()
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

    # Get parameters
    game_name = data.get("name")
    character_type = data.get("character_type", "Empire Builder")
    character_name = data.get("character_name", account.username)
    max_players = data.get("max_players", 6)
    map_size = data.get("map_size", 100)

    if not game_name:
        await sender.send_error_ws(websocket, "Game name required")
        return

    # Create game
    success, message, game = game_manager.create_game(
        name=game_name,
        created_by=account.id,
        max_players=max_players,
        map_size=map_size
    )

    if not success:
        await sender.send_error_ws(websocket, message)
        return

    # Add creator as first player
    success, join_message = game.add_player(
        player_id=account.id,
        player_name=account.username,
        character_type=character_type,
        character_name=character_name,
        websocket=websocket
    )

    if not success:
        await sender.send_error_ws(websocket, join_message)
        return

    # Send success response
    await sender.send_message_ws(websocket, {
        "type": "GAME_CREATED",
        "game": game.to_lobby_info(),
        "message": f"Created game '{game_name}'"
    })

    logger.info(f"Player {account.username} created game {game_name} (ID: {game.id})")


async def handle_join_game(websocket, data: dict):
    """
    Handle JOIN_GAME message.

    Message format:
    {
        "type": "JOIN_GAME",
        "token": "session_token",
        "game_id": "game_uuid",
        "character_type": "Merchant",
        "character_name": "Trader Bob"
    }
    """
    auth_manager = get_auth_manager()
    game_manager = get_game_manager()
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

    # Get parameters
    game_id = data.get("game_id")
    character_type = data.get("character_type", "Empire Builder")
    character_name = data.get("character_name", account.username)

    if not game_id:
        await sender.send_error_ws(websocket, "Game ID required")
        return

    # Get game
    game = game_manager.get_game(game_id)
    if not game:
        await sender.send_error_ws(websocket, "Game not found")
        return

    # Add player to game
    success, message = game.add_player(
        player_id=account.id,
        player_name=account.username,
        character_type=character_type,
        character_name=character_name,
        websocket=websocket
    )

    if not success:
        await sender.send_error_ws(websocket, message)
        return

    # Send success response
    await sender.send_message_ws(websocket, {
        "type": "GAME_JOINED",
        "game": game.to_lobby_info(),
        "message": message
    })

    logger.info(f"Player {account.username} joined game {game.name} (ID: {game.id})")


async def handle_leave_game(websocket, data: dict):
    """
    Handle LEAVE_GAME message.

    Message format:
    {
        "type": "LEAVE_GAME",
        "token": "session_token",
        "game_id": "game_uuid"
    }
    """
    auth_manager = get_auth_manager()
    game_manager = get_game_manager()
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

    # Get parameters
    game_id = data.get("game_id")
    if not game_id:
        await sender.send_error_ws(websocket, "Game ID required")
        return

    # Get game
    game = game_manager.get_game(game_id)
    if not game:
        await sender.send_error_ws(websocket, "Game not found")
        return

    # Remove player from game
    success, message = game.remove_player(account.id)
    if not success:
        await sender.send_error_ws(websocket, message)
        return

    # Send success response
    await sender.send_message_ws(websocket, {
        "type": "GAME_LEFT",
        "game_id": game_id,
        "message": message
    })

    logger.info(f"Player {account.username} left game {game.name} (ID: {game.id})")


async def handle_get_game_info(websocket, data: dict):
    """
    Handle GET_GAME_INFO message.
    Returns detailed info about a specific game including scoreboard.

    Message format:
    {
        "type": "GET_GAME_INFO",
        "token": "session_token",
        "game_id": "game_uuid"
    }
    """
    auth_manager = get_auth_manager()
    game_manager = get_game_manager()
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

    # Get parameters
    game_id = data.get("game_id")
    if not game_id:
        await sender.send_error_ws(websocket, "Game ID required")
        return

    # Get game
    game = game_manager.get_game(game_id)
    if not game:
        await sender.send_error_ws(websocket, "Game not found")
        return

    # Get scoreboard
    scoreboard = game.get_scoreboard()

    # Send detailed info
    await sender.send_message_ws(websocket, {
        "type": "GAME_INFO",
        "game": game.to_dict(include_state=False),
        "scoreboard": scoreboard
    })


async def handle_enter_game(websocket, data: dict):
    """
    Handle ENTER_GAME message.
    Registers the player with the game and initializes their empire if needed.

    Message format:
    {
        "type": "ENTER_GAME",
        "token": "session_token",
        "game_id": "game_uuid"
    }
    """
    from ..auth.auth_manager import get_auth_manager
    from ..game_manager import get_game_manager
    from ..message_sender import get_message_sender
    from ..connection_manager import get_connection_manager
    from ..game.state import get_game_state
    from ..game.entities import Player

    auth_manager = get_auth_manager()
    game_manager = get_game_manager()
    sender = get_message_sender()
    connection_manager = get_connection_manager()
    game_state = get_game_state()

    # Validate session
    token = data.get("token")
    if not token:
        await sender.send_error_ws(websocket, "No session token provided")
        return

    account = auth_manager.validate_session(token)
    if not account:
        await sender.send_error_ws(websocket, "Invalid session")
        return

    # Get parameters
    game_id = data.get("game_id")
    if not game_id:
        await sender.send_error_ws(websocket, "Game ID required")
        return

    # Get game
    game = game_manager.get_game(game_id)
    if not game:
        await sender.send_error_ws(websocket, "Game not found")
        return

    # Check if player is in this game
    if account.id not in game.players:
        await sender.send_error_ws(websocket, "You are not in this game")
        return

    player_in_game = game.players[account.id]

    # Check if player already exists in game state (reconnection)
    existing_player = None
    for p in game_state.players.values():
        if p.name == player_in_game.character_name:
            existing_player = p
            break

    if existing_player:
        # Reconnect existing player
        # Update websocket in existing player
        existing_player.websocket = websocket
        # Manually register with connection manager
        connection_manager._connections[websocket] = existing_player
        connection_manager._players_by_id[existing_player.id] = existing_player

        await sender.send_info(existing_player, f"Welcome back, {existing_player.name}!")
        await sender.send_full_update(existing_player)
        logger.info(f"Player {existing_player.name} reconnected to game")
    else:
        # New player - initialize them using JOIN logic
        # Get next player ID from game state
        next_player_id = len(game_state.players) + 1

        # Create player entity
        player = Player(player_id=next_player_id, name=player_in_game.character_name, websocket=websocket)
        player.character_type = player_in_game.character_type
        player.turn_timer_minutes = 60  # Default

        # Register with connection manager manually
        connection_manager._connections[websocket] = player
        connection_manager._players_by_id[player.id] = player

        # Add to game state
        game_state.players[next_player_id] = player

        # Import JOIN logic
        from ..game.command_handlers import handle_join

        # Create fake command parts for JOIN
        command_parts = ["JOIN", player_in_game.character_name, player_in_game.character_type]
        full_command = " ".join(command_parts)

        # Execute JOIN logic to set up homeworld and fleets
        await handle_join(player, full_command, command_parts)

        # Send initial full update
        await sender.send_full_update(player)

        logger.info(f"Player {player.name} ({player.character_type}) entered game {game.name}")

    # Send success response
    await sender.send_message_ws(websocket, {
        "type": "GAME_ENTERED",
        "game_id": game_id,
        "message": "Entered game successfully"
    })
