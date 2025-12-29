"""
Command handlers for processing player commands.
"""
import logging
from .commands import parse_command, has_exclusive_order
from .state import get_game_state
from ..message_sender import get_message_sender
from ..events.event_bus import get_event_bus
from ..events.event_types import PlayerJoinedEvent
from .help_content import get_help
import time

logger = logging.getLogger(__name__)

# Game constants
HOMEWORLD_POPULATION = 50
HOMEWORLD_INDUSTRY = 30
HOMEWORLD_METAL = 30
HOMEWORLD_MINES = 2
HOMEWORLD_ISHIPS = 1
HOMEWORLD_PSHIPS = 1
HOMEWORLD_STARTING_SHIPS = 10
CHARACTER_TYPES = ["Empire Builder", "Merchant", "Pirate", "Artifact Collector", "Berserker", "Apostle"]


async def handle_command_message(player, data):
    """
    Handle command messages from players.

    Args:
        player: The player sending the command
        data: Message data containing command text
    """
    command_text = data.get("text", "").strip()
    if not command_text:
        return

    parts = command_text.split()
    if not parts:
        return

    cmd = parts[0].upper()
    sender = get_message_sender()
    game_state = get_game_state()

    # HELP command - always available
    if cmd == "HELP" or cmd == "?":
        await handle_help(player, parts)
        return

    # JOIN command - special handling
    if cmd == "JOIN":
        await handle_join(player, command_text, parts)
        return

    # Check if player has joined
    if not player.worlds and not player.fleets:
        await sender.send_error(player, "Please JOIN the game first.")
        return

    # TURN command - end turn
    if cmd == "TURN":
        await handle_turn(player)
        return

    # SAY command - chat with other players
    if cmd == "SAY" or cmd == "CHAT":
        await handle_say(player, command_text, parts)
        return

    # Parse and validate command
    command = parse_command(player, command_text, game_state)

    if not command:
        await sender.send_error(player, f"Unknown command: {command_text}")
        return

    # Check for exclusive orders
    if hasattr(command, 'fleet_id') and has_exclusive_order(player, command.fleet_id):
        await sender.send_error(player, "Fleet already has an exclusive order.")
        return

    # Validate command
    is_valid, error_message = command.validate(game_state)

    if not is_valid:
        await sender.send_error(player, error_message)
        return

    # Queue the order
    order = command.to_order()
    player.orders.append(order)

    # Send confirmation
    await sender.send_info(player, f"Order queued: {command.get_description()}")

    # Send updated state
    await sender.send_delta_update(player)


async def handle_join(player, full_command, parts):
    """
    Handle JOIN command.

    Args:
        player: The player
        full_command: Full command text
        parts: Command split into parts
    """
    sender = get_message_sender()
    game_state = get_game_state()
    event_bus = get_event_bus()

    if len(parts) < 2:
        await sender.send_error(player, "Usage: JOIN <name> [timer_minutes] [character_type]")
        return

    # Parse command: JOIN <name> [timer_minutes] <character_type>
    # Example: "JOIN Alice 60 Empire Builder"
    full_args = " ".join(parts[1:])

    # Try to find character type at end
    char_type = "EmpireBuilder"
    name = full_args

    for ct in CHARACTER_TYPES:
        if full_args.upper().endswith(ct.upper()):
            char_type = ct
            name = full_args[:-(len(ct))].strip()
            break

    # Extract turn timer if present (a number)
    turn_timer = 60  # Default 60 minutes
    name_parts = name.split()
    if name_parts and name_parts[-1].isdigit():
        turn_timer = int(name_parts[-1])
        # Clamp between 5 and 1440 minutes (5 min to 24 hours)
        turn_timer = max(5, min(1440, turn_timer))
        name = " ".join(name_parts[:-1])

    if not name:
        await sender.send_error(player, "Please provide a name")
        return

    # Update player
    player.name = name
    player.character_type = char_type
    player.turn_timer_minutes = turn_timer

    # Find starting world - must be at least 1 hop from other homeworlds
    import random

    # Get all existing homeworlds
    existing_homeworlds = [w.id for w in game_state.worlds.values() if w.key and w.owner is not None]

    # Build set of worlds that are too close (homeworlds + their direct neighbors)
    excluded_worlds = set(existing_homeworlds)
    for hw_id in existing_homeworlds:
        hw = game_state.worlds[hw_id]
        excluded_worlds.update(hw.connections)

    # Find neutral worlds that are at least 1 hop from any existing homeworld
    candidates = [w for w in game_state.worlds.values()
                 if w.owner is None and w.id not in excluded_worlds]

    if candidates:
        start_world = random.choice(candidates)
    else:
        # Fallback if no distant worlds available - just pick any neutral world
        candidates = [w for w in game_state.worlds.values() if w.owner is None]
        if candidates:
            start_world = random.choice(candidates)
        else:
            # Last resort - pick any world
            start_world = game_state.worlds[random.randint(1, game_state.map_size)]

    # Remove existing owner if any
    if start_world.owner:
        start_world.owner.worlds.remove(start_world)

    # Relocate neutral fleets from start world
    existing_fleets = [f for f in start_world.fleets if f.owner is None]
    for f in existing_fleets:
        start_world.fleets.remove(f)
        new_world = game_state.worlds[random.randint(1, game_state.map_size)]
        while new_world == start_world:
            new_world = game_state.worlds[random.randint(1, game_state.map_size)]
        f.world = new_world
        new_world.fleets.append(f)

    # Setup homeworld
    start_world.owner = player
    start_world.key = True  # Mark as homeworld
    start_world.population = HOMEWORLD_POPULATION
    start_world.industry = HOMEWORLD_INDUSTRY
    start_world.metal = HOMEWORLD_METAL
    start_world.mines = HOMEWORLD_MINES
    start_world.iships = HOMEWORLD_ISHIPS
    start_world.pships = HOMEWORLD_PSHIPS
    player.worlds.append(start_world)

    # Homeworlds should not have artifacts - relocate any to neutral worlds
    if start_world.artifacts:
        import random
        for artifact in list(start_world.artifacts):
            # Find a neutral world to move it to
            neutral_worlds = [w for w in game_state.worlds.values()
                            if w.owner is None and w != start_world]
            if neutral_worlds:
                target_world = random.choice(neutral_worlds)
                start_world.artifacts.remove(artifact)
                target_world.artifacts.append(artifact)
                logger.info(f"Relocated artifact {artifact.name} from homeworld {start_world.id} to neutral world {target_world.id}")

    # Update known worlds
    player.known_worlds[start_world.id] = game_state.game_turn
    for neighbor in start_world.connections:
        player.known_worlds[neighbor] = game_state.game_turn

    # Assign neutral fleets
    import random
    neutral_fleets = [
        f for f in game_state.fleets.values()
        if f.owner is None and f.world != start_world
    ]

    if len(neutral_fleets) >= 5:
        fleets_to_assign = random.sample(neutral_fleets, 5)
    else:
        fleets_to_assign = neutral_fleets

    for f in fleets_to_assign:
        f.world.fleets.remove(f)
        f.world = start_world
        start_world.fleets.append(f)
        f.owner = player
        player.fleets.append(f)
        f.ships = HOMEWORLD_STARTING_SHIPS

    # Send welcome
    await sender.send_info(
        player,
        f"Welcome, {name}! You are a {char_type} starting at World {start_world.id}."
    )

    # Publish event
    event = PlayerJoinedEvent(
        player_id=player.id,
        player_name=player.name,
        character_type=char_type,
        homeworld_id=start_world.id,
        game_turn=game_state.game_turn,
        timestamp=time.time()
    )
    await event_bus.publish(event)


