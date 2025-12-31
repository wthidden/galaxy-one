"""
Command parser registry - data-driven command parsing.
Each command type registers its own parser function.
"""
import re
from typing import Callable, Optional, List
from .commands import (
    Command,
    MoveFleetCommand,
    BuildCommand,
    TransferCommand,
    TransferFromDefenseCommand,
    TransferArtifactCommand,
    LoadCommand,
    UnloadCommand,
    FireCommand,
    DefenseFireCommand,
    AmbushCommand,
    ProbeCommand,
    ScrapShipsCommand,
    JettisonCommand,
    UnloadConsumerGoodsCommand,
    ViewArtifactCommand,
    DeclareRelationCommand,
    PlunderCommand,
    RobotAttackCommand
)


class CommandParserRegistry:
    """Registry for command parsers."""

    def __init__(self):
        self._parsers: List[tuple[re.Pattern, Callable]] = []

    def register(self, pattern: str):
        """
        Decorator to register a command parser.

        Args:
            pattern: Regex pattern to match command
        """
        def decorator(func: Callable):
            compiled_pattern = re.compile(pattern, re.IGNORECASE)
            self._parsers.append((compiled_pattern, func))
            return func
        return decorator

    def parse(self, player, command_text: str) -> Optional[Command]:
        """
        Parse command text using registered parsers.

        Args:
            player: The player issuing the command
            command_text: The command text

        Returns:
            Command object or None if no parser matches
        """
        for pattern, parser_func in self._parsers:
            match = pattern.match(command_text)
            if match:
                return parser_func(player, command_text, match)

        return None


# Global registry instance
_registry = CommandParserRegistry()


