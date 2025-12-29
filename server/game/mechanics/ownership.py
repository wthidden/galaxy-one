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

    Ownership rules:
    1. World stays owned if owner has fleets OR iships/pships defending
    2. World becomes neutral if owner has no fleets AND no iships/pships
    3. World is captured on FOLLOWING turn if single player has uncontested presence
    4. World becomes neutral if multiple players contest it

    Args:
        world: World to check

    Returns:
        True if ownership changed
    """
    game_state = get_game_state()
    event_bus = get_event_bus()
    sender = get_message_sender()

    old_owner = world.owner
    changed = False

    # Get players with ships orbiting
    orbiting_players = {f.owner for f in world.fleets if f.ships > 0 and f.owner is not None}

    # Check if current owner still has presence
    owner_has_presence = False
    if world.owner:
        # Owner has presence if they have fleets OR defensive ships
        owner_has_fleets = world.owner in orbiting_players
        owner_has_defense = (world.iships > 0 or world.pships > 0)
        owner_has_presence = owner_has_fleets or owner_has_defense

    # Determine ownership changes
    if world.owner and not owner_has_presence:
        # Current owner lost presence - neutralize immediately
        logger.info(f"World {world.id}: {world.owner.name} lost presence (no fleets, no defense)")
        await sender.send_event(
            world.owner,
            f"Lost World {world.id} - no fleets in orbit and no defenses remaining.",
            "combat"
        )
        world.owner.worlds.remove(world)
        world.owner = None
        world.pending_owner = None
        changed = True

    elif len(orbiting_players) > 1:
        # Multiple players contesting - neutralize if owned, clear pending
        if world.owner and world.owner not in orbiting_players:
            # Owner doesn't have fleet but others do - lose it
            logger.info(f"World {world.id}: Contested by multiple players")
            await sender.send_event(
                world.owner,
                f"Lost World {world.id} - contested by multiple players.",
                "combat"
            )
            world.owner.worlds.remove(world)
            world.owner = None
            changed = True
        world.pending_owner = None

    elif len(orbiting_players) == 1:
        # Single player has presence
        sole_player = list(orbiting_players)[0]

        # Check if there are defending forces from another player
        has_enemy_defense = world.owner and world.owner != sole_player and (world.iships > 0 or world.pships > 0)

        if has_enemy_defense:
            # Enemy defenses block capture
            world.pending_owner = None
        elif world.owner == sole_player:
            # Already owns it, maintain ownership
            world.pending_owner = None
        elif world.pending_owner == sole_player:
            # Same player from last turn - complete the capture!
            logger.info(f"World {world.id}: {sole_player.name} completes capture")
            world.owner = sole_player
            sole_player.worlds.append(world)
            world.pending_owner = None
            changed = True
            await sender.send_event(
                sole_player,
                f"**Captured World {world.id}!** Now under your control.",
                "capture"
            )
        else:
            # New uncontested presence - set pending for next turn
            logger.info(f"World {world.id}: {sole_player.name} pending capture next turn")
            world.pending_owner = sole_player
            await sender.send_event(
                sole_player,
                f"Fleet at World {world.id} - will capture next turn if uncontested.",
                "info"
            )
    else:
        # No presence at all
        world.pending_owner = None
        if world.owner:
            # This case should be handled by the first condition, but just in case
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
