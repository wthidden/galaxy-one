"""
Population mechanics for StarWeb.
Handles robot attacks, convert mechanics, and population interactions.
"""
import math
import random
import logging
from ..state import get_game_state
from ...events.event_bus import get_event_bus
from ...message_sender import get_message_sender

logger = logging.getLogger(__name__)


async def execute_robot_attack(order: dict):
    """
    Execute a robot attack order (F#R#).
    Berserker converts ships to robots (1 ship = 2 robots) and drops them on world.

    Args:
        order: Robot attack order dict with keys: player, fleet_id, num_ships
    """
    game_state = get_game_state()
    sender = get_message_sender()

    player = order["player"]
    fleet_id = order["fleet_id"]
    num_ships = order["num_ships"]

    # Verify player is Berserker
    if player.character_type != "Berserker":
        return

    fleet = game_state.get_fleet(fleet_id)
    if not fleet or fleet.owner != player:
        return

    # Must leave at least 1 ship on key
    max_ships = fleet.ships - 1
    if num_ships > max_ships:
        num_ships = max_ships

    if num_ships < 1:
        return

    world = fleet.world
    num_robots = num_ships * 2

    # Remove ships from fleet
    fleet.ships -= num_ships

    # Check if world has normal population
    if world.population_type == "normal" and world.population > 0:
        # Robot vs people combat
        await resolve_robot_vs_people(world, num_robots, player)
    elif world.population_type == "robot":
        # Adding robots to robot world
        if world.owner == player:
            # Adding to own robots
            world.population += num_robots
            await sender.send_event(
                player,
                f"Robot attack: Added {num_robots} robots to World {world.id}. Total: {world.population}",
                "robot_attack"
            )
        else:
            # Compete for control of robots
            await resolve_robot_vs_robot(world, num_robots, player)
    else:
        # Empty world or already destroyed - just add robots
        world.population = num_robots
        world.population_type = "robot"
        world.owner = player
        await sender.send_event(
            player,
            f"Robot attack: Deployed {num_robots} robots to World {world.id}",
            "robot_attack"
        )

    logger.info(f"Berserker {player.name} robot attack: F{fleet_id} dropped {num_robots} robots at W{world.id}")


async def resolve_robot_vs_people(world, num_robots, attacker):
    """
    Resolve combat when robots land on world with people.
    1 robot kills 4 people; 4 people kill 1 robot (fractions rounded up).

    Args:
        world: World where combat occurs
        num_robots: Number of robots attacking
        attacker: Berserker player launching attack
    """
    game_state = get_game_state()
    sender = get_message_sender()

    initial_population = world.population
    initial_robots = num_robots

    # Calculate casualties
    # 1 robot kills 4 people
    people_killed = min(num_robots * 4, world.population)

    # 4 people kill 1 robot (fractions rounded up)
    # If 1-4 people, kill 1 robot. If 5-8 people, kill 2 robots, etc.
    robots_killed = math.ceil(world.population / 4.0)
    robots_killed = min(robots_killed, num_robots)

    # Apply casualties
    world.population -= people_killed
    surviving_robots = num_robots - robots_killed

    # Award points to Berserker for killing population
    attacker.score += people_killed * 2

    # Notify Berserker
    await sender.send_event(
        attacker,
        f"Robot attack at World {world.id}: {people_killed} people killed, {robots_killed} robots destroyed. "
        f"{surviving_robots} robots survive. (+{people_killed * 2} points)",
        "robot_attack"
    )

    # Notify world owner if different
    if world.owner and world.owner != attacker:
        await sender.send_event(
            world.owner,
            f"Robot attack at World {world.id}! Lost {people_killed} population. {surviving_robots} enemy robots remain.",
            "robot_attack"
        )
        # Owner loses 1 point per population killed (non-Berserker penalty)
        world.owner.score -= people_killed

    # Determine final state
    if world.population == 0 and surviving_robots >= 1:
        # Berserker captures world
        old_owner = world.owner
        world.owner = attacker
        world.population = surviving_robots
        world.population_type = "robot"
        world.converts = 0  # Converts destroyed
        world.convert_owner = None

        await sender.send_event(
            attacker,
            f"World {world.id} captured! Now controlled with {surviving_robots} robots.",
            "world_captured"
        )

        if old_owner:
            await sender.send_event(
                old_owner,
                f"World {world.id} lost to Berserker robot attack!",
                "world_lost"
            )
    elif world.population == 0:
        # All people killed, but no robots survive - world goes neutral
        world.owner = None
        world.population_type = "normal"
        world.converts = 0
        world.convert_owner = None
    elif surviving_robots == 0:
        # All robots destroyed, people survive
        pass  # World stays as is with reduced population

    logger.info(f"Robot vs people at W{world.id}: {people_killed} people killed, {robots_killed} robots killed, "
               f"{world.population} people remain, {surviving_robots} robots remain")


