"""
Central game state management.
"""
import random
import logging
from typing import Dict, Optional
from .entities import World, Fleet, Artifact, Player
from ..config import get_config

logger = logging.getLogger(__name__)


class GameState:
    """
    Central repository for all game state.
    """

    def __init__(self, map_size=255):
        self.map_size = map_size
        self.worlds: Dict[int, World] = {}
        self.fleets: Dict[int, Fleet] = {}
        self.artifacts: Dict[int, Artifact] = {}
        self.players: Dict[any, Player] = {}  # websocket -> Player
        self._persistent_players: Dict[str, dict] = {}  # player_name -> player_data (for reconnection)

        self.game_turn = 0
        self.turn_end_time = 0
        self.current_turn_duration = 180  # 3 minutes
        self.players_ready = set()

        self.next_player_id = 1

    def initialize_map(self):
        """Generate initial game map with worlds, connections, and artifacts."""
        config = get_config()
        world_settings = config.world_settings
        artifact_settings = config.artifact_settings
        fleet_settings = config.fleet_settings

        # Create worlds
        industry_range = world_settings.get('industry_range', [0, 10])
        mines_range = world_settings.get('mines_range', [0, 10])
        limit_range = world_settings.get('limit_range', [10, 50])
        population_range = world_settings.get('population_range', [0, 50])

        for i in range(1, self.map_size + 1):
            w = World(i)
            w.industry = random.randint(*industry_range)
            w.mines = random.randint(*mines_range)
            w.limit = random.randint(*limit_range)
            # Population can't exceed limit
            max_pop = min(population_range[1], w.limit)
            w.population = random.randint(population_range[0], max_pop)
            self.worlds[i] = w

        # Create connections
        min_conn = world_settings.get('min_connections', 2)
        max_conn = world_settings.get('max_connections', 4)

        for i in range(1, self.map_size + 1):
            num_connections = random.randint(min_conn, max_conn)
            while len(self.worlds[i].connections) < num_connections:
                target = random.randint(1, self.map_size)
                if target != i and target not in self.worlds[i].connections:
                    self.worlds[i].connections.append(target)
                    self.worlds[target].connections.append(i)

        # Create neutral fleets
        num_fleets = fleet_settings.get('num_neutral_fleets', 255)
        for i in range(1, num_fleets + 1):
            w = self.worlds[random.randint(1, self.map_size)]
            f = Fleet(i, None, w)
            self.fleets[i] = f

        # Create artifacts
        aid = 1
        types = artifact_settings.get('types', [
            "Platinum", "Ancient", "Vegan", "Blessed", "Arcturian",
            "Silver", "Titanium", "Gold", "Radiant", "Plastic"
        ])
        items = artifact_settings.get('items', [
            "Lodestar", "Pyramid", "Stardust", "Shekel", "Crown",
            "Sword", "Moonstone", "Sepulchre", "Sphinx"
        ])

        # Standard artifacts (type + item combinations)
        for t in types:
            for item in items:
                name = f"{t} {item}"
                a = Artifact(aid, name)
                self.artifacts[aid] = a
                aid += 1
                w = self.worlds[random.randint(1, self.map_size)]
                w.artifacts.append(a)

        # Special artifacts
        special_artifacts = artifact_settings.get('special_artifacts', [])
        for special in special_artifacts:
            name = special['name']
            a = Artifact(aid, name)
            # Store special properties for future use
            a.points = special.get('points', 15)
            a.effect = special.get('effect', 'none')
            self.artifacts[aid] = a
            aid += 1
            w = self.worlds[random.randint(1, self.map_size)]
            w.artifacts.append(a)

    def get_player_by_websocket(self, websocket) -> Optional[Player]:
        """Get player by websocket connection."""
        return self.players.get(websocket)

    def get_player_by_name(self, name: str) -> Optional[Player]:
        """Get player by name."""
        for player in self.players.values():
            if player.name == name:
                return player
        return None

    def add_player(self, websocket, name: str) -> Player:
        """Create and add a new player."""
        player = Player(self.next_player_id, name, websocket)
        self.next_player_id += 1
        self.players[websocket] = player
        return player

    def remove_player(self, websocket):
        """Remove a player from the game."""
        if websocket in self.players:
            del self.players[websocket]
        if websocket in self.players_ready:
            self.players_ready.remove(websocket)

    def get_all_players(self):
        """Get list of all players."""
        return list(self.players.values())

    def get_world(self, world_id: int) -> Optional[World]:
        """Get world by ID."""
        return self.worlds.get(world_id)

    def get_fleet(self, fleet_id: int) -> Optional[Fleet]:
        """Get fleet by ID."""
        return self.fleets.get(fleet_id)

    def get_average_turn_duration_seconds(self) -> int:
        """
        Calculate average turn duration from all players' preferences.
        Returns duration in seconds.
        """
        players = [p for p in self.players.values() if p.name]  # Only joined players
        if not players:
            return 180  # Default 3 minutes if no players

        total_minutes = sum(p.turn_timer_minutes for p in players)
        avg_minutes = total_minutes / len(players)
        return int(avg_minutes * 60)  # Convert to seconds

    def get_persistent_player(self, player_name: str) -> Optional[dict]:
        """
        Get persistent player data for reconnection.

        Args:
            player_name: Name of the player

        Returns:
            Player data dict or None
        """
        return self._persistent_players.get(player_name)

    def reconnect_player(self, player: Player, player_data: dict):
        """
        Reconnect a player to their existing game state.

        Args:
            player: New Player object with websocket
            player_data: Persistent player data
        """
        # Restore player state
        player.id = player_data["id"]
        player.name = player_data["name"]
        player.character_type = player_data["character_type"]
        player.score = player_data["score"]
        player.turn_timer_minutes = player_data["turn_timer_minutes"]
        player.known_worlds = player_data["known_worlds"]

        # Reconnect fleets
        for fleet_id in player_data.get("fleet_ids", []):
            if fleet_id in self.fleets:
                fleet = self.fleets[fleet_id]
                fleet.owner = player
                player.fleets.append(fleet)

        # Reconnect worlds
        for world_id in player_data.get("world_ids", []):
            if world_id in self.worlds:
                world = self.worlds[world_id]
                world.owner = player
                player.worlds.append(world)

        logger.info(f"Reconnected player {player.name} with {len(player.worlds)} worlds and {len(player.fleets)} fleets")


# Global game state instance
_game_state = None


def get_game_state() -> GameState:
    """Get the global game state instance."""
    global _game_state
    if _game_state is None:
        _game_state = GameState()
        _game_state.initialize_map()
    return _game_state


def reset_game_state():
    """Reset the global game state (useful for testing)."""
    global _game_state
    _game_state = GameState()
    _game_state.initialize_map()


def set_game_state(game_state: GameState):
    """Set the global game state (useful for testing)."""
    global _game_state
    _game_state = game_state
