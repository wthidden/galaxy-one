"""
Command pattern for game actions.
All player commands go through validation and execution.
"""
from abc import ABC, abstractmethod
from typing import Optional, List
from .command_validators import (
    validate_fleet_has_ships,
    validate_fleet_has_cargo,
    validate_fleet_ownership,
    validate_world_ownership,
    validate_world_has_population,
    validate_world_connected,
    validate_transfer_ships_basic,
    validate_build_basic,
    validate_not_own_fleet,
    validate_fleet_at_same_world,
    validate_artifact_exists,
    validate_character_type,
    validate_ships_available,
    validate_sufficient_resources
)


class Command(ABC):
    """Base class for all game commands."""

    def __init__(self, player):
        self.player = player

    @abstractmethod
    def validate(self, game_state) -> tuple[bool, str]:
        """
        Validate if command can be executed.

        Returns:
            (is_valid, error_message)
        """
        pass

    @abstractmethod
    def to_order(self) -> dict:
        """Convert command to an order dict for queueing."""
        pass

    @abstractmethod
    def get_description(self) -> str:
        """Get human-readable description of command."""
        pass


class MoveFleetCommand(Command):
    """Move a fleet along a path."""

    def __init__(self, player, fleet_id: int, path: List[int]):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.path = path

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership and has ships
        valid, msg, fleet = validate_fleet_has_ships(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # Validate path connectivity
        current = fleet.world.id
        for next_world_id in self.path:
            valid, msg = validate_world_connected(game_state, current, next_world_id)
            if not valid:
                return valid, msg
            current = next_world_id

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "MOVE",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "path": self.path
        }

    def get_description(self) -> str:
        return f"Move F{self.fleet_id} -> W{self.path[-1]}"


class BuildCommand(Command):
    """Build ships at a world."""

    def __init__(self, player, world_id: int, amount: int, target_type: str, target_id: Optional[int] = None):
        super().__init__(player)
        self.world_id = world_id
        self.amount = amount
        self.target_type = target_type  # "I", "P", "F"
        self.target_id = target_id  # Fleet ID if building on fleet

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate world ownership and resources
        valid, msg, world = validate_build_basic(game_state, self.player, self.world_id, self.amount)
        if not valid:
            return valid, msg

        # If building on a fleet, validate fleet
        if self.target_type == "F" and self.target_id:
            valid, msg, fleet = validate_fleet_ownership(game_state, self.player, self.target_id)
            if not valid:
                return valid, msg

            if fleet.world != world:
                return False, f"Fleet {self.target_id} is not at world {self.world_id}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "BUILD",
            "player": self.player,
            "world_id": self.world_id,
            "amount": self.amount,
            "target_type": self.target_type,
            "target_id": self.target_id
        }

    def get_description(self) -> str:
        target = f"F{self.target_id}" if self.target_id else self.target_type
        return f"Build {self.amount} {target} at W{self.world_id}"


class TransferCommand(Command):
    """Transfer ships between fleet and garrison or other fleets."""

    def __init__(self, player, fleet_id: int, amount: int, target_type: str, target_id: Optional[int] = None):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.amount = amount
        self.target_type = target_type  # "I", "P", "F"
        self.target_id = target_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership and sufficient ships
        valid, msg, fleet = validate_transfer_ships_basic(
            game_state, self.player, self.fleet_id, self.amount
        )
        if not valid:
            return valid, msg

        # If transferring to world garrison, validate world ownership
        world = fleet.world
        if self.target_type in ["I", "P"]:
            valid, msg, _ = validate_world_ownership(game_state, self.player, world.id)
            if not valid:
                return False, "Cannot transfer to garrison of world you don't own"

        # If transferring to another fleet, validate target fleet and location
        if self.target_type == "F" and self.target_id:
            valid, msg = validate_fleet_at_same_world(game_state, self.fleet_id, self.target_id)
            if not valid:
                return False, "Target fleet must be at same world"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "TRANSFER",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "amount": self.amount,
            "target_type": self.target_type,
            "target_id": self.target_id
        }

    def get_description(self) -> str:
        target = f"F{self.target_id}" if self.target_id else self.target_type
        return f"Transfer {self.amount} from F{self.fleet_id} to {target}"


