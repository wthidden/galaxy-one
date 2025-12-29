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

    Ownership rules (per StarWeb official rules):
    1. Capture happens IMMEDIATELY when you're the only player with ships not at peace
    2. Defensive ships (iships/pships) prevent capture
    3. Owner keeps world as long as they have fleets OR defensive ships
    4. Multiple players contesting → neutralize if no defenses
    5. Zero population worlds cannot be owned

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

    # Cannot own zero-population worlds
    if world.population <= 0:
        if world.owner:
            logger.info(f"World {world.id}: Neutralized (zero population)")
            await sender.send_event(
                world.owner,
                f"Lost World {world.id} - population eliminated.",
                "combat"
            )
            world.owner.worlds.remove(world)
            world.owner = None
            changed = True
        return changed

    # Get players with ships orbiting (not at peace)
    orbiting_players = {f.owner for f in world.fleets if f.ships > 0 and f.owner is not None}

    # Check if owner has defensive ships (iships/pships)
    owner_has_defense = world.owner and (world.iships > 0 or world.pships > 0)

    if owner_has_defense:
        # Owner has defensive ships - they keep the world regardless of fleets
        # Defenses guarantee ownership
        return changed

    # If owner has no defense, check fleet presence
    if world.owner:
        owner_has_fleets = world.owner in orbiting_players

        if not owner_has_fleets:
            # Owner has no fleets and no defenses - lose the world
            logger.info(f"World {world.id}: {world.owner.name} lost presence (no fleets, no defense)")
            await sender.send_event(
                world.owner,
                f"Lost World {world.id} - no fleets in orbit and no defenses remaining.",
                "combat"
            )
            world.owner.worlds.remove(world)
            world.owner = None
            changed = True
            # Fall through to check if someone else captures it

    # Now determine if someone captures the world
    if len(orbiting_players) > 1:
        # Multiple players contesting - cannot capture
        # World stays neutral or owner keeps it if they have fleets
        pass

    elif len(orbiting_players) == 1:
        # Single player has uncontested presence
        sole_player = list(orbiting_players)[0]

        # Check if there are enemy defensive ships blocking capture
        has_enemy_defense = world.owner and world.owner != sole_player and (world.iships > 0 or world.pships > 0)

        if has_enemy_defense:
            # Enemy defenses block capture - cannot capture until destroyed
            pass
        elif world.owner != sole_player:
            # Not owned by this player (neutral or different owner with no defense)
            # CAPTURE IMMEDIATELY
            logger.info(f"World {world.id}: {sole_player.name} captures immediately")

            if world.owner:
                # Taking from another player (who had no defense)
                await sender.send_event(
                    world.owner,
                    f"Lost World {world.id} - captured by {sole_player.name}.",
                    "combat"
                )
                world.owner.worlds.remove(world)

            world.owner = sole_player
            sole_player.worlds.append(world)
            changed = True

            await sender.send_event(
                sole_player,
                f"**Captured World {world.id}!** Now under your control.",
                "capture"
            )

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
