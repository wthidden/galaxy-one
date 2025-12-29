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
    from ...message_sender import get_message_sender
    game_state = get_game_state()
    event_bus = get_event_bus()
    sender = get_message_sender()

    player = order["player"]
    world_id = order["world_id"]
    amount = order["amount"]
    target_type = order["target_type"]
    target_id = order.get("target_id")

    world = game_state.get_world(world_id)
    if not world:
        return

    # Can build if: (1) you own the world, OR (2) you have a fleet there
    can_build = world.owner == player or any(f.owner == player for f in world.fleets)
    if not can_build:
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
    claimed_world = False
    if target_type == "I":
        world.iships += actual_amount
        # Building iships on neutral world establishes ownership
        if not world.owner:
            world.owner = player
            player.worlds.append(world)
            claimed_world = True
            logger.info(f"World {world_id}: {player.name} claimed via building iships")
    elif target_type == "P":
        world.pships += actual_amount
        # Building pships on neutral world establishes ownership
        if not world.owner:
            world.owner = player
            player.worlds.append(world)
            claimed_world = True
            logger.info(f"World {world_id}: {player.name} claimed via building pships")
    elif target_type == "F" and target_id:
        fleet = game_state.get_fleet(target_id)
        if fleet and fleet.world == world and fleet.owner == player:
            fleet.ships += actual_amount
        else:
            # Invalid target, refund metal and population allocation
            world.metal += actual_amount
            world.population_used_building -= actual_amount
            return

    # Notify player if they claimed the world
    if claimed_world:
        await sender.send_event(
            player,
            f"**Claimed World {world_id}!** Built defenses on neutral world.",
            "capture"
        )

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
    # Check if player has access to world (owns it OR has fleet there)
    has_access = world.owner == player or any(f.owner == player for f in world.fleets)
    if not has_access:
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
    # Check if player has access to world (owns it OR has fleet there)
    has_access = world.owner == player or any(f.owner == player for f in world.fleets)
    if not has_access:
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


async def execute_transfer_from_defense_order(order: dict):
    """
    Execute a TRANSFER_FROM_DEFENSE order (I#T#F#, P#T#F#, I#T#P, P#T#I).
    Transfer ships from ISHIPS/PSHIPS to fleets or between defenses.

    Args:
        order: Transfer from defense order dict
    """
    game_state = get_game_state()

    player = order["player"]
    world_id = order["world_id"]
    amount = order["amount"]
    source_type = order["source_type"]  # "I" or "P"
    target_type = order["target_type"]  # "I", "P", or "F"
    target_id = order.get("target_id")

    world = game_state.get_world(world_id)
    if not world or world.owner != player:
        return

    # Check source has enough ships
    if source_type == "I":
        if world.iships < amount:
            return
        world.iships -= amount
    elif source_type == "P":
        if world.pships < amount:
            return
        world.pships -= amount
    else:
        return

    # Execute transfer to target
    if target_type == "I":
        world.iships += amount
    elif target_type == "P":
        world.pships += amount
    elif target_type == "F" and target_id:
        target_fleet = game_state.get_fleet(target_id)
        if not target_fleet or target_fleet.world.id != world_id:
            # Invalid target, refund ships to source
            if source_type == "I":
                world.iships += amount
            else:
                world.pships += amount
            return

        # Transfer ships to fleet
        target_fleet.ships += amount

    logger.info(f"Transferred {amount} ships from {source_type}SHIPS@W{world_id} to {target_type}{target_id if target_id else ''}")


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
        if not source or source.owner != player:
            return
    elif source_type == "W":
        source = game_state.get_world(source_id)
        if not source:
            return
        # Check if player has access to world (owns it OR has fleet there)
        has_access = source.owner == player or any(f.owner == player for f in source.fleets)
        if not has_access:
            return
    else:
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
        # Check if player has access to target world (owns it OR has fleet there)
        has_access = target.owner == player or any(f.owner == player for f in target.fleets)
        if not has_access:
            return
    else:
        return

    # Execute transfer
    source.artifacts.remove(artifact)
    target.artifacts.append(artifact)


def calculate_player_score(player):
    """
    Calculate player's score based on their assets and character type.
    Each character type has different scoring rules.

    Args:
        player: Player to calculate score for

    Returns:
        int: Calculated score
    """
    score = 0
    char_type = player.character_type

    # Character-specific scoring
    if char_type == "EmpireBuilder":
        score = _score_empire_builder(player)
    elif char_type == "Merchant":
        score = _score_merchant(player)
    elif char_type == "Pirate":
        score = _score_pirate(player)
    elif char_type == "ArtifactCollector":
        score = _score_artifact_collector(player)
    elif char_type == "Berserker":
        score = _score_berserker(player)
    elif char_type == "Apostle":
        score = _score_apostle(player)
    else:
        # Fallback to generic scoring
        logger.warning(f"Unknown character type: {char_type}, using generic scoring")
        score = _score_generic(player)

    player.score = score
    return score