class TransferFromDefenseCommand(Command):
    """Transfer ships FROM ISHIPS/PSHIPS to fleet or between defenses."""

    def __init__(self, player, world_id: int, amount: int, source_type: str, target_type: str, target_id: Optional[int] = None):
        super().__init__(player)
        self.world_id = world_id
        self.amount = amount
        self.source_type = source_type  # "I" or "P"
        self.target_type = target_type  # "I", "P", or "F"
        self.target_id = target_id  # Required if target_type is "F"

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate world ownership
        valid, msg, world = validate_world_ownership(game_state, self.player, self.world_id)
        if not valid:
            return valid, msg

        # Check source has enough ships
        valid, msg = validate_ships_available(world, self.source_type, self.amount)
        if not valid:
            return False, f"World {self.world_id} {msg}"

        # Validate target fleet if specified
        if self.target_type == "F":
            if not self.target_id:
                return False, "Target fleet ID required"
            target_fleet = game_state.get_fleet(self.target_id)
            if not target_fleet:
                return False, f"Fleet {self.target_id} does not exist"
            if target_fleet.world.id != self.world_id:
                return False, f"Fleet {self.target_id} not at world {self.world_id}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "TRANSFER_FROM_DEFENSE",
            "player": self.player,
            "world_id": self.world_id,
            "amount": self.amount,
            "source_type": self.source_type,
            "target_type": self.target_type,
            "target_id": self.target_id
        }

    def get_description(self) -> str:
        source = f"{self.source_type}SHIPS@W{self.world_id}"
        target = f"F{self.target_id}" if self.target_id else f"{self.target_type}SHIPS"
        return f"Transfer {self.amount} from {source} to {target}"


class TransferArtifactCommand(Command):
    """Transfer artifact between fleet and world or between fleets."""

    def __init__(self, player, source_type: str, source_id: int, artifact_id: int,
                 target_type: str, target_id: Optional[int] = None):
        super().__init__(player)
        self.source_type = source_type  # "F" or "W"
        self.source_id = source_id
        self.artifact_id = artifact_id
        self.target_type = target_type  # "F" or "W"
        self.target_id = target_id  # Required if target_type is "F"

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate source
        if self.source_type == "F":
            valid, msg, source = validate_fleet_ownership(game_state, self.player, self.source_id)
            if not valid:
                return valid, msg
            source_world = source.world
        elif self.source_type == "W":
            valid, msg, source = validate_world_ownership(game_state, self.player, self.source_id)
            if not valid:
                return valid, msg
            source_world = source
        else:
            return False, "Invalid source type"

        # Check artifact exists in source
        valid, msg, artifact = validate_artifact_exists(source, self.artifact_id)
        if not valid:
            return valid, msg

        # Validate target
        if self.target_type == "F":
            if not self.target_id:
                return False, "Target fleet ID required"
            valid, msg, target = validate_fleet_ownership(game_state, self.player, self.target_id)
            if not valid:
                return valid, msg
            # Fleets must be at same world
            if target.world.id != source_world.id:
                return False, "Source and target must be at same world"
        elif self.target_type == "W":
            # Transfer to world garrison at source location - already validated
            pass
        else:
            return False, "Invalid target type"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "TRANSFER_ARTIFACT",
            "player": self.player,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "artifact_id": self.artifact_id,
            "target_type": self.target_type,
            "target_id": self.target_id
        }

    def get_description(self) -> str:
        source = f"{self.source_type}{self.source_id}"
        target = f"F{self.target_id}" if self.target_type == "F" and self.target_id else "World"
        return f"Transfer Artifact {self.artifact_id} from {source} to {target}"


class FireCommand(Command):
    """Fire at fleet or world - supports all fire target types."""

    def __init__(self, player, fleet_id: int, target_type: str, target_id: Optional[int] = None, sub_target: Optional[str] = None):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.target_type = target_type  # "FLEET", "ISHIPS", "PSHIPS", "HOME", "INDUSTRY", "POPULATION", "CONVERTS"
        self.target_id = target_id  # Fleet ID if targeting fleet
        self.sub_target = sub_target  # Additional target specification

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet has ships
        valid, msg, fleet = validate_fleet_has_ships(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # If firing at a fleet, validate target
        if self.target_type == "FLEET" and self.target_id:
            # Check not own fleet
            valid, msg = validate_not_own_fleet(game_state, self.player, self.target_id)
            if not valid:
                return valid, msg

            # Check at same world
            valid, msg = validate_fleet_at_same_world(game_state, self.fleet_id, self.target_id)
            if not valid:
                return False, "Target fleet must be at same world"

        # Validate target type
        valid_targets = ["FLEET", "ISHIPS", "PSHIPS", "HOME", "INDUSTRY", "POPULATION", "CONVERTS", "WORLD"]
        if self.target_type not in valid_targets:
            return False, f"Invalid target type: {self.target_type}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "FIRE",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "sub_target": self.sub_target
        }

    def get_description(self) -> str:
        if self.target_type == "FLEET":
            return f"F{self.fleet_id} Fire at F{self.target_id}"
        elif self.target_type == "ISHIPS":
            return f"F{self.fleet_id} Fire at ISHIPS (then industry)"
        elif self.target_type == "PSHIPS":
            return f"F{self.fleet_id} Fire at PSHIPS (then population)"
        elif self.target_type == "HOME":
            return f"F{self.fleet_id} Fire at home fleets"
        elif self.target_type == "CONVERTS":
            return f"F{self.fleet_id} Fire at converts"
        else:
            return f"F{self.fleet_id} Fire at {self.target_type}"


