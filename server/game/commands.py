"""
Command pattern for game actions.
All player commands go through validation and execution.
"""
from abc import ABC, abstractmethod
from typing import Optional, List


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
        fleet = game_state.get_fleet(self.fleet_id)

        if not fleet:
            return False, f"Fleet {self.fleet_id} does not exist"

        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.fleet_id}"

        if fleet.ships == 0:
            return False, f"Fleet {self.fleet_id} has no ships"

        # Validate path connectivity
        current = fleet.world.id
        for next_world_id in self.path:
            world = game_state.get_world(current)
            if next_world_id not in world.connections:
                return False, f"World {current} is not connected to {next_world_id}"
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
        world = game_state.get_world(self.world_id)

        if not world:
            return False, f"World {self.world_id} does not exist"

        if world.owner != self.player:
            return False, f"You do not own world {self.world_id}"

        if self.amount <= 0:
            return False, "Build amount must be positive"

        max_build = min(world.industry, world.metal, world.population)
        if self.amount > max_build:
            return False, f"Cannot build {self.amount}, maximum is {max_build}"

        if self.target_type == "F" and self.target_id:
            fleet = game_state.get_fleet(self.target_id)
            if not fleet:
                return False, f"Fleet {self.target_id} does not exist"
            if fleet.owner != self.player:
                return False, f"You do not own fleet {self.target_id}"
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
        fleet = game_state.get_fleet(self.fleet_id)

        if not fleet:
            return False, f"Fleet {self.fleet_id} does not exist"

        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.fleet_id}"

        if fleet.ships < self.amount:
            return False, f"Fleet {self.fleet_id} only has {fleet.ships} ships"

        world = fleet.world
        if self.target_type in ["I", "P"] and world.owner != self.player:
            return False, "Cannot transfer to garrison of world you don't own"

        if self.target_type == "F" and self.target_id:
            target_fleet = game_state.get_fleet(self.target_id)
            if not target_fleet:
                return False, f"Target fleet {self.target_id} does not exist"
            if target_fleet.world.id != world.id:
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
        world = game_state.get_world(self.world_id)

        if not world:
            return False, f"World {self.world_id} does not exist"

        if world.owner != self.player:
            return False, f"You do not own world {self.world_id}"

        # Check source has enough ships
        if self.source_type == "I":
            if world.iships < self.amount:
                return False, f"World {self.world_id} only has {world.iships} ISHIPS"
        elif self.source_type == "P":
            if world.pships < self.amount:
                return False, f"World {self.world_id} only has {world.pships} PSHIPS"

        # Validate target
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
            source = game_state.get_fleet(self.source_id)
            if not source:
                return False, f"Fleet {self.source_id} does not exist"
            if source.owner != self.player:
                return False, f"You do not own fleet {self.source_id}"
            source_world = source.world
        elif self.source_type == "W":
            source = game_state.get_world(self.source_id)
            if not source:
                return False, f"World {self.source_id} does not exist"
            if source.owner != self.player:
                return False, f"You do not own world {self.source_id}"
            source_world = source
        else:
            return False, "Invalid source type"

        # Check artifact exists in source
        artifact = None
        for a in source.artifacts:
            if a.id == self.artifact_id:
                artifact = a
                break

        if not artifact:
            return False, f"Artifact {self.artifact_id} not found in source"

        # Validate target
        if self.target_type == "F":
            if not self.target_id:
                return False, "Target fleet ID required"
            target = game_state.get_fleet(self.target_id)
            if not target:
                return False, f"Target fleet {self.target_id} does not exist"
            if target.owner != self.player:
                return False, f"You do not own target fleet {self.target_id}"
            # Fleets must be at same world
            if target.world.id != source_world.id:
                return False, "Source and target must be at same world"
        elif self.target_type == "W":
            # Transfer to world garrison at source location
            target = source_world
            if target.owner != self.player:
                return False, f"You do not own world {target.id}"
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
    """Fire at fleet or world."""

    def __init__(self, player, fleet_id: int, target_type: str, target_id: Optional[int] = None, sub_target: Optional[str] = None):
        super().__init__(player)
        self.fleet_id = fleet_id
        self.target_type = target_type  # "WORLD" or "FLEET"
        self.target_id = target_id  # Fleet ID if targeting fleet
        self.sub_target = sub_target  # "P" or "I" if targeting world

    def validate(self, game_state) -> tuple[bool, str]:
        fleet = game_state.get_fleet(self.fleet_id)

        if not fleet:
            return False, f"Fleet {self.fleet_id} does not exist"

        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.fleet_id}"

        if fleet.ships == 0:
            return False, f"Fleet {self.fleet_id} has no ships"

        if self.target_type == "FLEET" and self.target_id:
            target = game_state.get_fleet(self.target_id)
            if not target:
                return False, f"Target fleet {self.target_id} does not exist"
            if target.world != fleet.world:
                return False, "Target fleet must be at same world"

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
        else:
            return f"F{self.fleet_id} Fire at World {self.sub_target}"


