"""
World ownership and fleet capture mechanics.
"""
import logging
from ..state import get_game_state
from ...events.event_bus import get_event_bus
from ...events.event_types import WorldCapturedEvent
from ...message_sender import get_message_sender
import time

logger = logging.getLogger(__name__)


async def check_world_ownership(world) -> bool:
    """
    Check and update world ownership based on presence.

    Args:
        world: World to check

    Returns:
        True if ownership changed
    """
    game_state = get_game_state()
    event_bus = get_event_bus()

    old_owner = world.owner
    changed = False

    # Check if world has defending forces
    defender = None
    if world.owner and (world.iships > 0 or world.pships > 0):
        defender = world.owner

    # Get players with ships orbiting
    orbiting_players = {f.owner for f in world.fleets if f.ships > 0 and f.owner is not None}

    if defender:
        # Defended world keeps owner
        pass
    elif len(orbiting_players) == 1:
        # Single player presence - they capture it
        new_owner = list(orbiting_players)[0]
        if world.owner != new_owner:
            if world.owner:
                world.owner.worlds.remove(world)
            world.owner = new_owner
            new_owner.worlds.append(world)
            changed = True
    elif len(orbiting_players) > 1:
        # Contested - neutralize
        if world.owner:
            world.owner.worlds.remove(world)
            world.owner = None
            changed = True
    else:
        # No presence - neutralize
        if world.owner:
            world.owner.worlds.remove(world)
            world.owner = None
            changed = True

    # Publish ownership change event
    if changed:
        event = WorldCapturedEvent(
            world_id=world.id,
            old_owner_id=old_owner.id if old_owner else None,
            new_owner_id=world.owner.id if world.owner else None,
            new_owner_name=world.owner.name if world.owner else "[Neutral]",
            game_turn=game_state.game_turn,
            timestamp=time.time()
        )
        await event_bus.publish(event)

    return changed


async def handle_fleet_captures(world):
    """
    Handle capture of empty fleets at a world.

    Args:
        world: World to process fleet captures at
    """
    sender = get_message_sender()

    # Determine who has ships present
    owners_with_ships = set()
    for f in world.fleets:
        if f.ships > 0 and f.owner is not None:
            owners_with_ships.add(f.owner)

    # Include world garrison
    if world.owner and (world.iships > 0 or world.pships > 0):
        owners_with_ships.add(world.owner)

    # Single owner - captures empty fleets
    if len(owners_with_ships) == 1:
        sole_owner = next(iter(owners_with_ships))
        for f in world.fleets:
            if f.ships == 0 and f.owner != sole_owner:
                old_owner = f.owner
                if old_owner:
                    old_owner.fleets.remove(f)
                    await sender.send_event(
                        old_owner,
                        f"Lost control of empty Fleet {f.id} at World {world.id}.",
                        "combat"
                    )
                f.owner = sole_owner
                sole_owner.fleets.append(f)
                await sender.send_event(
                    sole_owner,
                    f"Captured empty Fleet {f.id} at World {world.id}.",
                    "capture"
                )
    else:
        # Multiple owners or no owners - neutralize empty fleets
        for f in world.fleets:
            if f.ships == 0 and f.owner is not None:
                old_owner = f.owner
                old_owner.fleets.remove(f)
                await sender.send_event(
                    old_owner,
                    f"Lost control of empty Fleet {f.id} at World {world.id} (Neutralized).",
                    "combat"
                )
                f.owner = None