def _score_empire_builder(player):
    """Empire Builder scoring: population/10, industry, mines, artifacts"""
    score = 0

    for world in player.worlds:
        score += world.population // 10  # 1 point per 10 population
        score += world.industry  # 1 point per industry
        score += world.mines  # 1 point per mine

    # Artifacts use standard scoring
    score += _score_artifacts_standard(player, "Platinum", "Crown")

    return score


def _score_merchant(player):
    """
    Merchant scoring: metal unload points (transactional), CG points (transactional), artifacts.
    Note: Transactional points (metal/CG unloads) are awarded when actions occur, not here.
    """
    score = 0

    # Merchants only get points from transactions (handled elsewhere)
    # and artifacts
    score += _score_artifacts_standard(player, "Gold", "Shekel")

    return score


def _score_pirate(player):
    """Pirate scoring: 3 points per key, plunder points (transactional), artifacts"""
    score = 0

    # 3 points per key owned
    score += len(player.fleets) * 3

    # Plundering points are transactional (handled elsewhere)

    # Artifacts use standard scoring
    score += _score_artifacts_standard(player, "Silver", "Lodestar")

    return score


def _score_artifact_collector(player):
    """Artifact Collector scoring: artifacts only (special rules)"""
    score = 0

    # Collect all artifacts
    artifacts = []
    for world in player.worlds:
        artifacts.extend(world.artifacts)
    for fleet in player.fleets:
        artifacts.extend(fleet.artifacts)

    for artifact in artifacts:
        name = artifact.name.upper()

        # Special artifacts
        if name == "TREASURE OF POLARIS":
            score += 30
        elif name == "SLIPPERS OF VENUS":
            score += 30
        elif name == "RADIOACTIVE ISOTOPE":
            score += 30
        elif name == "LESSER OF TWO EVILS":
            score += 30
        elif name == "BLACK BOX":
            score += 30
        elif "NEBULA SCROLLS" in name:
            score += 30
        # Standard artifacts
        elif "ANCIENT" in name and "PYRAMID" in name:
            score += 90  # Ancient Pyramid - greatest treasure
        elif "ANCIENT" in name or "PYRAMID" in name:
            # Don't count Plastic Pyramid
            if "PLASTIC" not in name:
                score += 30
        elif "PLASTIC" in name:
            score += 0  # No penalty for Artifact Collectors
        else:
            # Other standard non-plastic artifacts
            score += 15

    return score


def _score_berserker(player):
    """
    Berserker scoring: 5 points/turn per robot world, kill points (transactional), artifacts.
    Note: Kill points are awarded when kills occur, not here.
    """
    score = 0

    # 5 points per turn for each robot world
    for world in player.worlds:
        if world.population_type == "robot":
            score += 5

    # Kill points are transactional (handled elsewhere)

    # Artifacts use standard scoring
    score += _score_artifacts_standard(player, "Titanium", "Sword")

    return score


def _score_apostle(player):
    """Apostle scoring: 5 per world, +5 for fully converted worlds, 1 per 10 converts, artifacts"""
    score = 0

    # Count converts
    total_converts = 0

    for world in player.worlds:
        # 5 points per world controlled
        score += 5

        # Check if entirely populated by converts
        if world.population_type == "apostle" and world.population > 0:
            # Additional 5 points for fully converted world
            score += 5
            total_converts += world.population
        elif world.population_type == "apostle":
            total_converts += world.population

    # 1 point per 10 converts
    score += total_converts // 10

    # Martyr points are transactional (handled elsewhere)
    # Shot penalty is transactional (handled elsewhere)

    # Artifacts use standard scoring
    score += _score_artifacts_standard(player, "Blessed", "Sepulchre")

    return score