async def handle_turn(player):
    """
    Handle TURN command - mark player as ready.

    Args:
        player: The player ending their turn
    """
    sender = get_message_sender()
    game_state = get_game_state()

    if player.websocket not in game_state.players_ready:
        game_state.players_ready.add(player.websocket)
        await sender.send_info(player, "You have ended your turn. Waiting for others...")

        # Check if all players ready
        if len(game_state.players_ready) == len(game_state.players):
            # Import here to avoid circular dependency
            from .turn_processor import process_turn
            await process_turn()
        else:
            # Send update to all players (ready count changed)
            from ..websocket_handler import get_websocket_handler
            ws_handler = get_websocket_handler()
            await ws_handler.send_update_to_all(force_full=False)


async def handle_help(player, parts):
    """
    Handle HELP command - show help information.

    Args:
        player: The player requesting help
        parts: Command parts (e.g., ['HELP', 'commands'], ['HELP', 'F5'], ['HELP', 'W3'])
    """
    sender = get_message_sender()
    game_state = get_game_state()

    # Parse context from command
    topic = None
    context = None

    if len(parts) > 1:
        arg = parts[1].upper()

        # Check if asking for help on specific fleet (e.g., "HELP F5")
        if arg.startswith('F') and len(arg) > 1 and arg[1:].isdigit():
            fleet_id = int(arg[1:])
            # Find this fleet
            fleet = next((f for f in player.fleets if f.id == fleet_id), None)
            if fleet:
                context = {
                    'selected_fleet': {
                        'id': fleet.id,
                        'key': fleet.world.key if fleet.world else 'Unknown',
                        'ships': fleet.ships,
                        'cargo': fleet.cargo,
                        'artifacts': [{'id': a.id} for a in fleet.artifacts]
                    },
                    'player': player
                }

        # Check if asking for help on specific world (e.g., "HELP W3")
        elif arg.startswith('W') and len(arg) > 1 and arg[1:].isdigit():
            world_id = int(arg[1:])
            # Find this world
            world = next((w for w in player.worlds if w.id == world_id), None)
            if world:
                context = {
                    'selected_world': {
                        'id': world.id,
                        'name': world.name,
                        'key': world.key,
                        'population': world.population,
                        'industry': world.industry,
                        'metal': world.metal,
                        'artifacts': [{'id': a.id} for a in world.artifacts]
                    },
                    'player': player
                }

        # Otherwise it's a regular topic
        else:
            topic = " ".join(parts[1:])

    # Get help content
    help_text = get_help(topic, context)

    # Send help as event message (supports HTML)
    await sender.send_event(player, help_text, event_type='help')


async def handle_say(player, full_command, parts):
    """
    Handle SAY/CHAT command - send a message to all players.

    Args:
        player: The player sending the message
        full_command: Full command text (e.g., "SAY Hello everyone!")
        parts: Command parts
    """
    sender = get_message_sender()

    # Extract message text (everything after SAY or CHAT)
    if len(parts) < 2:
        await sender.send_error(player, "Usage: SAY <message> or CHAT <message>")
        return

    # Get the message (everything after the command)
    cmd_word = parts[0]
    message_start = full_command.find(cmd_word) + len(cmd_word)
    message = full_command[message_start:].strip()

    if not message:
        await sender.send_error(player, "Usage: SAY <message> or CHAT <message>")
        return

    # Broadcast message to all players
    game_state = get_game_state()
    chat_text = f"<strong>{player.name}:</strong> {message}"

    for p in game_state.players.values():
        await sender.send_event(p, chat_text, event_type='chat')
