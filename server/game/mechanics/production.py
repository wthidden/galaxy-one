"""
Production mechanics for StarWeb.
Handles economic production and building.
"""
import math
import logging
from ..state import get_game_state
from ...events.event_bus import get_event_bus
from ...events.event_types import ProductionEvent, BuildEvent
import time

logger = logging.getLogger(__name__)


async def process_world_production(world):
    """
    Process production for a single world.
    Production is limited by population NOT used in building during this turn.

    Args:
        world: World to process
    """
    if not world.owner:
        return

    game_state = get_game_state()
    event_bus = get_event_bus()

    # Population available for mining = total population - population allocated to building
    population_used_building = getattr(world, 'population_used_building', 0)
    available_population = world.population - population_used_building

    # Calculate mineral production
    production = min(world.mines, max(0, available_population))
    old_metal = world.metal
    world.metal += production

    # Reset building tracker for next turn
    world.population_used_building = 0

    # Calculate population growth
    old_population = world.population
    if world.population < world.limit:
        growth = math.ceil(world.population * 0.10)
        world.population = min(world.population + growth, world.limit)

    population_growth = world.population - old_population

    # Publish production event
    if production > 0 or population_growth > 0:
        event = ProductionEvent(
            world_id=world.id,
            owner_id=world.owner.id,
            metal_produced=production,
            population_growth=population_growth,
            game_turn=game_state.game_turn,
            timestamp=time.time()
        )
        await event_bus.publish(event)


async def execute_build_order(order: dict):
    """
    Execute a BUILD order.
    Industry and population are used but not consumed (they're rate limiters).
    Metal is consumed (raw materials).

    Args:
        order: Build order dict
    """
    game_state = get_game_state()
    event_bus = get_event_bus()

    player = order["player"]
    world_id = order["world_id"]
    amount = order["amount"]
    target_type = order["target_type"]
    target_id = order.get("target_id")

    world = game_state.get_world(world_id)
    if not world or world.owner != player:
        return

    # Calculate actual build amount
    max_build = min(world.industry, world.metal, world.population)
    actual_amount = min(amount, max_build)

    if actual_amount <= 0:
        return

    # Deduct metal
    world.metal -= actual_amount

    # Track population allocated to building (for production calculation later)
    if not hasattr(world, 'population_used_building'):
        world.population_used_building = 0
    world.population_used_building += actual_amount

    # Build ships
    if target_type == "I":
        world.iships += actual_amount
    elif target_type == "P":
        world.pships += actual_amount
    elif target_type == "F" and target_id:
        fleet = game_state.get_fleet(target_id)
        if fleet and fleet.world == world and fleet.owner == player:
            fleet.ships += actual_amount
        else:
            # Invalid target, refund metal and population allocation
            world.metal += actual_amount
            world.population_used_building -= actual_amount
            return

    # Publish build event
    event = BuildEvent(
        world_id=world_id,
        owner_id=player.id,
        target_type=target_type,
        target_id=target_id,
        amount=actual_amount,
        game_turn=game_state.game_turn,
        timestamp=time.time()
    )
    await event_bus.publish(event)


async def execute_transfer_order(order: dict):
    """
    Execute a TRANSFER order.
    When transferring ships between fleets, cargo is transferred proportionally.
    Character class differences may cause cargo to be jettisoned.

    Args:
        order: Transfer order dict
    """
    game_state = get_game_state()
    event_bus = get_event_bus()

    player = order["player"]
    fleet_id = order["fleet_id"]
    amount = order["amount"]
    target_type = order["target_type"]
    target_id = order.get("target_id")

    fleet = game_state.get_fleet(fleet_id)
    if not fleet or fleet.owner != player or fleet.ships < amount:
        return

    world = fleet.world

    # Can't transfer to garrison of world you don't own
    if target_type in ["I", "P"] and world.owner != player:
        return

    # Execute transfer
    fleet.ships -= amount

    if target_type == "I":
        world.iships += amount
    elif target_type == "P":
        world.pships += amount
    elif target_type == "F" and target_id:
        target_fleet = game_state.get_fleet(target_id)
        if not target_fleet or target_fleet.world.id != world.id:
            # Invalid target, refund ships
            fleet.ships += amount
            return

        # Transfer ships
        target_fleet.ships += amount

        # Transfer proportional cargo with the ships
        if fleet.cargo > 0:
            # Calculate cargo per ship in source fleet (before transfer)
            total_ships_before = fleet.ships + amount  # Add back the ships we just removed
            cargo_per_ship = fleet.cargo / total_ships_before
            cargo_to_transfer = int(amount * cargo_per_ship)

            if cargo_to_transfer > fleet.cargo:
                cargo_to_transfer = fleet.cargo

            # Remove cargo from source
            fleet.cargo -= cargo_to_transfer

            # Check target capacity based on character class
            target_owner = target_fleet.owner
            target_cargo_multiplier = 2 if target_owner.character_type == "Merchant" else 1
            target_max_capacity = target_fleet.ships * target_cargo_multiplier
            target_available_capacity = target_max_capacity - target_fleet.cargo

            # Transfer what fits, jettison the rest
            if cargo_to_transfer <= target_available_capacity:
                # All cargo fits
                target_fleet.cargo += cargo_to_transfer
            else:
                # Some cargo must be jettisoned
                cargo_transferred = target_available_capacity
                cargo_jettisoned = cargo_to_transfer - cargo_transferred
                target_fleet.cargo += cargo_transferred

                # Log the jettison
                logger.info(
                    f"Jettisoned {cargo_jettisoned} cargo in fleet transfer "
                    f"from F{fleet_id} to F{target_id} (capacity mismatch)"
                )

                # Notify player
                from ...message_sender import get_message_sender
                sender = get_message_sender()
                await sender.send_event(
                    player,
                    f"Transfer F{fleet_id}→F{target_id}: {cargo_jettisoned} cargo jettisoned due to capacity limits",
                    "info"
                )