# Register parsers for each command type
@_registry.register(r"^F(\d+)(W\d+)+$")
def parse_move(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5W10 or F5W1W3W10"""
    fleet_id = int(match.group(1))
    path = [int(x) for x in command_text[len(f"F{fleet_id}"):].split("W") if x]
    return MoveFleetCommand(player, fleet_id, path)


@_registry.register(r"^W(\d+)B(\d+)(F(\d+)|I|P|IND|INDUSTRY|L|LIMIT|R|ROBOT)$")
def parse_build(player, command_text: str, match: re.Match) -> Command:
    """Parse: W3B25I, W3B10P, W3B15F7, W3B2INDUSTRY, W3B5LIMIT, W3B10ROBOT"""
    world_id = int(match.group(1))
    amount = int(match.group(2))
    target_type = match.group(3).upper()

    # Handle different build types
    if target_type.startswith("F"):
        target_id = int(match.group(4))
        return BuildCommand(player, world_id, amount, "F", target_id)
    elif target_type in ["I", "P"]:
        return BuildCommand(player, world_id, amount, target_type)
    elif target_type in ["IND", "INDUSTRY"]:
        return BuildCommand(player, world_id, amount, "INDUSTRY")
    elif target_type in ["L", "LIMIT"]:
        return BuildCommand(player, world_id, amount, "LIMIT")
    elif target_type in ["R", "ROBOT"]:
        return BuildCommand(player, world_id, amount, "ROBOT")


@_registry.register(r"^F(\d+)T(\d+)(F(\d+)|I|P)$")
def parse_transfer(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5T10I, F5T10P, F5T10F7"""
    fleet_id = int(match.group(1))
    amount = int(match.group(2))
    target_type = match.group(3)
    target_id = int(match.group(4)) if target_type.startswith("F") else None
    return TransferCommand(player, fleet_id, amount, target_type[0], target_id)


@_registry.register(r"^([IP])(\d+)T(\d+)(F(\d+)|I|P)$")
def parse_transfer_from_defense(player, command_text: str, match: re.Match) -> Command:
    """Parse: I5T10F7, P5T10F7, I5T10P, P5T10I"""
    source_type = match.group(1)  # "I" or "P"
    world_id = int(match.group(2))
    amount = int(match.group(3))
    target_type = match.group(4)
    target_id = int(match.group(5)) if target_type.startswith("F") else None
    return TransferFromDefenseCommand(player, world_id, amount, source_type, target_type[0], target_id)


@_registry.register(r"^F(\d+)TA(\d+)F(\d+)$")
def parse_transfer_artifact_fleet_to_fleet(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5TA3F7 - Transfer artifact 3 from fleet 5 to fleet 7"""
    fleet_id = int(match.group(1))
    artifact_id = int(match.group(2))
    target_id = int(match.group(3))
    return TransferArtifactCommand(player, "F", fleet_id, artifact_id, "F", target_id)


@_registry.register(r"^F(\d+)TA(\d+)W$")
def parse_transfer_artifact_fleet_to_world(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5TA3W - Transfer artifact 3 from fleet 5 to world"""
    fleet_id = int(match.group(1))
    artifact_id = int(match.group(2))
    return TransferArtifactCommand(player, "F", fleet_id, artifact_id, "W", None)


@_registry.register(r"^W(\d+)TA(\d+)F(\d+)$")
def parse_transfer_artifact_world_to_fleet(player, command_text: str, match: re.Match) -> Command:
    """Parse: W5TA3F7 - Transfer artifact 3 from world 5 to fleet 7"""
    world_id = int(match.group(1))
    artifact_id = int(match.group(2))
    target_id = int(match.group(3))
    return TransferArtifactCommand(player, "W", world_id, artifact_id, "F", target_id)


@_registry.register(r"^F(\d+)L(\d+)?$")
def parse_load(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5L or F5L10"""
    fleet_id = int(match.group(1))
    amount = int(match.group(2)) if match.group(2) else None
    return LoadCommand(player, fleet_id, amount)


@_registry.register(r"^F(\d+)U(\d+)?$")
def parse_unload(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5U or F5U10"""
    fleet_id = int(match.group(1))
    amount = int(match.group(2)) if match.group(2) else None
    return UnloadCommand(player, fleet_id, amount)


@_registry.register(r"^F(\d+)AF(\d+)$")
def parse_fire_fleet(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5AF10"""
    fleet_id = int(match.group(1))
    target_id = int(match.group(2))
    return FireCommand(player, fleet_id, "FLEET", target_id)


@_registry.register(r"^F(\d+)A(P|I|H)$")
def parse_fire_world(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5AP, F5AI, F5AH"""
    fleet_id = int(match.group(1))
    sub_target = match.group(2)
    return FireCommand(player, fleet_id, "WORLD", sub_target=sub_target)


@_registry.register(r"^([IP])(\d+)AF(\d+)$")
def parse_defense_fire_fleet(player, command_text: str, match: re.Match) -> Command:
    """Parse: I5AF10, P5AF10"""
    defense_type = match.group(1)
    world_id = int(match.group(2))
    target_id = int(match.group(3))
    return DefenseFireCommand(player, world_id, defense_type, "F", target_id)


@_registry.register(r"^([IP])(\d+)AC$")
def parse_defense_fire_converts(player, command_text: str, match: re.Match) -> Command:
    """Parse: I5AC, P5AC"""
    defense_type = match.group(1)
    world_id = int(match.group(2))
    return DefenseFireCommand(player, world_id, defense_type, "C")


@_registry.register(r"^F(\d+)A$")
def parse_ambush(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5A"""
    fleet_id = int(match.group(1))
    return AmbushCommand(player, fleet_id)


@_registry.register(r"^W(\d+)M(\d+)W(\d+)$")
def parse_migrate(player, command_text: str, match: re.Match) -> Command:
    """Parse: W3M5W10"""
    from .commands import MigrateCommand
    world_id = int(match.group(1))
    amount = int(match.group(2))
    dest_world = int(match.group(3))
    return MigrateCommand(player, world_id, amount, dest_world)


@_registry.register(r"^F(\d+)P(\d+)$")
def parse_fleet_probe(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5P10"""
    fleet_id = int(match.group(1))
    target_world = int(match.group(2))
    return ProbeCommand(player, "F", fleet_id, target_world)


@_registry.register(r"^([IP])(\d+)P(\d+)$")
def parse_defense_probe(player, command_text: str, match: re.Match) -> Command:
    """Parse: I5P10, P5P10"""
    defense_type = match.group(1)
    world_id = int(match.group(2))
    target_world = int(match.group(3))
    return ProbeCommand(player, defense_type, world_id, target_world)


@_registry.register(r"^W(\d+)S(\d+)$")
def parse_scrap_ships(player, command_text: str, match: re.Match) -> Command:
    """Parse: W5S3 - Scrap ships to make 3 industry"""
    world_id = int(match.group(1))
    amount = int(match.group(2))
    return ScrapShipsCommand(player, world_id, amount)


@_registry.register(r"^F(\d+)J(\d+)?$")
def parse_jettison(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5J or F5J10"""
    fleet_id = int(match.group(1))
    amount = int(match.group(2)) if match.group(2) else None
    return JettisonCommand(player, fleet_id, amount)


@_registry.register(r"^F(\d+)N(\d+)?$")
def parse_consumer_goods(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5N or F5N10"""
    fleet_id = int(match.group(1))
    amount = int(match.group(2)) if match.group(2) else None
    return UnloadConsumerGoodsCommand(player, fleet_id, amount)


@_registry.register(r"^F(\d+)R(\d+)$")
def parse_robot_attack(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5R3 - Fleet 5 convert 3 ships to 6 robots (Berserker only)"""
    fleet_id = int(match.group(1))
    num_ships = int(match.group(2))
    return RobotAttackCommand(player, fleet_id, num_ships)


@_registry.register(r"^V(\d+)F(\d+)$")
def parse_view_artifact_fleet(player, command_text: str, match: re.Match) -> Command:
    """Parse: V3F5 - View artifact 3 on fleet 5"""
    artifact_id = int(match.group(1))
    fleet_id = int(match.group(2))
    return ViewArtifactCommand(player, artifact_id, "F", fleet_id)


@_registry.register(r"^V(\d+)W$")
def parse_view_artifact_world(player, command_text: str, match: re.Match) -> Command:
    """Parse: V3W - View artifact 3 on world"""
    artifact_id = int(match.group(1))
    return ViewArtifactCommand(player, artifact_id, "W")


@_registry.register(r"^V(\d+)$")
def parse_view_artifact(player, command_text: str, match: re.Match) -> Command:
    """Parse: V3 - View artifact 3 (search player's possession)"""
    artifact_id = int(match.group(1))
    return ViewArtifactCommand(player, artifact_id)


@_registry.register(r"^F(\d+)Q(\d+)$")
def parse_declare_peace(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5Q10 - Fleet 5 declares peace with fleet 10"""
    fleet_id = int(match.group(1))
    target_fleet_id = int(match.group(2))
    return DeclareRelationCommand(player, fleet_id, target_fleet_id, "PEACE")


@_registry.register(r"^F(\d+)X(\d+)$")
def parse_declare_war(player, command_text: str, match: re.Match) -> Command:
    """Parse: F5X10 - Fleet 5 declares war with fleet 10"""
    fleet_id = int(match.group(1))
    target_fleet_id = int(match.group(2))
    return DeclareRelationCommand(player, fleet_id, target_fleet_id, "WAR")


@_registry.register(r"^W(\d+)X$")
def parse_plunder(player, command_text: str, match: re.Match) -> Command:
    """Parse: W5X - Plunder world 5"""
    world_id = int(match.group(1))
    return PlunderCommand(player, world_id)


def get_command_parser():
    """Get the global command parser registry."""
    return _registry
