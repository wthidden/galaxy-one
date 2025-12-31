"""
Game instance model for multi-game support.
Wraps GameState with metadata and player management.
"""
import uuid
import logging
from datetime import datetime
from typing import Dict, Optional, List
from .game.state import GameState

logger = logging.getLogger(__name__)


class PlayerInGame:
    """Represents a player's participation in a specific game."""

    def __init__(
        self,
        player_id: str,
        player_name: str,
        character_type: str,
        character_name: str,
        joined_at: Optional[datetime] = None,
        last_active: Optional[datetime] = None,
        is_ready: bool = False,
        websocket = None
    ):
        self.player_id = player_id
        self.player_name = player_name  # Account username
        self.character_type = character_type
        self.character_name = character_name  # In-game display name
        self.joined_at = joined_at or datetime.now()
        self.last_active = last_active or datetime.now()
        self.is_ready = is_ready
        self.websocket = websocket

    def to_dict(self) -> dict:
        """Convert to dictionary for serialization."""
        return {
            "player_id": self.player_id,
            "player_name": self.player_name,
            "character_type": self.character_type,
            "character_name": self.character_name,
            "joined_at": self.joined_at.isoformat() if self.joined_at else None,
            "last_active": self.last_active.isoformat() if self.last_active else None,
            "is_ready": self.is_ready
        }

    @classmethod
    def from_dict(cls, data: dict) -> 'PlayerInGame':
        """Create from dictionary."""
        return cls(
            player_id=data["player_id"],
            player_name=data["player_name"],
            character_type=data["character_type"],
            character_name=data["character_name"],
            joined_at=datetime.fromisoformat(data["joined_at"]) if data.get("joined_at") else None,
            last_active=datetime.fromisoformat(data["last_active"]) if data.get("last_active") else None,
            is_ready=data.get("is_ready", False)
        )


class Game:
    """
    Represents a single game instance.
    Wraps GameState and adds metadata, player management, and settings.
    """

    def __init__(
        self,
        name: str,
        created_by: str,
        game_id: Optional[str] = None,
        status: str = "waiting",
        created_at: Optional[datetime] = None,
        max_players: int = 6,
        map_size: int = 100,
        settings: Optional[dict] = None
    ):
        self.id = game_id or str(uuid.uuid4())
        self.name = name
        self.status = status  # "waiting", "active", "completed"
        self.created_by = created_by  # player_id
        self.created_at = created_at or datetime.now()
        self.max_players = max_players
        self.map_size = map_size
        self.settings = settings or {}

        # Game state (the actual game logic)
        self.game_state = GameState(map_size=map_size)

        # Player membership
        self.players: Dict[str, PlayerInGame] = {}  # player_id -> PlayerInGame

    @property
    def current_turn(self) -> int:
        """Get current turn number from game state."""
        return self.game_state.game_turn

    @property
    def turn_end_time(self) -> Optional[float]:
        """Get turn end time from game state."""
        return self.game_state.turn_end_time

    @property
    def player_count(self) -> int:
        """Get number of players in game."""
        return len(self.players)

    @property
    def is_full(self) -> bool:
        """Check if game has reached max players."""
        return self.player_count >= self.max_players

    def can_start(self) -> bool:
        """Check if game can start (at least 2 players)."""
        return self.player_count >= 2

    def add_player(
        self,
        player_id: str,
        player_name: str,
        character_type: str,
        character_name: str,
        websocket=None
    ) -> tuple[bool, str]:
        """
        Add a player to the game.

        Returns:
            (success, message)
        """
        if player_id in self.players:
            return False, "Already in this game"

        if self.is_full:
            return False, "Game is full"

        if self.status == "completed":
            return False, "Game has ended"

        player_in_game = PlayerInGame(
            player_id=player_id,
            player_name=player_name,
            character_type=character_type,
            character_name=character_name,
            websocket=websocket
        )

        self.players[player_id] = player_in_game
        logger.info(f"Player {player_name} ({character_type}) joined game {self.name}")

        # If first player joins waiting game, keep waiting
        # If second player joins, we can start the game
        if self.status == "waiting" and self.can_start():
            logger.info(f"Game {self.name} ready to start ({self.player_count} players)")

        return True, f"Joined game {self.name}"

    def remove_player(self, player_id: str) -> tuple[bool, str]:
        """
        Remove a player from the game.

        Returns:
            (success, message)
        """
        if player_id not in self.players:
            return False, "Not in this game"

        if self.status == "active":
            # In active game, mark as inactive rather than removing
            # (preserves game state)
            del self.players[player_id]
            logger.info(f"Player {player_id} left active game {self.name}")
            return True, "Left game"
        else:
            # In waiting game, can fully remove
            del self.players[player_id]
            logger.info(f"Player {player_id} left waiting game {self.name}")
            return True, "Left game"

    def get_player(self, player_id: str) -> Optional[PlayerInGame]:
        """Get player by ID."""
        return self.players.get(player_id)

    def update_player_websocket(self, player_id: str, websocket):
        """Update a player's websocket connection."""
        if player_id in self.players:
            self.players[player_id].websocket = websocket
            self.players[player_id].last_active = datetime.now()

    def get_scoreboard(self) -> List[dict]:
        """
        Get current scoreboard sorted by score.

        Returns:
            List of player info dicts with scores
        """
        scoreboard = []

        for player_id, player_in_game in self.players.items():
            # Get player from game state
            game_player = None
            for p in self.game_state.get_all_players():
                if p.name == player_in_game.character_name:
                    game_player = p
                    break

            if game_player:
                scoreboard.append({
                    "player_name": player_in_game.player_name,
                    "character_name": player_in_game.character_name,
                    "character_type": player_in_game.character_type,
                    "score": game_player.score,
                    "worlds": len(game_player.worlds),
                    "fleets": len(game_player.fleets)
                })

        # Sort by score descending
        scoreboard.sort(key=lambda x: x["score"], reverse=True)
        return scoreboard

    def to_dict(self, include_state: bool = False) -> dict:
        """
        Convert to dictionary for serialization.

        Args:
            include_state: If True, include full game state
        """
        data = {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "created_by": self.created_by,
            "created_at": self.created_at.isoformat(),
            "max_players": self.max_players,
            "map_size": self.map_size,
            "settings": self.settings,
            "current_turn": self.current_turn,
            "turn_end_time": self.turn_end_time,
            "player_count": self.player_count,
            "players": {
                player_id: player.to_dict()
                for player_id, player in self.players.items()
            }
        }

        if include_state:
            # Include full game state for persistence
            data["game_state"] = {
                "game_turn": self.game_state.game_turn,
                "map_size": self.game_state.map_size,
                # Add other game state fields as needed
            }

        return data

    def to_lobby_info(self) -> dict:
        """
        Get summary info for lobby display.

        Returns:
            Minimal game info dict
        """
        return {
            "id": self.id,
            "name": self.name,
            "status": self.status,
            "current_turn": self.current_turn,
            "player_count": self.player_count,
            "max_players": self.max_players,
            "created_at": self.created_at.isoformat()
        }