def _score_artifacts_standard(player, category1, category2):
    """
    Standard artifact scoring for non-Artifact Collectors.

    Args:
        player: Player to score
        category1: First artifact category (e.g., "Platinum")
        category2: Second artifact category (e.g., "Crown")

    Returns:
        int: Artifact score
    """
    score = 0
    category1 = category1.upper()
    category2 = category2.upper()
    greatest_treasure = f"{category1} {category2}"

    # Collect all artifacts
    artifacts = []
    for world in player.worlds:
        artifacts.extend(world.artifacts)
    for fleet in player.fleets:
        artifacts.extend(fleet.artifacts)

    for artifact in artifacts:
        name = artifact.name.upper()

        # Special artifacts
        if name == "TREASURE OF POLARIS":
            score += 20
        elif name == "SLIPPERS OF VENUS":
            score += 10
        elif name == "RADIOACTIVE ISOTOPE":
            score -= 30
        elif name == "LESSER OF TWO EVILS":
            score -= 15
        elif name == "BLACK BOX":
            score += 0
        elif "NEBULA SCROLLS" in name:
            score += 0  # End-game bonus only (not implemented yet)
        # Greatest Treasure
        elif name == greatest_treasure:
            score += 15
        # Standard artifacts from your categories
        elif category1 in name or category2 in name:
            # Don't count Plastic items as part of category
            if "PLASTIC" not in name:
                score += 5
        # Plastic penalty
        elif "PLASTIC" in name:
            score -= 10
        # Other standard artifacts
        else:
            score += 0

    return score


def _score_generic(player):
    """Generic fallback scoring (old system)"""
    score = 0

    # Worlds: 10 points each
    score += len(player.worlds) * 10

    # Industry, ships, population from owned worlds
    for world in player.worlds:
        score += world.industry * 2
        score += world.iships
        score += world.pships
        score += world.population

    # Ships in fleets
    for fleet in player.fleets:
        score += fleet.ships
        score += fleet.cargo

    return score


async def execute_scrap_ships_order(order: dict):
    """
    Execute a SCRAP_SHIPS order (W#S#).
    Convert ISHIPS to industry.

    Args:
        order: Scrap ships order dict
    """
    game_state = get_game_state()
    sender = get_message_sender()

    player = order["player"]
    world_id = order["world_id"]
    amount = order["amount"]

    world = game_state.get_world(world_id)
    if not world or world.owner != player:
        return

    # Calculate ships needed
    is_empire_builder = player.character_type == "Empire Builder"
    ships_per_industry = 4 if is_empire_builder else 6
    ships_needed = amount * ships_per_industry

    if world.iships < ships_needed:
        return

    # Scrap ships and create industry
    world.iships -= ships_needed
    world.industry += amount

    await sender.send_event(
        player,
        f"W{world_id}: Scrapped {ships_needed} ISHIPS to create {amount} industry",
        "production"
    )
    logger.info(f"W{world_id}: Scrapped {ships_needed} ISHIPS -> {amount} industry")


async def execute_jettison_order(order: dict):
    """
    Execute a JETTISON order (F#J or F#J#).
    Destroy cargo from fleet.

    Args:
        order: Jettison order dict
    """
    game_state = get_game_state()
    sender = get_message_sender()

    player = order["player"]
    fleet_id = order["fleet_id"]
    amount = order.get("amount")

    fleet = game_state.get_fleet(fleet_id)
    if not fleet or fleet.owner != player or fleet.cargo == 0:
        return

    # Jettison specified amount or all
    if amount is None or amount > fleet.cargo:
        amount = fleet.cargo

    fleet.cargo -= amount

    await sender.send_event(
        player,
        f"F{fleet_id}: Jettisoned {amount} cargo",
        "logistics"
    )
    logger.info(f"F{fleet_id}: Jettisoned {amount} cargo")


async def execute_consumer_goods_order(order: dict):
    """
    Execute an UNLOAD_CONSUMER_GOODS order (F#N or F#N#).
    Merchant-only: Unload cargo as consumer goods for points.

    Args:
        order: Consumer goods order dict
    """
    game_state = get_game_state()
    sender = get_message_sender()

    player = order["player"]
    fleet_id = order["fleet_id"]
    amount = order.get("amount")

    # Only Merchants can deliver consumer goods
    if player.character_type != "Merchant":
        return

    fleet = game_state.get_fleet(fleet_id)
    if not fleet or fleet.owner != player or fleet.cargo == 0:
        return

    world = fleet.world

    # Calculate amount to unload
    if amount is None or amount > fleet.cargo:
        amount = fleet.cargo

    # Merchant scoring for consumer goods:
    # 10 points first time, 8 second, 5 third, 3 fourth, 1 fifth+
    # Track deliveries per world
    if not hasattr(world, 'consumer_goods_deliveries'):
        world.consumer_goods_deliveries = {}

    delivery_count = world.consumer_goods_deliveries.get(player.id, 0)
    
    # Points based on delivery number
    points_schedule = [10, 8, 5, 3, 1]
    if delivery_count < len(points_schedule):
        points = points_schedule[delivery_count] * amount
    else:
        points = 1 * amount  # 1 point for 5th+ delivery

    # Award points
    player.score += points
    world.consumer_goods_deliveries[player.id] = delivery_count + 1

    # Unload cargo
    fleet.cargo -= amount

    await sender.send_event(
        player,
        f"F{fleet_id}: Delivered {amount} consumer goods to W{world.id} for {points} points!",
        "merchant"
    )
    logger.info(f"F{fleet_id}: Merchant delivered {amount} consumer goods for {points} points")