class AmbushCommand(Command):
    """Set fleet to ambush mode."""

    def __init__(self, player, fleet_id: int):
        super().__init__(player)
        self.fleet_id = fleet_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership
        valid, msg, _ = validate_fleet_ownership(game_state, self.player, self.fleet_id)
        return valid, msg

    def to_order(self) -> dict:
        return {
            "type": "AMBUSH",
            "player": self.player,
            "fleet_id": self.fleet_id
        }

    def get_description(self) -> str:
        return f"F{self.fleet_id} Ambush"


class DefenseFireCommand(Command):
    """Fire from ISHIPS or PSHIPS at a target."""

    def __init__(self, player, world_id: int, defense_type: str, target_type: str, target_id: Optional[int] = None):
        super().__init__(player)
        self.world_id = world_id
        self.defense_type = defense_type  # "I" or "P"
        self.target_type = target_type  # "F" (fleet) or "C" (converts)
        self.target_id = target_id  # Fleet ID if targeting fleet

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate world ownership
        valid, msg, world = validate_world_ownership(game_state, self.player, self.world_id)
        if not valid:
            return valid, msg

        # Check we have defense ships
        valid, msg = validate_ships_available(world, self.defense_type, 1)
        if not valid:
            ship_type = "ISHIPS" if self.defense_type == "I" else "PSHIPS"
            return False, f"World {self.world_id} has no {ship_type}"

        # Validate target fleet if specified
        if self.target_type == "F" and self.target_id:
            from .command_validators import validate_fleet_exists
            valid, msg, target = validate_fleet_exists(game_state, self.target_id)
            if not valid:
                return valid, msg
            if target.world.id != self.world_id:
                return False, f"Fleet {self.target_id} not at world {self.world_id}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "DEFENSE_FIRE",
            "player": self.player,
            "world_id": self.world_id,
            "defense_type": self.defense_type,
            "target_type": self.target_type,
            "target_id": self.target_id
        }

    def get_description(self) -> str:
        defense = f"{self.defense_type}SHIPS@W{self.world_id}"
        if self.target_type == "F":
            return f"{defense} Fire at F{self.target_id}"
        else:
            return f"{defense} Fire at Converts"


class ProbeCommand(Command):
    """Probe an adjacent world (F#P#, I#P#, P#P#)."""

    def __init__(self, player, source_type: str, source_id: int, target_world: int):
        super().__init__(player)
        self.source_type = source_type  # "F", "I", or "P"
        self.source_id = source_id  # Fleet ID or World ID
        self.target_world = target_world

    def validate(self, game_state) -> tuple[bool, str]:
        if self.source_type == "F":
            # Fleet probe - validate fleet has ships
            valid, msg, fleet = validate_fleet_has_ships(game_state, self.player, self.source_id)
            if not valid:
                return valid, msg

            # Check target is adjacent
            valid, msg = validate_world_connected(game_state, fleet.world.id, self.target_world)
            if not valid:
                return False, f"World {self.target_world} is not adjacent to {fleet.world.id}"

        else:
            # Defense probe - validate world ownership
            valid, msg, world = validate_world_ownership(game_state, self.player, self.source_id)
            if not valid:
                return valid, msg

            # Check we have defense ships
            valid, msg = validate_ships_available(world, self.source_type, 1)
            if not valid:
                ship_type = "ISHIPS" if self.source_type == "I" else "PSHIPS"
                return False, f"World {self.source_id} has no {ship_type}"

            # Check target is adjacent
            valid, msg = validate_world_connected(game_state, self.source_id, self.target_world)
            if not valid:
                return False, f"World {self.target_world} is not adjacent to {self.source_id}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "PROBE",
            "player": self.player,
            "source_type": self.source_type,
            "source_id": self.source_id,
            "target_world": self.target_world
        }

    def get_description(self) -> str:
        if self.source_type == "F":
            return f"F{self.source_id} Probe W{self.target_world}"
        else:
            return f"{self.source_type}SHIPS@W{self.source_id} Probe W{self.target_world}"


class ScrapShipsCommand(Command):
    """Scrap ships to make industry (W#S#)."""

    def __init__(self, player, world_id: int, amount: int):
        super().__init__(player)
        self.world_id = world_id
        self.amount = amount  # Amount of industry to create

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate world ownership
        valid, msg, world = validate_world_ownership(game_state, self.player, self.world_id)
        if not valid:
            return valid, msg

        # Check if player is empire builder (gets bonus)
        is_empire_builder = self.player.character_type == "Empire Builder"
        ships_per_industry = 4 if is_empire_builder else 6

        # Check we have enough ISHIPS to scrap
        ships_needed = self.amount * ships_per_industry
        valid, msg = validate_ships_available(world, "I", ships_needed)
        if not valid:
            return False, f"Need {ships_needed} ISHIPS to create {self.amount} industry (have {world.iships})"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "SCRAP_SHIPS",
            "player": self.player,
            "world_id": self.world_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        return f"W{self.world_id} Scrap ships to create {self.amount} industry"


