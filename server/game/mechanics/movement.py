"""
Movement mechanics for StarWeb.
Handles fleet movement including ambush detection.
"""
import math
import logging
from ..state import get_game_state
from ...events.event_bus import get_event_bus
from ...events.event_types import FleetMovedEvent
from ...message_sender import get_message_sender
import time

logger = logging.getLogger(__name__)


async def execute_move_order(order: dict):
    """
    Execute a MOVE order.

    Args:
        order: Move order dict
    """
    game_state = get_game_state()
    event_bus = get_event_bus()
    sender = get_message_sender()

    player = order["player"]
    fleet_id = order["fleet_id"]
    path = order["path"]

    fleet = game_state.get_fleet(fleet_id)
    if not fleet or fleet.owner != player or fleet.ships == 0:
        return

    from_world = fleet.world
    current_world = fleet.world

    # Move through path
    for dest_id in path:
        dest_world = game_state.get_world(dest_id)
        if not dest_world:
            continue

        # Check for ambush
        ambushers = [
            f for f in dest_world.fleets
            if f.is_ambushing and f.owner != player and f.ships > 0
        ]

        if ambushers:
            await handle_ambush(fleet, dest_world, ambushers, player)
            return  # Fleet stops here

        current_world = dest_world

    # No ambush - complete move
    final_dest = game_state.get_world(path[-1])
    if fleet.world != final_dest:
        fleet.world.fleets.remove(fleet)
        fleet.world = final_dest
        final_dest.fleets.append(fleet)

    fleet.moved = True

    # Publish movement event (handler will send user message)
    event = FleetMovedEvent(
        fleet_id=fleet_id,
        owner_id=player.id,
        owner_name=player.name,
        from_world=from_world.id,
        to_world=path[-1],
        path=path,
        ships=fleet.ships,
        game_turn=game_state.game_turn,
        timestamp=time.time()
    )
    await event_bus.publish(event)


async def handle_ambush(fleet, dest_world, ambushers, player):
    """
    Handle fleet being ambushed.

    Args:
        fleet: Fleet being ambushed
        dest_world: World where ambush occurs
        ambushers: List of ambushing fleets
        player: Owner of ambushed fleet
    """
    sender = get_message_sender()

    # Move fleet to ambush location
    fleet.world.fleets.remove(fleet)
    fleet.world = dest_world
    dest_world.fleets.append(fleet)
    fleet.moved = True

    # Calculate ambush damage
    total_ambush_strength = sum(f.ships for f in ambushers) * 2
    damage_to_fleet = math.ceil(total_ambush_strength / 2)
    fleet.ships = max(0, fleet.ships - damage_to_fleet)

    # Notify victim
    await sender.send_event(
        player,
        f"Fleet {fleet.id} ambushed at World {dest_world.id}! Lost {damage_to_fleet} ships.",
        "ambush"
    )

    # Notify ambushers
    for ambusher in ambushers:
        if ambusher.owner:
            await sender.send_event(
                ambusher.owner,
                f"Your Fleet {ambusher.id} ambushed Fleet {fleet.id} at World {dest_world.id}.",
                "ambush"
            )


async def set_ambush(fleet_id: int, player):
    """
    Set a fleet to ambush mode.

    Args:
        fleet_id: Fleet to set ambushing
        player: Owner of fleet
    """
    game_state = get_game_state()

    fleet = game_state.get_fleet(fleet_id)
    if fleet and fleet.owner == player:
        fleet.is_ambushing = True


async def execute_probe_order(order: dict):
    """
    Execute a PROBE order (F#P#, I#P#, P#P#).
    Uses 1 ship to scout an adjacent world before movement.

    Args:
        order: Probe order dict
    """
    game_state = get_game_state()
    sender = get_message_sender()

    player = order["player"]
    source_type = order["source_type"]  # "F", "I", or "P"
    source_id = order["source_id"]
    target_world_id = order["target_world"]

    target_world = game_state.get_world(target_world_id)
    if not target_world:
        return

    # Execute probe based on source type
    if source_type == "F":
        # Fleet probe
        fleet = game_state.get_fleet(source_id)
        if not fleet or fleet.owner != player or fleet.ships < 1:
            return

        # Spend 1 ship for the probe
        fleet.ships -= 1

        # Send probe information
        probe_info = f"Probe of W{target_world_id}: "
        probe_info += f"Pop={target_world.population}, "
        probe_info += f"Ind={target_world.industry}, "
        probe_info += f"Metal={target_world.metal}, "
        probe_info += f"Mines={target_world.mines}, "
        probe_info += f"I{target_world.iships}/P{target_world.pships}"

        if target_world.owner:
            probe_info += f" (owned by {target_world.owner.name})"
        else:
            probe_info += " (neutral)"

        # Count fleets at world
        fleets_at_world = [f for f in game_state.fleets.values() if f.world.id == target_world_id and f.ships > 0]
        if fleets_at_world:
            probe_info += f", {len(fleets_at_world)} fleets present"

        # Count artifacts
        if target_world.artifacts:
            probe_info += f", {len(target_world.artifacts)} artifacts"

        await sender.send_event(player, probe_info, "probe")
        logger.info(f"F{source_id} probed W{target_world_id}")

    else:
        # Defense probe (I or P)
        world = game_state.get_world(source_id)
        if not world or world.owner != player:
            return

        # Spend 1 defense ship
        if source_type == "I":
            if world.iships < 1:
                return
            world.iships -= 1
        elif source_type == "P":
            if world.pships < 1:
                return
            world.pships -= 1

        # Send probe information (same as fleet probe)
        probe_info = f"Probe of W{target_world_id}: "
        probe_info += f"Pop={target_world.population}, "
        probe_info += f"Ind={target_world.industry}, "
        probe_info += f"Metal={target_world.metal}, "
        probe_info += f"Mines={target_world.mines}, "
        probe_info += f"I{target_world.iships}/P{target_world.pships}"

        if target_world.owner:
            probe_info += f" (owned by {target_world.owner.name})"
        else:
            probe_info += " (neutral)"

        fleets_at_world = [f for f in game_state.fleets.values() if f.world.id == target_world_id and f.ships > 0]
        if fleets_at_world:
            probe_info += f", {len(fleets_at_world)} fleets present"

        if target_world.artifacts:
            probe_info += f", {len(target_world.artifacts)} artifacts"

        await sender.send_event(player, probe_info, "probe")
        logger.info(f"{source_type}SHIPS@W{source_id} probed W{target_world_id}")
