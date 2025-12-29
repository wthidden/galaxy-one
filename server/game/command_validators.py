"""
Command validation helpers - DRY validation logic for commands.

This module provides reusable validation functions to eliminate code duplication
across command classes. Each function returns (is_valid, error_message) tuple.

Usage:
    from .command_validators import validate_fleet_ownership, validate_world_ownership

    def validate(self, game_state):
        # Reuse common validation
        valid, msg = validate_fleet_ownership(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # Add command-specific validation
        # ...
        return True, ""
"""
from typing import Tuple, Optional


# ============================================================================
# FLEET VALIDATIONS
# ============================================================================

def validate_fleet_exists(game_state, fleet_id: int) -> Tuple[bool, str, Optional[object]]:
    """
    Validate that a fleet exists.

    Returns:
        (is_valid, error_message, fleet_object)
    """
    fleet = game_state.get_fleet(fleet_id)
    if not fleet:
        return False, f"Fleet {fleet_id} does not exist", None
    return True, "", fleet


def validate_fleet_ownership(game_state, player, fleet_id: int) -> Tuple[bool, str, Optional[object]]:
    """
    Validate that a fleet exists and is owned by the player.

    Returns:
        (is_valid, error_message, fleet_object)
    """
    valid, msg, fleet = validate_fleet_exists(game_state, fleet_id)
    if not valid:
        return valid, msg, None

    if fleet.owner != player:
        return False, f"You do not own fleet {fleet_id}", None

    return True, "", fleet


def validate_fleet_has_ships(game_state, player, fleet_id: int,
                            min_ships: int = 1) -> Tuple[bool, str, Optional[object]]:
    """
    Validate that a fleet exists, is owned by player, and has ships.

    Args:
        min_ships: Minimum number of ships required (default 1)

    Returns:
        (is_valid, error_message, fleet_object)
    """
    valid, msg, fleet = validate_fleet_ownership(game_state, player, fleet_id)
    if not valid:
        return valid, msg, None

    if fleet.ships < min_ships:
        if min_ships == 1:
            return False, f"Fleet {fleet_id} has no ships", None
        else:
            return False, f"Fleet {fleet_id} has only {fleet.ships} ships, need {min_ships}", None

    return True, "", fleet


def validate_fleet_has_cargo(game_state, player, fleet_id: int,
                             min_cargo: int = 1) -> Tuple[bool, str, Optional[object]]:
    """
    Validate that a fleet exists, is owned by player, and has cargo.

    Args:
        min_cargo: Minimum cargo required (default 1)

    Returns:
        (is_valid, error_message, fleet_object)
    """
    valid, msg, fleet = validate_fleet_ownership(game_state, player, fleet_id)
    if not valid:
        return valid, msg, None

    if fleet.cargo < min_cargo:
        if min_cargo == 1:
            return False, f"Fleet {fleet_id} has no cargo", None
        else:
            return False, f"Fleet {fleet_id} only has {fleet.cargo} cargo", None

    return True, "", fleet


def validate_fleet_at_same_world(game_state, fleet1_id: int, fleet2_id: int) -> Tuple[bool, str]:
    """
    Validate that two fleets are at the same world.

    Returns:
        (is_valid, error_message)
    """
    fleet1 = game_state.get_fleet(fleet1_id)
    fleet2 = game_state.get_fleet(fleet2_id)

    if not fleet1 or not fleet2:
        return False, "One or both fleets do not exist"

    if fleet1.world != fleet2.world:
        return False, f"Fleets must be at same world"

    return True, ""


# ============================================================================
# WORLD VALIDATIONS
# ============================================================================

def validate_world_exists(game_state, world_id: int) -> Tuple[bool, str, Optional[object]]:
    """
    Validate that a world exists.

    Returns:
        (is_valid, error_message, world_object)
    """
    world = game_state.get_world(world_id)
    if not world:
        return False, f"World {world_id} does not exist", None
    return True, "", world


def validate_world_ownership(game_state, player, world_id: int) -> Tuple[bool, str, Optional[object]]:
    """
    Validate that a world exists and is owned by the player.

    Returns:
        (is_valid, error_message, world_object)
    """
    valid, msg, world = validate_world_exists(game_state, world_id)
    if not valid:
        return valid, msg, None

    if world.owner != player:
        return False, f"You do not own world {world_id}", None

    return True, "", world


