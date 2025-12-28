"""
Combat mechanics for StarWeb.
Handles fleet vs fleet and fleet vs world combat.
"""
import math
import logging
from typing import Tuple
from ..state import get_game_state
from ...events.event_bus import get_event_bus
from ...events.event_types import CombatEvent
from ...message_sender import get_message_sender
import time

logger = logging.getLogger(__name__)


async def resolve_combat(attacker_ships: int, defender_ships: int) -> Tuple[int, int]:
    """
    Resolve combat between two forces.

    Args:
        attacker_ships: Number of attacking ships
        defender_ships: Number of defending ships

    Returns:
        (attacker_losses, defender_losses)
    """
    hits_on_defender = attacker_ships
    hits_on_attacker = defender_ships
    defender_losses = math.ceil(hits_on_defender / 2)
    attacker_losses = math.ceil(hits_on_attacker / 2)

    return attacker_losses, defender_losses


async def execute_fire_order(order: dict):
    """
    Execute a FIRE order.

    Args:
        order: Order dict containing fire parameters
    """
    game_state = get_game_state()
    event_bus = get_event_bus()
    sender = get_message_sender()

    player = order["player"]
    fleet_id = order["fleet_id"]
    target_type = order["target_type"]

    fleet = game_state.get_fleet(fleet_id)
    if not fleet or fleet.owner != player:
        return

    world = fleet.world

    if target_type == "WORLD":
        await fire_at_world(order, fleet, world)
    elif target_type == "FLEET":
        await fire_at_fleet(order, fleet, world)


async def fire_at_world(order: dict, attacker_fleet, world):
    """
    Fire at world garrison or installations.

    Args:
        order: Fire order
        attacker_fleet: Attacking fleet
        world: Target world
    """
    game_state = get_game_state()
    event_bus = get_event_bus()
    sender = get_message_sender()

    player = order["player"]
    sub_target = order["sub_target"]
    shots = attacker_fleet.ships

    if sub_target == "P":
        # Fire at population ships then population
        def_ships = world.pships
        world.pships = max(0, world.pships - math.ceil(shots / 2))
        rem_shots = shots - (def_ships * 2)

        if rem_shots > 0:
            pop_killed = math.ceil(rem_shots / 2)
            world.population = max(0, world.population - pop_killed)
            player.score -= pop_killed

            await sender.send_event(
                player,
                f"Fired on W{world.id} population, killing {pop_killed}.",
                "combat"
            )

        # Publish combat event
        event = CombatEvent(
            world_id=world.id,
            attacker_id=player.id,
            defender_id=world.owner.id if world.owner else None,
            attacker_losses=0,
            defender_losses=def_ships + (pop_killed if rem_shots > 0 else 0),
            combat_type="fleet_vs_world",
            game_turn=game_state.game_turn,
            timestamp=time.time()
        )
        await event_bus.publish(event)

    elif sub_target == "I":
        # Fire at industry ships then industry
        def_ships = world.iships
        world.iships = max(0, world.iships - math.ceil(shots / 2))
        rem_shots = shots - (def_ships * 2)

        if rem_shots > 0:
            ind_destroyed = math.ceil(rem_shots / 2)
            world.industry = max(0, world.industry - ind_destroyed)

            await sender.send_event(
                player,
                f"Fired on W{world.id} industry, destroying {ind_destroyed}.",
                "combat"
            )

        # Publish combat event
        event = CombatEvent(
            world_id=world.id,
            attacker_id=player.id,
            defender_id=world.owner.id if world.owner else None,
            attacker_losses=0,
            defender_losses=def_ships + (ind_destroyed if rem_shots > 0 else 0),
            combat_type="fleet_vs_world",
            game_turn=game_state.game_turn,
            timestamp=time.time()
        )
        await event_bus.publish(event)


async def fire_at_fleet(order: dict, attacker_fleet, world):
    """
    Fire at another fleet.

    Args:
        order: Fire order
        attacker_fleet: Attacking fleet
        world: World where combat occurs
    """
    game_state = get_game_state()
    event_bus = get_event_bus()
    sender = get_message_sender()

    player = order["player"]
    target_id = order["target_id"]

    defender_fleet = game_state.get_fleet(target_id)
    if not defender_fleet or defender_fleet.world != world:
        return

    # Resolve combat
    dmg_attacker, dmg_defender = await resolve_combat(
        attacker_fleet.ships,
        defender_fleet.ships
    )

    attacker_fleet.ships = max(0, attacker_fleet.ships - dmg_attacker)
    defender_fleet.ships = max(0, defender_fleet.ships - dmg_defender)

    # Notify both players
    msg = (
        f"Combat at W{world.id}! F{attacker_fleet.id} vs F{defender_fleet.id}. "
        f"Losses: Attacker {dmg_attacker}, Defender {dmg_defender}."
    )

    await sender.send_event(player, msg, "combat")

    if defender_fleet.owner:
        await sender.send_event(defender_fleet.owner, msg, "combat")

    # Publish combat event
    event = CombatEvent(
        world_id=world.id,
        attacker_id=player.id,
        defender_id=defender_fleet.owner.id if defender_fleet.owner else None,
        attacker_losses=dmg_attacker,
        defender_losses=dmg_defender,
        combat_type="fleet_vs_fleet",
        game_turn=game_state.game_turn,
        timestamp=time.time()
    )
    await event_bus.publish(event)