class JettisonCommand(Command):
    """Jettison cargo (F#J or F#J#)."""

    def __init__(self, player, fleet_id: int, amount: Optional[int] = None):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.amount = amount  # None means jettison all

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet has cargo
        min_cargo = self.amount if self.amount else 1
        valid, msg, fleet = validate_fleet_has_cargo(game_state, self.player, self.fleet_id, min_cargo)
        return valid, msg

    def to_order(self) -> dict:
        return {
            "type": "JETTISON",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        if self.amount:
            return f"F{self.fleet_id} Jettison {self.amount} cargo"
        else:
            return f"F{self.fleet_id} Jettison all cargo"


class UnloadConsumerGoodsCommand(Command):
    """Unload cargo as consumer goods (F#N or F#N#)."""

    def __init__(self, player, fleet_id: int, amount: Optional[int] = None):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.amount = amount  # None means all

    def validate(self, game_state) -> tuple[bool, str]:
        # Must be Merchant to use consumer goods
        valid, msg = validate_character_type(self.player, "Merchant")
        if not valid:
            return valid, msg

        # Validate fleet has cargo
        min_cargo = self.amount if self.amount else 1
        valid, msg, fleet = validate_fleet_has_cargo(game_state, self.player, self.fleet_id, min_cargo)
        return valid, msg

    def to_order(self) -> dict:
        return {
            "type": "UNLOAD_CONSUMER_GOODS",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        if self.amount:
            return f"F{self.fleet_id} Unload {self.amount} consumer goods"
        else:
            return f"F{self.fleet_id} Unload all as consumer goods"


class LoadCommand(Command):
    """Load population onto fleet as cargo."""

    def __init__(self, player, fleet_id: int, amount: Optional[int] = None):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.amount = amount  # None means load max

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership
        valid, msg, fleet = validate_fleet_ownership(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # Validate world has population
        world = fleet.world
        valid, msg, _ = validate_world_has_population(game_state, self.player, world.id)
        if not valid:
            return valid, msg

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "LOAD",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        if self.amount is None:
            return f"F{self.fleet_id} Load Max"
        else:
            return f"F{self.fleet_id} Load {self.amount}"


class UnloadCommand(Command):
    """Unload cargo from fleet to world."""

    def __init__(self, player, fleet_id: int, amount: Optional[int] = None):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.amount = amount  # None means unload all

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet has cargo
        valid, msg, fleet = validate_fleet_has_cargo(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # Validate world ownership
        world = fleet.world
        valid, msg, _ = validate_world_ownership(game_state, self.player, world.id)
        if not valid:
            return False, "Cannot unload to world you don't own"

        # Check population limit
        if world.population >= world.limit:
            return False, f"World {world.id} is at population limit"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "UNLOAD",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        if self.amount is None:
            return f"F{self.fleet_id} Unload All"
        else:
            return f"F{self.fleet_id} Unload {self.amount}"


class MigrateCommand(Command):
    """Migrate population from one world to another."""

    def __init__(self, player, world_id: int, amount: int, dest_world: int):
        super().__init__(player)
        self.world_id = world_id
        self.amount = amount
        self.dest_world = dest_world

    def validate(self, game_state) -> tuple[bool, str]:
        world = game_state.get_world(self.world_id)

        if not world:
            return False, f"World {self.world_id} does not exist"

        if world.owner != self.player:
            return False, f"You do not own world {self.world_id}"

        dest = game_state.get_world(self.dest_world)
        if not dest:
            return False, f"Destination world {self.dest_world} does not exist"

        if self.dest_world not in world.connections:
            return False, f"World {self.dest_world} is not connected to {self.world_id}"

        if self.amount <= 0:
            return False, "Migration amount must be positive"

        max_migrate = min(world.industry, world.metal, world.population)
        if self.amount > max_migrate:
            return False, f"Cannot migrate {self.amount}, maximum is {max_migrate}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "MIGRATE",
            "player": self.player,
            "world_id": self.world_id,
            "amount": self.amount,
            "dest_world": self.dest_world
        }

    def get_description(self) -> str:
        return f"Migrate {self.amount} population from W{self.world_id} to W{self.dest_world}"


class ViewArtifactCommand(Command):
    """View artifact details (V#, V#F#, V#W)."""

    def __init__(self, player, artifact_id: int, location_type: Optional[str] = None,
                 location_id: Optional[int] = None):
        super().__init__(player)
        self.artifact_id = artifact_id
        self.location_type = location_type  # None, "F", or "W"
        self.location_id = location_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Find the artifact
        artifact = None
        source = None

        if self.location_type == "F":
            # View artifact on specific fleet
            valid, msg, fleet = validate_fleet_ownership(game_state, self.player, self.location_id)
            if not valid:
                return valid, msg

            valid, msg, artifact = validate_artifact_exists(fleet, self.artifact_id)
            if not valid:
                return False, f"Artifact {self.artifact_id} not found on Fleet {self.location_id}"

        elif self.location_type == "W":
            # View artifact on world where any of player's fleets are located
            # Find first fleet location
            player_fleets = [f for f in game_state.fleets.values() if f.owner == self.player and f.ships > 0]
            if not player_fleets:
                return False, "You have no fleets"

            world = player_fleets[0].world
            for a in world.artifacts:
                if a.id == self.artifact_id:
                    artifact = a
                    source = world
                    break

            if not artifact:
                return False, f"Artifact {self.artifact_id} not found at world {world.id}"

        else:
            # V# - search player's fleets and owned worlds
            # Check player's fleets first
            for fleet in game_state.fleets.values():
                if fleet.owner == self.player:
                    for a in fleet.artifacts:
                        if a.id == self.artifact_id:
                            artifact = a
                            source = fleet
                            break
                    if artifact:
                        break

            # If not found, check player's worlds
            if not artifact:
                for world in game_state.worlds.values():
                    if world.owner == self.player:
                        for a in world.artifacts:
                            if a.id == self.artifact_id:
                                artifact = a
                                source = world
                                break
                        if artifact:
                            break

            if not artifact:
                return False, f"Artifact {self.artifact_id} not found in your possession"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "VIEW_ARTIFACT",
            "player": self.player,
            "artifact_id": self.artifact_id,
            "location_type": self.location_type,
            "location_id": self.location_id
        }

    def get_description(self) -> str:
        if self.location_type == "F":
            return f"View Artifact {self.artifact_id} on Fleet {self.location_id}"
        elif self.location_type == "W":
            return f"View Artifact {self.artifact_id} on World"
        else:
            return f"View Artifact {self.artifact_id}"


class DeclareRelationCommand(Command):
    """Declare peace/war with another fleet (F#Q, F#X)."""

    def __init__(self, player, fleet_id: int, target_fleet_id: int, relation_type: str):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.target_fleet_id = target_fleet_id
        self.relation_type = relation_type  # "PEACE" or "WAR"

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership
        valid, msg, _ = validate_fleet_ownership(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # Validate target fleet is not owned by player
        valid, msg = validate_not_own_fleet(game_state, self.player, self.target_fleet_id)
        return valid, msg

    def to_order(self) -> dict:
        return {
            "type": "DECLARE_RELATION",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "target_fleet_id": self.target_fleet_id,
            "relation_type": self.relation_type
        }

    def get_description(self) -> str:
        relation = "Peace" if self.relation_type == "PEACE" else "War"
        return f"F{self.fleet_id} declares {relation} with F{self.target_fleet_id}"


class PlunderCommand(Command):
    """Plunder world - convert population to metal (W#X)."""

    def __init__(self, player, world_id: int):
        super().__init__(player)
        self.world_id = world_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate world has population
        valid, msg, world = validate_world_has_population(game_state, self.player, self.world_id)
        return valid, msg

    def to_order(self) -> dict:
        return {
            "type": "PLUNDER",
            "player": self.player,
            "world_id": self.world_id
        }

    def get_description(self) -> str:
        return f"Plunder W{self.world_id} (convert population to metal)"


class BuildIndustryCommand(Command):
    """Build industry on world (W#I#I)."""

    def __init__(self, player, world_id: int, amount: int):
        super().__init__(player)
        self.world_id = world_id
        self.amount = amount

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate world ownership
        valid, msg, world = validate_world_ownership(game_state, self.player, self.world_id)
        if not valid:
            return valid, msg

        if self.amount <= 0:
            return False, "Build amount must be positive"

        # Empire Builders pay 4 per industry, others pay 5
        cost_per_industry = 4 if self.player.character_type == "Empire Builder" else 5

        total_industry_cost = self.amount * cost_per_industry
        total_metal_cost = self.amount * cost_per_industry

        if world.industry < total_industry_cost:
            return False, f"Need {total_industry_cost} industry, have {world.industry}"

        if world.metal < total_metal_cost:
            return False, f"Need {total_metal_cost} metal, have {world.metal}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "BUILD_INDUSTRY",
            "player": self.player,
            "world_id": self.world_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        return f"Build {self.amount} industry on W{self.world_id}"


class IncreasePopulationLimitCommand(Command):
    """Increase population limit on world (W#I#L)."""

    def __init__(self, player, world_id: int, amount: int):
        super().__init__(player)
        self.world_id = world_id
        self.amount = amount

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate world ownership
        valid, msg, world = validate_world_ownership(game_state, self.player, self.world_id)
        if not valid:
            return valid, msg

        if self.amount <= 0:
            return False, "Amount must be positive"

        # Costs 5 industry + 5 metal per increase
        total_industry_cost = self.amount * 5
        total_metal_cost = self.amount * 5

        if world.industry < total_industry_cost:
            return False, f"Need {total_industry_cost} industry, have {world.industry}"

        if world.metal < total_metal_cost:
            return False, f"Need {total_metal_cost} metal, have {world.metal}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "INCREASE_POPULATION_LIMIT",
            "player": self.player,
            "world_id": self.world_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        return f"Increase population limit by {self.amount} on W{self.world_id}"


class BuildRobotsCommand(Command):
    """Build robots from industry (W#B#R) - Berserker only."""

    def __init__(self, player, world_id: int, amount: int):
        super().__init__(player)
        self.world_id = world_id
        self.amount = amount

    def validate(self, game_state) -> tuple[bool, str]:
        # Only Berserker can build robots
        valid, msg = validate_character_type(self.player, "Berserker")
        if not valid:
            return valid, msg

        # Validate world ownership
        valid, msg, world = validate_world_ownership(game_state, self.player, self.world_id)
        if not valid:
            return valid, msg

        if self.amount <= 0:
            return False, "Build amount must be positive"

        # 1 industry = 2 robots
        industry_needed = (self.amount + 1) // 2  # Round up

        if world.industry < industry_needed:
            return False, f"Need {industry_needed} industry, have {world.industry}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "BUILD_ROBOTS",
            "player": self.player,
            "world_id": self.world_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        return f"Build {self.amount} robots on W{self.world_id}"


class GiftFleetCommand(Command):
    """Gift fleet to another player (F#G=xxxxxx)."""

    def __init__(self, player, fleet_id: int, target_player_name: str):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.target_player_name = target_player_name

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership
        valid, msg, fleet = validate_fleet_ownership(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # Check target player exists
        target_player = None
        for p in game_state.players.values():
            if p.name == self.target_player_name:
                target_player = p
                break

        if not target_player:
            return False, f"Player '{self.target_player_name}' not found"

        if target_player == self.player:
            return False, "Cannot gift fleet to yourself"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "GIFT_FLEET",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "target_player_name": self.target_player_name
        }

    def get_description(self) -> str:
        return f"Gift F{self.fleet_id} to player '{self.target_player_name}'"


class GiftWorldCommand(Command):
    """Gift world to another player (W#G=xxxxxx)."""

    def __init__(self, player, world_id: int, target_player_name: str):
        super().__init__(player)
        self.world_id = world_id
        self.target_player_name = target_player_name

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate world ownership
        valid, msg, world = validate_world_ownership(game_state, self.player, self.world_id)
        if not valid:
            return valid, msg

        # Cannot gift homeworld
        if world.key:
            return False, "Cannot gift your homeworld"

        # Check target player exists
        target_player = None
        for p in game_state.players.values():
            if p.name == self.target_player_name:
                target_player = p
                break

        if not target_player:
            return False, f"Player '{self.target_player_name}' not found"

        if target_player == self.player:
            return False, "Cannot gift world to yourself"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "GIFT_WORLD",
            "player": self.player,
            "world_id": self.world_id,
            "target_player_name": self.target_player_name
        }

    def get_description(self) -> str:
        return f"Gift W{self.world_id} to player '{self.target_player_name}'"


class BuildPBBCommand(Command):
    """Build Planet Buster Bomb (F#B) - requires 25+ ships."""

    def __init__(self, player, fleet_id: int):
        super().__init__(player)
        self.fleet_id = fleet_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership and has ships
        valid, msg, fleet = validate_fleet_has_ships(game_state, self.player, self.fleet_id, min_ships=25)
        if not valid:
            return valid, msg

        # Fleet cannot already have a PBB
        if fleet.has_pbb:
            return False, f"Fleet {self.fleet_id} already has a Planet Buster Bomb"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "BUILD_PBB",
            "player": self.player,
            "fleet_id": self.fleet_id
        }

    def get_description(self) -> str:
        return f"Build Planet Buster Bomb on F{self.fleet_id}"


class DropPBBCommand(Command):
    """Drop Planet Buster Bomb (F#D) - destroys world."""

    def __init__(self, player, fleet_id: int):
        super().__init__(player)
        self.fleet_id = fleet_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership
        valid, msg, fleet = validate_fleet_ownership(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # Fleet must have a PBB
        if not fleet.has_pbb:
            return False, f"Fleet {self.fleet_id} does not have a Planet Buster Bomb"

        # Cannot drop on homeworld
        world = fleet.world
        if world.key:
            return False, "Cannot drop Planet Buster Bomb on a homeworld"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "DROP_PBB",
            "player": self.player,
            "fleet_id": self.fleet_id
        }

    def get_description(self) -> str:
        return f"Drop Planet Buster Bomb from F{self.fleet_id}"


class RobotAttackCommand(Command):
    """Convert ships to robots for attack (F#R#) - Berserker only."""

    def __init__(self, player, fleet_id: int, amount: int):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.amount = amount

    def validate(self, game_state) -> tuple[bool, str]:
        # Only Berserker can use robot attacks
        valid, msg = validate_character_type(self.player, "Berserker")
        if not valid:
            return valid, msg

        # Validate fleet ownership and has ships
        valid, msg, fleet = validate_fleet_has_ships(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        if self.amount <= 0:
            return False, "Amount must be positive"

        # 1 ship = 2 robots
        ships_needed = (self.amount + 1) // 2  # Round up

        if fleet.ships < ships_needed:
            return False, f"Fleet {self.fleet_id} only has {fleet.ships} ships, need {ships_needed}"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "ROBOT_ATTACK",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "amount": self.amount
        }

    def get_description(self) -> str:
        return f"Convert {self.amount} robots from F{self.fleet_id} for attack"


class DeclareAllyCommand(Command):
    """Declare another player as ally (A=xxxxxx)."""

    def __init__(self, player, target_player_name: str):
        super().__init__(player)
        self.target_player_name = target_player_name

    def validate(self, game_state) -> tuple[bool, str]:
        # Check target player exists
        target_player = None
        for p in game_state.players.values():
            if p.name == self.target_player_name:
                target_player = p
                break

        if not target_player:
            return False, f"Player '{self.target_player_name}' not found"

        if target_player == self.player:
            return False, "Cannot declare yourself as ally"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "DECLARE_ALLY",
            "player": self.player,
            "target_player_name": self.target_player_name
        }

    def get_description(self) -> str:
        return f"Declare '{self.target_player_name}' as ally"