def validate_world_has_population(game_state, player, world_id: int,
                                  min_population: int = 1) -> Tuple[bool, str, Optional[object]]:
    """
    Validate that a world has population.

    Returns:
        (is_valid, error_message, world_object)
    """
    valid, msg, world = validate_world_ownership(game_state, player, world_id)
    if not valid:
        return valid, msg, None

    if world.population < min_population:
        if min_population == 1:
            return False, f"World {world_id} has no population", None
        else:
            return False, f"World {world_id} only has {world.population} population", None

    return True, "", world


def validate_world_connected(game_state, world_id: int, target_world_id: int) -> Tuple[bool, str]:
    """
    Validate that two worlds are connected.

    Returns:
        (is_valid, error_message)
    """
    valid, msg, world = validate_world_exists(game_state, world_id)
    if not valid:
        return valid, msg

    if target_world_id not in world.connections:
        return False, f"World {target_world_id} is not connected to {world_id}"

    return True, ""


# ============================================================================
# RESOURCE VALIDATIONS
# ============================================================================

def validate_sufficient_resources(world, amount: int) -> Tuple[bool, str]:
    """
    Validate that a world has sufficient industry, metal, and population.

    Returns:
        (is_valid, error_message)
    """
    max_build = min(world.industry, world.metal, world.population)
    if amount > max_build:
        return False, f"Cannot build {amount}, maximum is {max_build} (limited by industry={world.industry}, metal={world.metal}, pop={world.population})"

    return True, ""


def validate_ships_available(source, ship_type: str, amount: int) -> Tuple[bool, str]:
    """
    Validate that sufficient ships are available.

    Args:
        source: Fleet or World object
        ship_type: "fleet", "I", or "P"
        amount: Number of ships required

    Returns:
        (is_valid, error_message)
    """
    if ship_type == "fleet" or ship_type == "F":
        available = source.ships
        ship_name = "ships"
    elif ship_type == "I":
        available = source.iships
        ship_name = "ISHIPS"
    elif ship_type == "P":
        available = source.pships
        ship_name = "PSHIPS"
    else:
        return False, f"Invalid ship type: {ship_type}"

    if available < amount:
        return False, f"only has {available} {ship_name}, need {amount}"

    return True, ""


# ============================================================================
# ARTIFACT VALIDATIONS
# ============================================================================

def validate_artifact_exists(source, artifact_id: int) -> Tuple[bool, str, Optional[object]]:
    """
    Validate that an artifact exists in a source (fleet or world).

    Returns:
        (is_valid, error_message, artifact_object)
    """
    for artifact in source.artifacts:
        if artifact.id == artifact_id:
            return True, "", artifact

    return False, f"Artifact {artifact_id} not found", None


# ============================================================================
# COMBAT VALIDATIONS
# ============================================================================

def validate_not_own_fleet(game_state, player, target_fleet_id: int) -> Tuple[bool, str]:
    """
    Validate that a target fleet is not owned by the player.

    Returns:
        (is_valid, error_message)
    """
    valid, msg, fleet = validate_fleet_exists(game_state, target_fleet_id)
    if not valid:
        return valid, msg

    if fleet.owner == player:
        return False, "Cannot fire at your own fleet"

    return True, ""


# ============================================================================
# CHARACTER-SPECIFIC VALIDATIONS
# ============================================================================

def validate_character_type(player, required_type: str) -> Tuple[bool, str]:
    """
    Validate that a player has a specific character type.

    Returns:
        (is_valid, error_message)
    """
    if player.character_type != required_type:
        return False, f"Only {required_type} can use this command"

    return True, ""


# ============================================================================
# COMPOSITE VALIDATORS (Common Patterns)
# ============================================================================

def validate_transfer_ships_basic(game_state, player, fleet_id: int,
                                  amount: int) -> Tuple[bool, str, Optional[object]]:
    """
    Common validation for transferring ships from a fleet.
    Validates: fleet ownership, sufficient ships.

    Returns:
        (is_valid, error_message, fleet_object)
    """
    valid, msg, fleet = validate_fleet_ownership(game_state, player, fleet_id)
    if not valid:
        return valid, msg, None

    valid, msg = validate_ships_available(fleet, "fleet", amount)
    if not valid:
        return valid, msg, None

    return True, "", fleet


def validate_build_basic(game_state, player, world_id: int,
                        amount: int) -> Tuple[bool, str, Optional[object]]:
    """
    Common validation for building.
    Validates: world ownership, sufficient resources.

    Returns:
        (is_valid, error_message, world_object)
    """
    valid, msg, world = validate_world_ownership(game_state, player, world_id)
    if not valid:
        return valid, msg, None

    if amount <= 0:
        return False, "Build amount must be positive", None

    valid, msg = validate_sufficient_resources(world, amount)
    if not valid:
        return valid, msg, None

    return True, "", world
