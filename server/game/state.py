"""
Central game state management.
"""
import random
from typing import Dict, Optional
from .entities import World, Fleet, Artifact, Player


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

        self.game_turn = 0
        self.turn_end_time = 0
        self.current_turn_duration = 180  # 3 minutes
        self.players_ready = set()

        self.next_player_id = 1

    def initialize_map(self):
        """Generate initial game map with worlds, connections, and artifacts."""
        # Create worlds
        for i in range(1, self.map_size + 1):
            w = World(i)
            w.industry = random.randint(0, 10)
            w.mines = random.randint(0, 10)
            w.limit = random.randint(10, 50)
            w.population = random.randint(0, w.limit)
            self.worlds[i] = w

        # Create connections
        for i in range(1, self.map_size + 1):
            num_connections = random.randint(2, 4)
            while len(self.worlds[i].connections) < num_connections:
                target = random.randint(1, self.map_size)
                if target != i and target not in self.worlds[i].connections:
                    self.worlds[i].connections.append(target)
                    self.worlds[target].connections.append(i)

        # Create neutral fleets
        for i in range(1, 256):
            w = self.worlds[random.randint(1, self.map_size)]
            f = Fleet(i, None, w)
            self.fleets[i] = f

        # Create artifacts
        aid = 1
        types = [
            "Platinum", "Ancient", "Vegan", "Blessed", "Arcturian",
            "Silver", "Titanium", "Gold", "Radiant", "Plastic"
        ]
        items = [
            "Lodestar", "Pyramid", "Stardust", "Shekel", "Crown",
            "Sword", "Moonstone", "Sepulchre", "Sphinx"
        ]

        for t in types:
            for item in items:
                name = f"{t} {item}"
                a = Artifact(aid, name)
                self.artifacts[aid] = a
                aid += 1
                w = self.worlds[random.randint(1, self.map_size)]
                w.artifacts.append(a)

        specials = [
            "Treasure of Polaris", "Slippers of Venus", "Radioactive Isotope",
            "Lesser of Two Evils", "Black Box"
        ]
        for i in range(1, 6):
            specials.append(f"Nebula Scroll {i}")

        for name in specials:
            a = Artifact(aid, name)
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