class DeclareNonAllyCommand(Command):
    """Declare player as non-ally (N=xxxxxx)."""

    def __init__(self, player, target_player_name: str):
        super().__init__(player)
        self.target_player_name = target_player_name

    def validate(self, game_state) -> tuple[bool, str]:
        # Check target player exists
        target_player = None
        for p in game_state.players.values():
            if p.name == self.target_player_name:
                target_player = p
                break

        if not target_player:
            return False, f"Player '{self.target_player_name}' not found"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "DECLARE_NON_ALLY",
            "player": self.player,
            "target_player_name": self.target_player_name
        }

    def get_description(self) -> str:
        return f"Declare '{self.target_player_name}' as non-ally"


class DeclareLoaderCommand(Command):
    """Allow player to load metal from your worlds (L=xxxxxx)."""

    def __init__(self, player, target_player_name: str):
        super().__init__(player)
        self.target_player_name = target_player_name

    def validate(self, game_state) -> tuple[bool, str]:
        # Check target player exists
        target_player = None
        for p in game_state.players.values():
            if p.name == self.target_player_name:
                target_player = p
                break

        if not target_player:
            return False, f"Player '{self.target_player_name}' not found"

        if target_player == self.player:
            return False, "Cannot declare yourself as loader"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "DECLARE_LOADER",
            "player": self.player,
            "target_player_name": self.target_player_name
        }

    def get_description(self) -> str:
        return f"Allow '{self.target_player_name}' to load metal from your worlds"


