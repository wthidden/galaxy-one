"""
Turn processing orchestration.
Executes all orders in priority order and runs game mechanics.
"""
import logging
import time
from .state import get_game_state
from .mechanics.combat import execute_fire_order, execute_defense_fire_order
from .mechanics.movement import execute_move_order, set_ambush
from .mechanics.production import (
    execute_build_order,
    execute_transfer_order,
    execute_transfer_from_defense_order,
    execute_transfer_artifact_order,
    execute_load_order,
    execute_unload_order,
    process_world_production,
    calculate_player_score
)
from .mechanics.ownership import check_world_ownership, handle_fleet_captures
from ..events.event_bus import get_event_bus
from ..events.event_types import TurnProcessedEvent

logger = logging.getLogger(__name__)

# Constants
INITIAL_TURN_DURATION = 180  # 3 minutes
MAX_TURN_DURATION = 480      # 8 minutes


def group_orders_by_type(orders):
    """
    Group orders by type.

    Args:
        orders: List of order dicts

    Returns:
        Dict mapping order type to list of orders
    """
    grouped = {}
    for order in orders:
        order_type = order.get("type")
        if order_type:
            grouped.setdefault(order_type, []).append(order)
    return grouped


async def process_turn():
    """
    Process a complete game turn.

    1. Execute orders by priority
    2. Run production
    3. Handle fleet/world captures
    4. Reset turn state
    5. Broadcast updates
    """
    game_state = get_game_state()
    event_bus = get_event_bus()

    logger.info(f"Processing turn {game_state.game_turn + 1}")

    game_state.game_turn += 1
    game_state.players_ready.clear()

    # Use average of all players' turn timer preferences
    game_state.current_turn_duration = game_state.get_average_turn_duration_seconds()
    game_state.turn_end_time = time.time() + game_state.current_turn_duration

    # Collect all orders from all players
    all_orders = []
    for player in game_state.get_all_players():
        all_orders.extend(player.orders)
        player.orders = []

    # Group orders by type
    orders_by_type = group_orders_by_type(all_orders)

    # Execute orders in priority order
    logger.info(f"Executing {len(all_orders)} orders")

    # 1. Transfers (can affect other orders)
    for order in orders_by_type.get("TRANSFER", []):
        await execute_transfer_order(order)

    # 1b. Transfers from defenses
    for order in orders_by_type.get("TRANSFER_FROM_DEFENSE", []):
        await execute_transfer_from_defense_order(order)

    # 2. Artifact transfers
    for order in orders_by_type.get("TRANSFER_ARTIFACT", []):
        await execute_transfer_artifact_order(order)

    # 3. Load cargo
    for order in orders_by_type.get("LOAD", []):
        await execute_load_order(order)

    # 4. Unload cargo
    for order in orders_by_type.get("UNLOAD", []):
        await execute_unload_order(order)

    # 5. Builds (before combat)
    for order in orders_by_type.get("BUILD", []):
        await execute_build_order(order)

    # 6. Fire orders
    for order in orders_by_type.get("FIRE", []):
        await execute_fire_order(order)

    # 6b. Defense fire orders
    for order in orders_by_type.get("DEFENSE_FIRE", []):
        await execute_defense_fire_order(order)

    # 7. Set ambush status
    for order in orders_by_type.get("AMBUSH", []):
        fleet_id = order["fleet_id"]
        fleet = game_state.get_fleet(fleet_id)
        if fleet:
            fleet.is_ambushing = True

    # 8. Move orders (last because they can trigger ambushes)
    for order in orders_by_type.get("MOVE", []):
        await execute_move_order(order)

    # Process world production
    logger.info("Processing production")
    for world in game_state.worlds.values():
        await process_world_production(world)

    # Handle empty fleet captures
    logger.info("Handling fleet captures")
    for world in game_state.worlds.values():
        await handle_fleet_captures(world)

    # Check world ownership changes
    logger.info("Checking world ownership")
    for world in game_state.worlds.values():
        await check_world_ownership(world)

    # Calculate scores for all players
    logger.info("Calculating player scores")
    for player in game_state.get_all_players():
        calculate_player_score(player)

    # Reset fleet states
    for fleet in game_state.fleets.values():
        fleet.moved = False
        fleet.is_ambushing = False

    # Update player knowledge
    for player in game_state.get_all_players():
        presence_worlds = {f.world.id for f in player.fleets} | {w.id for w in player.worlds}
        for wid in presence_worlds:
            player.known_worlds[wid] = game_state.game_turn
            world = game_state.get_world(wid)
            if world:
                for neighbor in world.connections:
                    if neighbor not in player.known_worlds:
                        player.known_worlds[neighbor] = game_state.game_turn

    # Publish turn processed event
    event = TurnProcessedEvent(
        turn_duration=game_state.current_turn_duration,
        players_ready=0,
        total_players=len(game_state.players),
        game_turn=game_state.game_turn,
        timestamp=time.time()
    )
    await event_bus.publish(event)

    # Save game state to disk
    from .persistence import get_persistence
    persistence = get_persistence()
    persistence.save_state(game_state)
    logger.info(f"Game state saved after turn {game_state.game_turn}")

    logger.info(f"Turn {game_state.game_turn} complete")