async def execute_load_order(order: dict):
    """
    Execute a LOAD order.
    Load population from world onto fleet as cargo.

    Args:
        order: Load order dict
    """
    game_state = get_game_state()

    player = order["player"]
    fleet_id = order["fleet_id"]
    amount = order.get("amount")  # None means load max

    fleet = game_state.get_fleet(fleet_id)
    if not fleet or fleet.owner != player:
        return

    world = fleet.world
    if world.owner != player:
        return

    # Calculate cargo capacity
    cargo_multiplier = 2 if player.character_type == "Merchant" else 1
    max_capacity = fleet.ships * cargo_multiplier
    available_capacity = max_capacity - fleet.cargo

    # Determine amount to load
    if amount is None:
        # Load max
        amount = min(available_capacity, world.population)
    else:
        # Load specified amount, limited by capacity and available population
        amount = min(amount, available_capacity, world.population)

    if amount <= 0:
        return

    # Execute load
    world.population -= amount
    fleet.cargo += amount


async def execute_unload_order(order: dict):
    """
    Execute an UNLOAD order.
    Unload cargo from fleet to world population.

    Args:
        order: Unload order dict
    """
    game_state = get_game_state()

    player = order["player"]
    fleet_id = order["fleet_id"]
    amount = order.get("amount")  # None means unload all

    fleet = game_state.get_fleet(fleet_id)
    if not fleet or fleet.owner != player:
        return

    world = fleet.world
    if world.owner != player:
        return

    # Determine amount to unload
    if amount is None:
        # Unload all
        amount = fleet.cargo
    else:
        # Unload specified amount, limited by cargo available
        amount = min(amount, fleet.cargo)

    if amount <= 0:
        return

    # Check population limit
    if world.population + amount > world.limit:
        max_unload = world.limit - world.population
        if max_unload <= 0:
            return
        amount = max_unload

    # Execute unload
    fleet.cargo -= amount
    world.population += amount


async def execute_transfer_artifact_order(order: dict):
    """
    Execute a TRANSFER_ARTIFACT order.
    Transfer artifact between fleet and world or between fleets.

    Args:
        order: Transfer artifact order dict
    """
    game_state = get_game_state()

    player = order["player"]
    source_type = order["source_type"]
    source_id = order["source_id"]
    artifact_id = order["artifact_id"]
    target_type = order["target_type"]
    target_id = order.get("target_id")

    # Get source
    if source_type == "F":
        source = game_state.get_fleet(source_id)
    elif source_type == "W":
        source = game_state.get_world(source_id)
    else:
        return

    if not source or source.owner != player:
        return

    # Find artifact in source
    artifact = None
    for a in source.artifacts:
        if a.id == artifact_id:
            artifact = a
            break

    if not artifact:
        return

    # Get target
    if target_type == "F":
        target = game_state.get_fleet(target_id)
        if not target or target.owner != player:
            return
        # Verify same location
        source_world = source.world if source_type == "F" else source
        if target.world.id != source_world.id:
            return
    elif target_type == "W":
        # Transfer to world at source location
        source_world = source.world if source_type == "F" else source
        target = source_world
        if target.owner != player:
            return
    else:
        return

    # Execute transfer
    source.artifacts.remove(artifact)
    target.artifacts.append(artifact)


def calculate_player_score(player):
    """
    Calculate player's score based on their assets.
    Score = worlds + industry + ships + artifacts + population

    Args:
        player: Player to calculate score for

    Returns:
        int: Calculated score
    """
    score = 0

    # Worlds: 10 points each
    score += len(player.worlds) * 10

    # Industry, ships, population from owned worlds
    for world in player.worlds:
        score += world.industry * 2  # 2 points per industry
        score += world.iships  # 1 point per IShip
        score += world.pships  # 1 point per PShip
        score += world.population  # 1 point per population

    # Ships in fleets
    for fleet in player.fleets:
        score += fleet.ships  # 1 point per ship
        score += fleet.cargo  # 1 point per cargo (population in transit)

    # Artifacts
    artifact_count = 0
    special_artifact_count = 0
    for world in player.worlds:
        for artifact in world.artifacts:
            if hasattr(artifact, 'type') and artifact.type == "special":
                special_artifact_count += 1
            else:
                artifact_count += 1
    for fleet in player.fleets:
        for artifact in fleet.artifacts:
            if hasattr(artifact, 'type') and artifact.type == "special":
                special_artifact_count += 1
            else:
                artifact_count += 1

    score += artifact_count * 10  # 10 points per regular artifact
    score += special_artifact_count * 50  # 50 points per special artifact

    player.score = score
    return score