class DeclareNonLoaderCommand(Command):
    """Revoke player's ability to load metal (X=xxxxxx)."""

    def __init__(self, player, target_player_name: str):
        super().__init__(player)
        self.target_player_name = target_player_name

    def validate(self, game_state) -> tuple[bool, str]:
        # Check target player exists
        target_player = None
        for p in game_state.players.values():
            if p.name == self.target_player_name:
                target_player = p
                break

        if not target_player:
            return False, f"Player '{self.target_player_name}' not found"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "DECLARE_NON_LOADER",
            "player": self.player,
            "target_player_name": self.target_player_name
        }

    def get_description(self) -> str:
        return f"Revoke '{self.target_player_name}' loader status"


class DeclareJihadCommand(Command):
    """Declare Jihad against another player (J=xxxxxx) - Apostle only."""

    def __init__(self, player, target_player_name: str):
        super().__init__(player)
        self.target_player_name = target_player_name

    def validate(self, game_state) -> tuple[bool, str]:
        # Only Apostle can declare Jihad
        valid, msg = validate_character_type(self.player, "Apostle")
        if not valid:
            return valid, msg

        # Check target player exists
        target_player = None
        for p in game_state.players.values():
            if p.name == self.target_player_name:
                target_player = p
                break

        if not target_player:
            return False, f"Player '{self.target_player_name}' not found"

        if target_player == self.player:
            return False, "Cannot declare Jihad against yourself"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "DECLARE_JIHAD",
            "player": self.player,
            "target_player_name": self.target_player_name
        }

    def get_description(self) -> str:
        return f"Declare Jihad against '{self.target_player_name}'"