async def resolve_robot_vs_robot(world, num_robots, attacker):
    """
    Resolve when robots are dropped on world already populated by robots.
    One player randomly chosen to own ALL robots based on proportional odds.

    Args:
        world: World with existing robots
        num_robots: Number of new robots being added
        attacker: Player adding new robots
    """
    sender = get_message_sender()

    existing_robots = world.population
    total_robots = existing_robots + num_robots

    # Calculate odds
    attacker_odds = num_robots / total_robots

    # Random selection
    if random.random() < attacker_odds:
        # Attacker wins all robots
        old_owner = world.owner
        world.owner = attacker
        world.population = total_robots

        await sender.send_event(
            attacker,
            f"Robot clash at World {world.id}: Your {num_robots} robots absorbed {existing_robots} existing robots. "
            f"Total: {total_robots} robots under your control.",
            "robot_clash"
        )

        if old_owner and old_owner != attacker:
            await sender.send_event(
                old_owner,
                f"Robot clash at World {world.id}: Lost control of {existing_robots} robots to attacking Berserker!",
                "robot_clash"
            )
    else:
        # Existing owner keeps all robots
        world.population = total_robots

        await sender.send_event(
            attacker,
            f"Robot clash at World {world.id}: Your {num_robots} robots were absorbed by {existing_robots} existing robots. "
            f"Total: {total_robots} robots controlled by {world.owner.name if world.owner else 'neutral'}.",
            "robot_clash"
        )

        if world.owner:
            await sender.send_event(
                world.owner,
                f"Robot clash at World {world.id}: {num_robots} attacking robots absorbed into your force. "
                f"Total: {total_robots} robots.",
                "robot_clash"
            )

    logger.info(f"Robot vs robot at W{world.id}: {num_robots} new robots, {existing_robots} existing, "
               f"winner: {world.owner.name if world.owner else 'neutral'}")


async def process_conversions(world):
    """
    Process Apostle conversion attempts at a world.

    - Each convert has 10% chance to convert 1 normal population
    - Each Apostle ship "not at peace" has 10% chance to convert 1 normal population
    - Only one Apostle can have converts on a world at a time

    Args:
        world: World to process conversions
    """
    game_state = get_game_state()
    sender = get_message_sender()

    # Can only convert normal population
    if world.population_type != "normal" or world.population == 0:
        return

    conversions = 0
    apostle = None

    # Existing converts attempt conversion
    if world.converts > 0 and world.convert_owner:
        apostle = world.convert_owner
        for _ in range(world.converts):
            if random.random() < 0.10:  # 10% chance per convert
                if world.population > 0:
                    conversions += 1

    # Apostle ships attempt conversion
    apostle_fleets = [f for f in world.fleets
                     if f.owner and f.owner.character_type == "Apostle"
                     and not f.at_peace and f.ships > 0]

    for fleet in apostle_fleets:
        fleet_conversions = 0
        for _ in range(fleet.ships):
            if random.random() < 0.10:  # 10% chance per ship
                if world.population > 0:
                    fleet_conversions += 1

        if fleet_conversions > 0:
            # Check if another Apostle already has converts here
            if world.convert_owner and world.convert_owner != fleet.owner:
                # Compete for converts - proportional odds
                total_influence = world.converts + fleet_conversions
                fleet_odds = fleet_conversions / total_influence

                if random.random() < fleet_odds:
                    # Fleet owner wins - takes all converts
                    old_apostle = world.convert_owner
                    world.convert_owner = fleet.owner
                    apostle = fleet.owner
                    conversions += fleet_conversions

                    await sender.send_event(
                        old_apostle,
                        f"Lost converts at World {world.id} to rival Apostle {fleet.owner.name}!",
                        "convert_lost"
                    )
                else:
                    # Existing convert owner keeps control
                    # Fleet conversions are lost
                    pass
            else:
                # No conflict - add conversions
                if not world.convert_owner:
                    world.convert_owner = fleet.owner
                apostle = fleet.owner
                conversions += fleet_conversions

    # Apply conversions
    if conversions > 0:
        actual_conversions = min(conversions, world.population)
        world.population -= actual_conversions
        world.converts += actual_conversions

        if apostle:
            await sender.send_event(
                apostle,
                f"Converted {actual_conversions} population at World {world.id}. Total converts: {world.converts}",
                "conversion"
            )

            # Check if entire population converted - Apostle captures world
            if world.population == 0 and world.converts > 0:
                old_owner = world.owner
                world.owner = apostle

                await sender.send_event(
                    apostle,
                    f"World {world.id} captured through complete conversion! All {world.converts} population are converts.",
                    "world_captured"
                )

                if old_owner and old_owner != apostle:
                    await sender.send_event(
                        old_owner,
                        f"World {world.id} lost to Apostle conversion!",
                        "world_lost"
                    )

        logger.info(f"Conversions at W{world.id}: {actual_conversions} people converted by {apostle.name if apostle else 'unknown'}")


async def process_deconversions(world, num_cgs):
    """
    Process consumer goods deconversion.
    Each CG has 50% chance to convert 1 convert back to normal.

    Args:
        world: World where CGs are unloaded
        num_cgs: Number of consumer goods unloaded
    """
    sender = get_message_sender()

    if world.converts == 0:
        return

    deconversions = 0
    for _ in range(num_cgs):
        if random.random() < 0.50:  # 50% chance per CG
            if world.converts > 0:
                deconversions += 1

    if deconversions > 0:
        actual_deconversions = min(deconversions, world.converts)
        world.converts -= actual_deconversions
        world.population += actual_deconversions

        if world.convert_owner:
            await sender.send_event(
                world.convert_owner,
                f"{actual_deconversions} converts de-converted at World {world.id} by consumer goods. "
                f"Remaining converts: {world.converts}",
                "deconversion"
            )

        # If no converts remain, clear convert owner
        if world.converts == 0:
            world.convert_owner = None

        logger.info(f"Deconversions at W{world.id}: {actual_deconversions} converts returned to normal")
