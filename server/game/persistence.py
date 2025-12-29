"""
Game state persistence system.
Saves and loads game state to/from disk.
"""
import json
import logging
import os
from pathlib import Path
from typing import Optional
import pickle

logger = logging.getLogger(__name__)


class GameStatePersistence:
    """
    Handles saving and loading game state to/from disk.
    """

    def __init__(self, save_file: str = "data/gamestate.json"):
        self.save_file = Path(save_file)
        self.save_file.parent.mkdir(parents=True, exist_ok=True)

    def save_state(self, game_state) -> bool:
        """
        Save game state to disk.

        Args:
            game_state: GameState object to save

        Returns:
            True if successful, False otherwise
        """
        try:
            # Build state dict
            state_data = {
                "version": "2.0",
                "game_turn": game_state.game_turn,
                "map_size": game_state.map_size,
                "turn_end_time": game_state.turn_end_time,
                "current_turn_duration": game_state.current_turn_duration,
                "next_player_id": game_state.next_player_id,

                # Worlds
                "worlds": {},

                # Fleets
                "fleets": {},

                # Artifacts
                "artifacts": {},

                # Players (persistent data only)
                "players": {}
            }

            # Serialize worlds
            for world_id, world in game_state.worlds.items():
                state_data["worlds"][world_id] = {
                    "id": world.id,
                    "connections": world.connections,
                    "owner_name": world.owner.name if world.owner else None,
                    "industry": world.industry,
                    "metal": world.metal,
                    "mines": world.mines,
                    "population": world.population,
                    "limit": world.limit,
                    "iships": world.iships,
                    "pships": world.pships,
                    "key": world.key,
                    "population_type": world.population_type,
                    "plundered": world.plundered,
                    "planet_buster": world.planet_buster,
                    "artifact_ids": [a.id for a in world.artifacts]
                }

            # Serialize fleets
            for fleet_id, fleet in game_state.fleets.items():
                state_data["fleets"][fleet_id] = {
                    "id": fleet.id,
                    "owner_name": fleet.owner.name if fleet.owner else None,
                    "world_id": fleet.world.id,
                    "ships": fleet.ships,
                    "cargo": fleet.cargo,
                    "moved": fleet.moved,
                    "is_ambushing": fleet.is_ambushing,
                    "has_pbb": fleet.has_pbb,
                    "artifact_ids": [a.id for a in fleet.artifacts]
                }

            # Serialize artifacts
            for artifact_id, artifact in game_state.artifacts.items():
                state_data["artifacts"][artifact_id] = {
                    "id": artifact.id,
                    "name": artifact.name
                }

            # Serialize players (only persistent data, not websocket)
            for ws, player in game_state.players.items():
                if player.name and not player.name.startswith("Player_"):
                    state_data["players"][player.name] = {
                        "id": player.id,
                        "name": player.name,
                        "character_type": player.character_type,
                        "score": player.score,
                        "turn_timer_minutes": player.turn_timer_minutes,
                        "known_worlds": player.known_worlds,
                        "fleet_ids": [f.id for f in player.fleets],
                        "world_ids": [w.id for w in player.worlds]
                    }

            # Write to file (with backup)
            if self.save_file.exists():
                backup = self.save_file.with_suffix('.json.bak')
                self.save_file.rename(backup)

            with open(self.save_file, 'w') as f:
                json.dump(state_data, f, indent=2)

            logger.info(f"Game state saved to {self.save_file}")
            return True

        except Exception as e:
            logger.error(f"Failed to save game state: {e}", exc_info=True)
            return False

    def load_state(self, game_state) -> bool:
        """
        Load game state from disk.

        Args:
            game_state: GameState object to populate

        Returns:
            True if successful, False otherwise
        """
        if not self.save_file.exists():
            logger.info(f"No saved game state found at {self.save_file}")
            return False

        try:
            with open(self.save_file, 'r') as f:
                state_data = json.load(f)

            logger.info(f"Loading game state version {state_data.get('version', 'unknown')}")

            # Restore basic state
            game_state.game_turn = state_data.get("game_turn", 0)
            game_state.map_size = state_data.get("map_size", 255)
            game_state.turn_end_time = state_data.get("turn_end_time", 0)
            game_state.current_turn_duration = state_data.get("current_turn_duration", 180)
            game_state.next_player_id = state_data.get("next_player_id", 1)

            # Restore artifacts first
            from .entities import Artifact
            game_state.artifacts.clear()
            for artifact_id, artifact_data in state_data.get("artifacts", {}).items():
                artifact = Artifact(
                    int(artifact_id),
                    artifact_data["name"]
                )
                game_state.artifacts[int(artifact_id)] = artifact

            # Restore worlds (without owner/fleets references yet)
            from .entities import World
            game_state.worlds.clear()
            for world_id, world_data in state_data.get("worlds", {}).items():
                world = World(int(world_id))
                world.connections = world_data["connections"]
                world.industry = world_data["industry"]
                world.metal = world_data["metal"]
                world.mines = world_data["mines"]
                world.population = world_data["population"]
                world.limit = world_data["limit"]
                world.iships = world_data["iships"]
                world.pships = world_data["pships"]
                world.key = world_data.get("key", False)
                world.population_type = world_data.get("population_type", "human")
                world.plundered = world_data.get("plundered", False)
                world.planet_buster = world_data.get("planet_buster", False)
                # Artifacts will be attached later
                game_state.worlds[int(world_id)] = world

            # Restore fleets (without owner/world references yet)
            from .entities import Fleet
            game_state.fleets.clear()
            fleet_data_map = {}
            for fleet_id, fleet_data in state_data.get("fleets", {}).items():
                # Store for later processing
                fleet_data_map[int(fleet_id)] = fleet_data

            # Restore players (persistent data only, no websocket)
            # Store player data for reconnection
            game_state._persistent_players = {}
            for player_name, player_data in state_data.get("players", {}).items():
                game_state._persistent_players[player_name] = player_data

            # Now create fleets with world references
            for fleet_id, fleet_data in fleet_data_map.items():
                world = game_state.worlds[fleet_data["world_id"]]
                fleet = Fleet(fleet_id, None, world)  # owner will be set later
                fleet.ships = fleet_data["ships"]
                fleet.cargo = fleet_data["cargo"]
                fleet.moved = fleet_data["moved"]
                fleet.is_ambushing = fleet_data["is_ambushing"]
                fleet.has_pbb = fleet_data.get("has_pbb", False)
                game_state.fleets[fleet_id] = fleet

            # Attach artifacts to worlds/fleets
            for world_id, world_data in state_data.get("worlds", {}).items():
                world = game_state.worlds[int(world_id)]
                for artifact_id in world_data.get("artifact_ids", []):
                    if artifact_id in game_state.artifacts:
                        world.artifacts.append(game_state.artifacts[artifact_id])

            for fleet_id, fleet_data in fleet_data_map.items():
                fleet = game_state.fleets[fleet_id]
                for artifact_id in fleet_data.get("artifact_ids", []):
                    if artifact_id in game_state.artifacts:
                        fleet.artifacts.append(game_state.artifacts[artifact_id])

            logger.info(f"Game state loaded: Turn {game_state.game_turn}, {len(game_state._persistent_players)} players, {len(game_state.worlds)} worlds, {len(game_state.fleets)} fleets")
            return True

        except Exception as e:
            logger.error(f"Failed to load game state: {e}", exc_info=True)
            return False


# Global persistence instance
_persistence = None


def get_persistence() -> GameStatePersistence:
    """Get the global persistence instance."""
    global _persistence
    if _persistence is None:
        _persistence = GameStatePersistence()
    return _persistence