class ConditionalFireCommand(Command):
    """Conditional fire - fires only if attacked (FnnnCFmmm, etc.)."""

    def __init__(self, player, fleet_id: int, target_type: str, target_id: Optional[int] = None):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.target_type = target_type  # "FLEET", "ISHIPS", "PSHIPS", etc.
        self.target_id = target_id  # Fleet ID if targeting fleet

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet has ships
        valid, msg, fleet = validate_fleet_has_ships(game_state, self.player, self.fleet_id)
        if not valid:
            return valid, msg

        # If firing at a fleet, validate target
        if self.target_type == "FLEET" and self.target_id:
            # Check not own fleet
            valid, msg = validate_not_own_fleet(game_state, self.player, self.target_id)
            if not valid:
                return valid, msg

            # Check at same world
            valid, msg = validate_fleet_at_same_world(game_state, self.fleet_id, self.target_id)
            if not valid:
                return False, "Target fleet must be at same world"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "CONDITIONAL_FIRE",
            "player": self.player,
            "fleet_id": self.fleet_id,
            "target_type": self.target_type,
            "target_id": self.target_id
        }

    def get_description(self) -> str:
        if self.target_type == "FLEET":
            return f"F{self.fleet_id} Conditional Fire at F{self.target_id}"
        else:
            return f"F{self.fleet_id} Conditional Fire at {self.target_type}"


