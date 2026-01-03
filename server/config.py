"""
Game configuration management.
Loads settings from game_config.yaml
"""
import yaml
import os
from pathlib import Path
from typing import Dict, Any, Optional

class GameConfig:
    """Manages game configuration from YAML file."""

    def __init__(self, config_file: Optional[str] = None):
        """Load configuration from file."""
        if config_file is None:
            # Default to game_config.yaml in project root
            config_file = Path(__file__).parent.parent / "game_config.yaml"

        self.config_file = Path(config_file)
        self.config: Dict[str, Any] = {}
        self.load()

    def load(self):
        """Load configuration from YAML file."""
        if not self.config_file.exists():
            raise FileNotFoundError(f"Config file not found: {self.config_file}")

        with open(self.config_file, 'r') as f:
            self.config = yaml.safe_load(f)

    def get(self, path: str, default=None):
        """
        Get configuration value using dot notation.
        Example: config.get('game.map_size') -> 255
        """
        keys = path.split('.')
        value = self.config

        for key in keys:
            if isinstance(value, dict) and key in value:
                value = value[key]
            else:
                return default

        return value

    # Convenience properties for common settings

    @property
    def map_size(self) -> int:
        return self.get('game.map_size', 255)

    @property
    def default_turn_duration(self) -> int:
        return self.get('game.default_turn_duration', 3600)

    @property
    def min_turn_duration(self) -> int:
        return self.get('game.min_turn_duration', 300)

    @property
    def max_turn_duration(self) -> int:
        return self.get('game.max_turn_duration', 86400)

    @property
    def default_target_score(self) -> int:
        return self.get('game.default_target_score', 8000)

    @property
    def homeworld_settings(self) -> Dict[str, Any]:
        return self.get('game.homeworld', {})

    @property
    def world_settings(self) -> Dict[str, Any]:
        return self.get('worlds', {})

    @property
    def fleet_settings(self) -> Dict[str, Any]:
        return self.get('fleets', {})

    @property
    def artifact_settings(self) -> Dict[str, Any]:
        return self.get('artifacts', {})

    @property
    def combat_settings(self) -> Dict[str, Any]:
        return self.get('combat', {})

    @property
    def production_settings(self) -> Dict[str, Any]:
        return self.get('production', {})

    @property
    def character_settings(self) -> Dict[str, Any]:
        return self.get('characters', {})

    @property
    def admin_settings(self) -> Dict[str, Any]:
        return self.get('admin', {})

    @property
    def admin_users(self) -> list:
        return [u.lower() for u in self.get('admin.users', [])]

    @property
    def admin_enabled(self) -> bool:
        return self.get('admin.enabled', True)


# Singleton instance
_config_instance: Optional[GameConfig] = None


def get_config() -> GameConfig:
    """Get the global config instance."""
    global _config_instance
    if _config_instance is None:
        _config_instance = GameConfig()
    return _config_instance


def reload_config(config_file: Optional[str] = None):
    """Reload configuration from file."""
    global _config_instance
    _config_instance = GameConfig(config_file)
    return _config_instance
