"""
Event type definitions for the StarWeb game.
All game events that can be published through the event bus.
"""
from dataclasses import dataclass
from typing import Any, Optional


@dataclass
class GameEvent:
    """Base class for all game events."""
    type: str
    game_turn: int
    timestamp: float = 0.0

    def to_dict(self):
        """Convert event to dictionary for serialization."""
        return {
            "type": self.type,
            "game_turn": self.game_turn,
            "timestamp": self.timestamp
        }


class FleetMovedEvent(GameEvent):
    """Fired when a fleet moves between worlds."""

    def __init__(self, fleet_id, owner_id, owner_name, from_world, to_world, path, ships, game_turn, timestamp=0.0):
        super().__init__("FLEET_MOVED", game_turn, timestamp)
        self.fleet_id = fleet_id
        self.owner_id = owner_id
        self.owner_name = owner_name
        self.from_world = from_world
        self.to_world = to_world
        self.path = path
        self.ships = ships

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "fleet_id": self.fleet_id,
            "owner_id": self.owner_id,
            "owner_name": self.owner_name,
            "from_world": self.from_world,
            "to_world": self.to_world,
            "path": self.path,
            "ships": self.ships
        })
        return data


class CombatEvent(GameEvent):
    """Fired when combat occurs."""

    def __init__(self, world_id, attacker_id, defender_id, attacker_losses, defender_losses, combat_type, game_turn, timestamp=0.0):
        super().__init__("COMBAT", game_turn, timestamp)
        self.world_id = world_id
        self.attacker_id = attacker_id
        self.defender_id = defender_id
        self.attacker_losses = attacker_losses
        self.defender_losses = defender_losses
        self.combat_type = combat_type

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "world_id": self.world_id,
            "attacker_id": self.attacker_id,
            "defender_id": self.defender_id,
            "attacker_losses": self.attacker_losses,
            "defender_losses": self.defender_losses,
            "combat_type": self.combat_type
        })
        return data


class WorldCapturedEvent(GameEvent):
    """Fired when a world changes ownership."""

    def __init__(self, world_id, old_owner_id, new_owner_id, new_owner_name, game_turn, timestamp=0.0):
        super().__init__("WORLD_CAPTURED", game_turn, timestamp)
        self.world_id = world_id
        self.old_owner_id = old_owner_id
        self.new_owner_id = new_owner_id
        self.new_owner_name = new_owner_name

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "world_id": self.world_id,
            "old_owner_id": self.old_owner_id,
            "new_owner_id": self.new_owner_id,
            "new_owner_name": self.new_owner_name
        })
        return data


class ProductionEvent(GameEvent):
    """Fired when production occurs on a world."""

    def __init__(self, world_id, owner_id, metal_produced, population_growth, game_turn, timestamp=0.0):
        super().__init__("PRODUCTION", game_turn, timestamp)
        self.world_id = world_id
        self.owner_id = owner_id
        self.metal_produced = metal_produced
        self.population_growth = population_growth

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "world_id": self.world_id,
            "owner_id": self.owner_id,
            "metal_produced": self.metal_produced,
            "population_growth": self.population_growth
        })
        return data


class BuildEvent(GameEvent):
    """Fired when ships are built."""

    def __init__(self, world_id, owner_id, target_type, target_id, amount, game_turn, timestamp=0.0):
        super().__init__("BUILD", game_turn, timestamp)
        self.world_id = world_id
        self.owner_id = owner_id
        self.target_type = target_type
        self.target_id = target_id
        self.amount = amount

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "world_id": self.world_id,
            "owner_id": self.owner_id,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "amount": self.amount
        })
        return data


class PlayerJoinedEvent(GameEvent):
    """Fired when a player joins the game."""

    def __init__(self, player_id, player_name, character_type, homeworld_id, game_turn, timestamp=0.0):
        super().__init__("PLAYER_JOINED", game_turn, timestamp)
        self.player_id = player_id
        self.player_name = player_name
        self.character_type = character_type
        self.homeworld_id = homeworld_id

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "player_id": self.player_id,
            "player_name": self.player_name,
            "character_type": self.character_type,
            "homeworld_id": self.homeworld_id
        })
        return data


class TurnProcessedEvent(GameEvent):
    """Fired when a turn is processed."""

    def __init__(self, turn_duration, players_ready, total_players, game_turn, timestamp=0.0):
        super().__init__("TURN_PROCESSED", game_turn, timestamp)
        self.turn_duration = turn_duration
        self.players_ready = players_ready
        self.total_players = total_players

    def to_dict(self):
        data = super().to_dict()
        data.update({
            "turn_duration": self.turn_duration,
            "players_ready": self.players_ready,
            "total_players": self.total_players
        })
        return data
