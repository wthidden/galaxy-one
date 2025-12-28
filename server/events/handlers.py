"""
Event handlers that react to game events.
These handlers subscribe to the event bus and perform actions like
sending updates to players, triggering animations, etc.
"""
import logging
from .event_types import (
    FleetMovedEvent,
    CombatEvent,
    WorldCapturedEvent,
    ProductionEvent,
    PlayerJoinedEvent,
    TurnProcessedEvent
)

logger = logging.getLogger(__name__)


async def on_fleet_moved(event: FleetMovedEvent):
    """
    Handle fleet movement - send animation triggers to observers.

    Args:
        event: FleetMovedEvent
    """
    from ..websocket_handler import get_websocket_handler
    from ..game.state import get_game_state

    logger.info(f"Fleet {event.fleet_id} moved: W{event.from_world} -> W{event.to_world}")

    ws_handler = get_websocket_handler()
    game_state = get_game_state()

    # Find all players who can observe this movement
    observers = set()
    for player in game_state.get_all_players():
        # Player can observe if they have presence at origin or destination
        for world_id in [event.from_world, event.to_world]:
            if world_id in [w.id for w in player.worlds]:
                observers.add(player)
                break
            if any(f.world.id == world_id for f in player.fleets):
                observers.add(player)
                break

    # Send animation trigger to observers
    sender = ws_handler.message_sender
    for observer in observers:
        await sender.send_animation(observer, {
            "animation_type": "fleet_movement",
            "fleet_id": event.fleet_id,
            "from_world": event.from_world,
            "to_world": event.to_world,
            "path": event.path,
            "duration": 2000  # 2 seconds
        })

        # Also send event notification
        if observer.name == event.owner_name:
            await sender.send_event(
                observer,
                f"Fleet {event.fleet_id} moved to World {event.to_world}.",
                "info"
            )


async def on_combat(event: CombatEvent):
    """
    Handle combat - notify participants and observers.

    Args:
        event: CombatEvent
    """
    from ..websocket_handler import get_websocket_handler
    from ..game.state import get_game_state

    logger.info(f"Combat at W{event.world_id}: {event.combat_type}")

    ws_handler = get_websocket_handler()
    game_state = get_game_state()
    sender = ws_handler.message_sender

    # Get participants
    attacker = game_state.get_player_by_id(event.attacker_id) if event.attacker_id else None
    defender = game_state.get_player_by_id(event.defender_id) if event.defender_id else None

    # Notify attacker
    if attacker:
        await sender.send_event(
            attacker,
            f"Combat at W{event.world_id}! Your losses: {event.attacker_losses}",
            "combat"
        )

    # Notify defender
    if defender:
        await sender.send_event(
            defender,
            f"Combat at W{event.world_id}! Your losses: {event.defender_losses}",
            "combat"
        )


async def on_world_captured(event: WorldCapturedEvent):
    """
    Handle world capture - notify new owner and send updates.

    Args:
        event: WorldCapturedEvent
    """
    from ..websocket_handler import get_websocket_handler
    from ..game.state import get_game_state

    logger.info(f"World {event.world_id} captured by player {event.new_owner_id}")

    ws_handler = get_websocket_handler()
    game_state = get_game_state()
    sender = ws_handler.message_sender

    # Notify new owner
    new_owner = game_state.get_player_by_id(event.new_owner_id)
    if new_owner:
        await sender.send_event(
            new_owner,
            f"Captured World {event.world_id}!",
            "capture"
        )

    # Notify old owner
    if event.old_owner_id:
        old_owner = game_state.get_player_by_id(event.old_owner_id)
        if old_owner:
            await sender.send_event(
                old_owner,
                f"Lost World {event.world_id}!",
                "combat"
            )


async def on_production(event: ProductionEvent):
    """
    Handle production - just log for now (could send notifications).

    Args:
        event: ProductionEvent
    """
    logger.debug(
        f"Production at W{event.world_id}: "
        f"Metal +{event.metal_produced}, Pop +{event.population_growth}"
    )


async def on_player_joined(event: PlayerJoinedEvent):
    """
    Handle player join - broadcast to all players.

    Args:
        event: PlayerJoinedEvent
    """
    from ..websocket_handler import get_websocket_handler

    logger.info(f"Player {event.player_name} joined as {event.character_type}")

    ws_handler = get_websocket_handler()

    # Send full update to all players (player count changed)
    await ws_handler.send_update_to_all(force_full=False)


async def on_turn_processed(event: TurnProcessedEvent):
    """
    Handle turn processing - send full updates to all players.

    Args:
        event: TurnProcessedEvent
    """
    from ..websocket_handler import get_websocket_handler
    from ..message_sender import get_message_sender
    from ..game.state import get_game_state

    logger.info(f"Turn {event.game_turn} processed")

    ws_handler = get_websocket_handler()
    sender = get_message_sender()
    game_state = get_game_state()

    # Send full update to all players
    await ws_handler.send_update_to_all(force_full=True)

    # Send info message
    for player in game_state.get_all_players():
        await sender.send_info(
            player,
            f"Turn {event.game_turn} processed. Next turn in {event.turn_duration}s."
        )


def register_all_handlers():
    """Register all event handlers with the event bus."""
    from .event_bus import get_event_bus

    event_bus = get_event_bus()

    # Register handlers
    event_bus.subscribe("FLEET_MOVED", on_fleet_moved)
    event_bus.subscribe("COMBAT", on_combat)
    event_bus.subscribe("WORLD_CAPTURED", on_world_captured)
    event_bus.subscribe("PRODUCTION", on_production)
    event_bus.subscribe("PLAYER_JOINED", on_player_joined)
    event_bus.subscribe("TURN_PROCESSED", on_turn_processed)

    logger.info("Registered all event handlers")