async def execute_view_artifact_order(order: dict):
    """Execute VIEW_ARTIFACT order (V#, V#F#, V#W). Display artifact information."""
    game_state = get_game_state()
    sender = get_message_sender()

    player = order["player"]
    artifact_id = order["artifact_id"]
    location_type = order.get("location_type")
    location_id = order.get("location_id")

    # Find the artifact
    artifact = None
    location_desc = ""

    if location_type == "F":
        fleet = game_state.get_fleet(location_id)
        if fleet and fleet.owner == player:
            for a in fleet.artifacts:
                if a.id == artifact_id:
                    artifact = a
                    location_desc = f"Fleet {location_id}"
                    break

    elif location_type == "W":
        # Find first player fleet's world
        for fleet in game_state.fleets.values():
            if fleet.owner == player and fleet.ships > 0:
                world = fleet.world
                for a in world.artifacts:
                    if a.id == artifact_id:
                        artifact = a
                        location_desc = f"World {world.id}"
                        break
                break

    else:
        # V# - search all player's possessions
        for fleet in game_state.fleets.values():
            if fleet.owner == player:
                for a in fleet.artifacts:
                    if a.id == artifact_id:
                        artifact = a
                        location_desc = f"Fleet {fleet.id}"
                        break
                if artifact:
                    break

        if not artifact:
            for world in game_state.worlds.values():
                if world.owner == player:
                    for a in world.artifacts:
                        if a.id == artifact_id:
                            artifact = a
                            location_desc = f"World {world.id}"
                            break
                    if artifact:
                        break

    if artifact:
        artifact_info = f"Artifact {artifact.id}: '{artifact.name}' (located at {location_desc})"
        await sender.send_event(player, artifact_info, "info")
        logger.info(f"Player {player.name} viewed artifact {artifact_id}")
    else:
        await sender.send_event(player, f"Artifact {artifact_id} not found", "error")


async def execute_declare_relation_order(order: dict):
    """Execute DECLARE_RELATION order (F#Q#, F#X#). Set peace/war status."""
    game_state = get_game_state()
    sender = get_message_sender()

    player = order["player"]
    fleet_id = order["fleet_id"]
    target_fleet_id = order["target_fleet_id"]
    relation_type = order["relation_type"]

    fleet = game_state.get_fleet(fleet_id)
    target_fleet = game_state.get_fleet(target_fleet_id)

    if not fleet or fleet.owner != player or not target_fleet:
        return

    # Initialize player relations if not exists
    if not hasattr(player, 'relations'):
        player.relations = {}

    target_player = target_fleet.owner
    if not target_player:
        return

    # Set the relation
    if relation_type == "PEACE":
        player.relations[target_player.id] = "PEACE"
        await sender.send_event(
            player,
            f"F{fleet_id} declared PEACE with F{target_fleet_id} (owned by {target_player.name})",
            "diplomacy"
        )
        # Notify the target player
        await sender.send_event(
            target_player,
            f"{player.name}'s F{fleet_id} declared PEACE with your F{target_fleet_id}",
            "diplomacy"
        )
        logger.info(f"{player.name} declared peace with {target_player.name}")

    elif relation_type == "WAR":
        player.relations[target_player.id] = "WAR"
        await sender.send_event(
            player,
            f"F{fleet_id} declared WAR with F{target_fleet_id} (owned by {target_player.name})",
            "diplomacy"
        )
        # Notify the target player
        await sender.send_event(
            target_player,
            f"{player.name}'s F{fleet_id} declared WAR on your F{target_fleet_id}!",
            "diplomacy"
        )
        logger.info(f"{player.name} declared war on {target_player.name}")


async def execute_plunder_order(order: dict):
    """Execute PLUNDER order (W#X). Convert population to metal."""
    game_state = get_game_state()
    sender = get_message_sender()

    player = order["player"]
    world_id = order["world_id"]

    world = game_state.get_world(world_id)
    if not world or world.owner != player or world.population == 0:
        return

    # Convert all population to metal (1:1 ratio)
    metal_gained = world.population
    world.metal += metal_gained
    world.population = 0

    await sender.send_event(
        player,
        f"W{world_id}: Plundered {metal_gained} population, converted to {metal_gained} metal!",
        "plunder"
    )
    logger.info(f"W{world_id}: {player.name} plundered {metal_gained} population")
