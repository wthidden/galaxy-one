"""
Game manager for multi-game support.
Manages creation, deletion, and lookup of game instances.
"""
import logging
from typing import Dict, Optional, List
from .game_instance import Game, PlayerInGame

logger = logging.getLogger(__name__)


class GameManager:
    """Manages multiple concurrent game instances."""

    def __init__(self):
        self._games: Dict[str, Game] = {}  # game_id -> Game

    def create_game(
        self,
        name: str,
        created_by: str,
        max_players: int = 6,
        map_size: int = 100,
        settings: Optional[dict] = None
    ) -> tuple[bool, str, Optional[Game]]:
        """
        Create a new game.

        Args:
            name: Game name
            created_by: Player ID of creator
            max_players: Maximum number of players
            map_size: Size of game map
            settings: Optional game settings

        Returns:
            (success, message, game) - game is None on failure
        """
        # Validate name
        if not name or len(name) < 3:
            return False, "Game name must be at least 3 characters", None

        if len(name) > 50:
            return False, "Game name must be at most 50 characters", None

        # Check for duplicate names
        for game in self._games.values():
            if game.name.lower() == name.lower():
                return False, "A game with this name already exists", None

        # Create game
        game = Game(
            name=name,
            created_by=created_by,
            max_players=max_players,
            map_size=map_size,
            settings=settings
        )

        self._games[game.id] = game
        logger.info(f"Created game: {name} (ID: {game.id}, created by: {created_by})")

        return True, f"Game '{name}' created", game

    def get_game(self, game_id: str) -> Optional[Game]:
        """
        Get game by ID.

        Args:
            game_id: Game ID

        Returns:
            Game if found, None otherwise
        """
        return self._games.get(game_id)

    def delete_game(self, game_id: str) -> tuple[bool, str]:
        """
        Delete a game.

        Args:
            game_id: Game ID to delete

        Returns:
            (success, message)
        """
        if game_id not in self._games:
            return False, "Game not found"

        game = self._games[game_id]
        del self._games[game_id]
        logger.info(f"Deleted game: {game.name} (ID: {game_id})")

        return True, f"Game '{game.name}' deleted"

    def list_games(self) -> List[Game]:
        """
        Get list of all games.

        Returns:
            List of Game objects
        """
        return list(self._games.values())

    def get_player_games(self, player_id: str) -> List[Game]:
        """
        Get all games a player is participating in.

        Args:
            player_id: Player ID

        Returns:
            List of Game objects
        """
        return [
            game for game in self._games.values()
            if player_id in game.players
        ]

    def get_available_games(self, player_id: str) -> List[Game]:
        """
        Get games available for a player to join (not full, not in already).

        Args:
            player_id: Player ID

        Returns:
            List of Game objects
        """
        return [
            game for game in self._games.values()
            if (
                player_id not in game.players and  # Not already in game
                not game.is_full and  # Not full
                game.status in ["waiting", "active"]  # Not completed
            )
        ]

    def cleanup_empty_waiting_games(self):
        """Remove waiting games with no players."""
        empty_games = [
            game_id for game_id, game in self._games.items()
            if game.status == "waiting" and game.player_count == 0
        ]

        for game_id in empty_games:
            game = self._games[game_id]
            logger.info(f"Removing empty waiting game: {game.name}")
            del self._games[game_id]

        if empty_games:
            logger.info(f"Cleaned up {len(empty_games)} empty waiting games")

    def get_game_count(self) -> int:
        """Get total number of games."""
        return len(self._games)

    def load_games(self, games_data: list):
        """
        Load games from persistence.

        Args:
            games_data: List of game dictionaries
        """
        # Note: Full implementation would reconstruct Game objects
        # from saved data. For now, this is a placeholder.
        logger.info(f"Loading {len(games_data)} games from persistence")
        # TODO: Implement full game state loading


# Global game manager instance
_game_manager: Optional[GameManager] = None


def get_game_manager() -> GameManager:
    """Get the global game manager instance."""
    global _game_manager
    if _game_manager is None:
        _game_manager = GameManager()
    return _game_manager