class NoAmbushCommand(Command):
    """Set no ambush (Z or Z#) - don't ambush anyone or at specific world."""

    def __init__(self, player, world_id: Optional[int] = None):
        super().__init__(player)
        self.world_id = world_id  # None means no ambush anywhere

    def validate(self, game_state) -> tuple[bool, str]:
        # If world specified, validate it exists
        if self.world_id is not None:
            world = game_state.get_world(self.world_id)
            if not world:
                return False, f"World {self.world_id} does not exist"

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "NO_AMBUSH",
            "player": self.player,
            "world_id": self.world_id
        }

    def get_description(self) -> str:
        if self.world_id:
            return f"Don't ambush at W{self.world_id}"
        else:
            return "Don't ambush anyone, anywhere this turn"


class AtPeaceCommand(Command):
    """Put fleet at peace (FnnnQ) - fleet won't participate in combat."""

    def __init__(self, player, fleet_id: int):
        super().__init__(player)
        self.fleet_id = fleet_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership
        valid, msg, _ = validate_fleet_ownership(game_state, self.player, self.fleet_id)
        return valid, msg

    def to_order(self) -> dict:
        return {
            "type": "AT_PEACE",
            "player": self.player,
            "fleet_id": self.fleet_id
        }

    def get_description(self) -> str:
        return f"F{self.fleet_id} at peace (won't participate in combat)"


class NotAtPeaceCommand(Command):
    """Put fleet not at peace (FnnnX) - fleet will participate in combat."""

    def __init__(self, player, fleet_id: int):
        super().__init__(player)
        self.fleet_id = fleet_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Validate fleet ownership
        valid, msg, _ = validate_fleet_ownership(game_state, self.player, self.fleet_id)
        return valid, msg

    def to_order(self) -> dict:
        return {
            "type": "NOT_AT_PEACE",
            "player": self.player,
            "fleet_id": self.fleet_id
        }

    def get_description(self) -> str:
        return f"F{self.fleet_id} not at peace (will participate in combat)"


class MigrateConvertsCommand(Command):
    """Migrate converts to another world (C#M#W#) - Apostle only."""

    def __init__(self, player, source_world_id: int, amount: int, target_world_id: int):
        super().__init__(player)
        self.source_world_id = source_world_id
        self.amount = amount
        self.target_world_id = target_world_id

    def validate(self, game_state) -> tuple[bool, str]:
        # Only Apostle can migrate converts
        valid, msg = validate_character_type(self.player, "Apostle")
        if not valid:
            return valid, msg

        # Validate source world ownership
        valid, msg, source_world = validate_world_ownership(game_state, self.player, self.source_world_id)
        if not valid:
            return valid, msg

        if self.amount <= 0:
            return False, "Migration amount must be positive"

        # Check source has enough converts
        # Note: converts would be tracked separately from population in a full implementation
        # For now, we'll validate against population as a placeholder
        if source_world.population < self.amount:
            return False, f"World {self.source_world_id} only has {source_world.population} population"

        # Validate target world exists and is connected
        valid, msg = validate_world_connected(game_state, self.source_world_id, self.target_world_id)
        if not valid:
            return valid, msg

        return True, ""

    def to_order(self) -> dict:
        return {
            "type": "MIGRATE_CONVERTS",
            "player": self.player,
            "source_world_id": self.source_world_id,
            "amount": self.amount,
            "target_world_id": self.target_world_id
        }

    def get_description(self) -> str:
        return f"Migrate {self.amount} converts from W{self.source_world_id} to W{self.target_world_id}"


# Exclusive order types that cannot coexist for same fleet
EXCLUSIVE_ORDER_TYPES = {"MOVE", "FIRE", "AMBUSH", "CONDITIONAL_FIRE"}


def has_exclusive_order(player, fleet_id: int) -> bool:
    """Check if player already has an exclusive order for this fleet."""
    return any(
        o.get("fleet_id") == fleet_id and o.get("type") in EXCLUSIVE_ORDER_TYPES
        for o in player.orders
    )


def parse_command(player, command_text: str, game_state) -> Optional[Command]:
    """
    Parse command text into Command object using the parser registry.

    Returns:
        Command object or None if invalid syntax
    """
    from .command_parser_registry import get_command_parser

    if not command_text or not command_text.strip():
        return None

    # Use the registry-based parser
    parser = get_command_parser()
    return parser.parse(player, command_text.strip())
