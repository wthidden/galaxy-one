#!/usr/bin/env python3
"""
StarWeb Game Management CLI

Commands:
  new-game              - Start a new game (clears existing state)
  show-config           - Display current configuration
  validate-config       - Validate configuration file
  backup-state          - Backup current game state
  restore-state [file]  - Restore game state from backup
"""
import argparse
import sys
import os
import shutil
from pathlib import Path
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from server.config import get_config, reload_config
from server.game.state import GameState
from server.game.persistence import GameStatePersistence


def new_game(args):
    """Initialize a new game with no players."""
    config = get_config()

    print("=" * 60)
    print("StarWeb - New Game Initialization")
    print("=" * 60)

    # Confirm if state file exists
    persistence = GameStatePersistence()
    if persistence.save_file.exists():
        response = input(f"\n⚠️  Existing game state found at {persistence.save_file}\n"
                        "This will DELETE the current game. Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return

        # Backup existing state
        backup_name = f"{persistence.save_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(persistence.save_file, backup_name)
        print(f"✓ Backed up existing state to: {backup_name}")

    # Create new game state
    print(f"\nInitializing new game...")
    print(f"  Map size: {config.map_size} worlds")
    print(f"  Turn duration: {config.default_turn_duration}s ({config.default_turn_duration // 60} minutes)")
    print(f"  Target score: {config.default_target_score}")

    game_state = GameState(map_size=config.map_size)
    game_state.initialize_map()

    print(f"\n✓ Created {len(game_state.worlds)} worlds")
    print(f"✓ Created {len(game_state.fleets)} neutral fleets")
    print(f"✓ Placed {len(game_state.artifacts)} artifacts")

    # Count connections
    total_connections = sum(len(w.connections) for w in game_state.worlds.values())
    avg_connections = total_connections / len(game_state.worlds) if game_state.worlds else 0
    print(f"✓ Generated world connections (avg: {avg_connections:.1f} per world)")

    # Save to disk
    if persistence.save_state(game_state):
        print(f"\n✓ Game state saved to: {persistence.save_file}")
    else:
        print(f"\n✗ Failed to save game state")
        return 1

    print("\n" + "=" * 60)
    print("New game ready! Start the server to allow players to join.")
    print("=" * 60)
    return 0


def show_config(args):
    """Display current configuration."""
    config = get_config()

    print("=" * 60)
    print("StarWeb - Current Configuration")
    print("=" * 60)

    print("\n[Game Settings]")
    print(f"  Map size:              {config.map_size} worlds")
    print(f"  Default turn duration: {config.default_turn_duration}s ({config.default_turn_duration // 60} min)")
    print(f"  Min turn duration:     {config.min_turn_duration}s ({config.min_turn_duration // 60} min)")
    print(f"  Max turn duration:     {config.max_turn_duration}s ({config.max_turn_duration // 60} min)")
    print(f"  Default target score:  {config.default_target_score}")

    print("\n[Homeworld Settings]")
    hw = config.homeworld_settings
    print(f"  Population:  {hw.get('population', 'N/A')}")
    print(f"  Industry:    {hw.get('industry', 'N/A')}")
    print(f"  Mines:       {hw.get('mines', 'N/A')}")
    print(f"  Metal:       {hw.get('metal', 'N/A')}")
    print(f"  Limit:       {hw.get('limit', 'N/A')}")
    print(f"  Fleets:      {hw.get('num_fleets', 'N/A')} x {hw.get('ships_per_fleet', 'N/A')} ships")

    print("\n[World Generation]")
    ws = config.world_settings
    print(f"  Industry range:   {ws.get('industry_range', 'N/A')}")
    print(f"  Mines range:      {ws.get('mines_range', 'N/A')}")
    print(f"  Population range: {ws.get('population_range', 'N/A')}")
    print(f"  Limit range:      {ws.get('limit_range', 'N/A')}")
    print(f"  Connections:      {ws.get('min_connections', 'N/A')}-{ws.get('max_connections', 'N/A')} per world")

    print("\n[Artifacts]")
    arts = config.artifact_settings
    print(f"  Standard types:    {len(arts.get('types', []))}")
    print(f"  Standard items:    {len(arts.get('items', []))}")
    print(f"  Special artifacts: {len(arts.get('special_artifacts', []))}")
    print(f"  Allow on homeworlds: {arts.get('allow_on_homeworlds', False)}")

    print("\n[Special Artifacts]")
    for artifact in arts.get('special_artifacts', []):
        print(f"  {artifact['name']:25s} - {artifact['points']:4d} pts - {artifact.get('effect', 'none')}")

    print("\n[Character Types]")
    chars = config.character_settings
    for char_type, settings in chars.items():
        print(f"  {char_type}")
        for key, value in settings.items():
            print(f"    {key}: {value}")

    print(f"\nConfig file: {config.config_file}")
    print("=" * 60)
    return 0


def validate_config(args):
    """Validate configuration file."""
    print("Validating configuration...")

    try:
        config = reload_config(args.config)
        print(f"✓ Configuration file loaded: {config.config_file}")

        # Check required fields
        required_fields = [
            'game.map_size',
            'game.default_turn_duration',
            'game.homeworld.population',
            'worlds.min_connections',
            'artifacts.types',
            'artifacts.items',
        ]

        errors = []
        for field in required_fields:
            value = config.get(field)
            if value is None:
                errors.append(f"Missing required field: {field}")

        if errors:
            print("\n✗ Validation errors:")
            for error in errors:
                print(f"  - {error}")
            return 1

        print("✓ All required fields present")
        print("✓ Configuration is valid")
        return 0

    except Exception as e:
        print(f"✗ Configuration error: {e}")
        return 1


def backup_state(args):
    """Backup current game state."""
    persistence = GameStatePersistence()

    if not persistence.save_file.exists():
        print(f"✗ No game state found at {persistence.save_file}")
        return 1

    backup_name = args.output or f"{persistence.save_file}.backup.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    shutil.copy(persistence.save_file, backup_name)
    print(f"✓ Backed up game state to: {backup_name}")

    # Show file size
    size_kb = Path(backup_name).stat().st_size / 1024
    print(f"  Size: {size_kb:.1f} KB")
    return 0


def restore_state(args):
    """Restore game state from backup."""
    backup_file = Path(args.backup_file)
    persistence = GameStatePersistence()

    if not backup_file.exists():
        print(f"✗ Backup file not found: {backup_file}")
        return 1

    response = input(f"Restore game state from {backup_file}?\n"
                    "This will overwrite the current state. Continue? (yes/no): ")
    if response.lower() not in ['yes', 'y']:
        print("Cancelled.")
        return 0

    # Backup current state first
    if persistence.save_file.exists():
        current_backup = f"{persistence.save_file}.pre-restore.{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        shutil.copy(persistence.save_file, current_backup)
        print(f"✓ Current state backed up to: {current_backup}")

    # Restore
    shutil.copy(backup_file, persistence.save_file)
    print(f"✓ Game state restored from: {backup_file}")

    # Validate restored state
    game_state = GameState()
    if persistence.load_state(game_state):
        print(f"✓ Restored state is valid")
        print(f"  Turn: {game_state.game_turn}")
        print(f"  Worlds: {len(game_state.worlds)}")
        print(f"  Fleets: {len(game_state.fleets)}")
        print(f"  Persistent players: {len(game_state._persistent_players)}")
        return 0
    else:
        print(f"✗ Restored state failed validation")
        return 1


def main():
    parser = argparse.ArgumentParser(
        description="StarWeb Game Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # new-game command
    new_game_parser = subparsers.add_parser('new-game', help='Start a new game (clears existing state)')
    new_game_parser.set_defaults(func=new_game)

    # show-config command
    show_config_parser = subparsers.add_parser('show-config', help='Display current configuration')
    show_config_parser.set_defaults(func=show_config)

    # validate-config command
    validate_config_parser = subparsers.add_parser('validate-config', help='Validate configuration file')
    validate_config_parser.add_argument('--config', help='Path to config file (default: game_config.yaml)')
    validate_config_parser.set_defaults(func=validate_config)

    # backup-state command
    backup_state_parser = subparsers.add_parser('backup-state', help='Backup current game state')
    backup_state_parser.add_argument('--output', help='Backup file path (default: auto-generated)')
    backup_state_parser.set_defaults(func=backup_state)

    # restore-state command
    restore_state_parser = subparsers.add_parser('restore-state', help='Restore game state from backup')
    restore_state_parser.add_argument('backup_file', help='Path to backup file')
    restore_state_parser.set_defaults(func=restore_state)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