class AmbushCommand(Command):
    """Set fleet to ambush mode."""

    def __init__(self, player, fleet_id: int):
        super().__init__(player)
        self.fleet_id = fleet_id

    def validate(self, game_state) -> tuple[bool, str]:
        fleet = game_state.get_fleet(self.fleet_id)

        if not fleet:
            return False, f"Fleet {self.fleet_id} does not exist"

        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.fleet_id}"

        return True, ""

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
        world = game_state.get_world(self.world_id)

        if not world:
            return False, f"World {self.world_id} does not exist"

        if world.owner != self.player:
            return False, f"You do not own world {self.world_id}"

        # Check we have defense ships
        if self.defense_type == "I":
            if world.iships == 0:
                return False, f"World {self.world_id} has no ISHIPS"
        elif self.defense_type == "P":
            if world.pships == 0:
                return False, f"World {self.world_id} has no PSHIPS"

        # Validate target
        if self.target_type == "F" and self.target_id:
            target = game_state.get_fleet(self.target_id)
            if not target:
                return False, f"Target fleet {self.target_id} does not exist"
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
            # Fleet probe
            fleet = game_state.get_fleet(self.source_id)
            if not fleet:
                return False, f"Fleet {self.source_id} does not exist"
            if fleet.owner != self.player:
                return False, f"You do not own fleet {self.source_id}"
            if fleet.ships < 1:
                return False, f"Fleet {self.source_id} has no ships"

            # Check target is adjacent
            current_world = fleet.world
            if self.target_world not in current_world.connections:
                return False, f"World {self.target_world} is not adjacent to {current_world.id}"

        else:
            # Defense probe (I or P)
            world = game_state.get_world(self.source_id)
            if not world:
                return False, f"World {self.source_id} does not exist"
            if world.owner != self.player:
                return False, f"You do not own world {self.source_id}"

            # Check we have defense ships
            if self.source_type == "I":
                if world.iships < 1:
                    return False, f"World {self.source_id} has no ISHIPS"
            elif self.source_type == "P":
                if world.pships < 1:
                    return False, f"World {self.source_id} has no PSHIPS"

            # Check target is adjacent
            if self.target_world not in world.connections:
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
        from ..config import get_config
        config = get_config()

        world = game_state.get_world(self.world_id)
        if not world:
            return False, f"World {self.world_id} does not exist"
        if world.owner != self.player:
            return False, f"You do not own world {self.world_id}"

        # Check if player is empire builder (gets bonus)
        is_empire_builder = self.player.character_type == "Empire Builder"
        ships_per_industry = 4 if is_empire_builder else 6

        # Check we have enough ISHIPS to scrap
        ships_needed = self.amount * ships_per_industry
        if world.iships < ships_needed:
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
        fleet = game_state.get_fleet(self.fleet_id)
        if not fleet:
            return False, f"Fleet {self.fleet_id} does not exist"
        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.fleet_id}"
        if fleet.cargo == 0:
            return False, f"Fleet {self.fleet_id} has no cargo"

        if self.amount and self.amount > fleet.cargo:
            return False, f"Fleet {self.fleet_id} only has {fleet.cargo} cargo"

        return True, ""

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
        fleet = game_state.get_fleet(self.fleet_id)
        if not fleet:
            return False, f"Fleet {self.fleet_id} does not exist"
        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.fleet_id}"
        if fleet.cargo == 0:
            return False, f"Fleet {self.fleet_id} has no cargo"

        if self.amount and self.amount > fleet.cargo:
            return False, f"Fleet {self.fleet_id} only has {fleet.cargo} cargo"

        # Must be Merchant to use consumer goods
        if self.player.character_type != "Merchant":
            return False, "Only Merchants can deliver consumer goods"

        return True, ""

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
        fleet = game_state.get_fleet(self.fleet_id)

        if not fleet:
            return False, f"Fleet {self.fleet_id} does not exist"

        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.fleet_id}"

        world = fleet.world
        if world.owner != self.player:
            return False, "Cannot load from world you don't own"

        if world.population == 0:
            return False, f"World {world.id} has no population to load"

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
        fleet = game_state.get_fleet(self.fleet_id)

        if not fleet:
            return False, f"Fleet {self.fleet_id} does not exist"

        if fleet.owner != self.player:
            return False, f"You do not own fleet {self.fleet_id}"

        world = fleet.world
        if world.owner != self.player:
            return False, "Cannot unload to world you don't own"

        if fleet.cargo == 0:
            return False, f"Fleet {self.fleet_id} has no cargo to unload"

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


# Exclusive order types that cannot coexist for same fleet
EXCLUSIVE_ORDER_TYPES = {"MOVE", "FIRE", "AMBUSH"}


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
