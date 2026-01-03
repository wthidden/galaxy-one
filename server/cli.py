#!/usr/bin/env python3
"""
StarWeb Game Management CLI

Commands:
  new-game              - Start a new game (clears existing state)
  reset-all             - Reset everything (accounts, sessions, games, state)
  show-config           - Display current configuration
  validate-config       - Validate configuration file
  backup-state          - Backup current game state
  restore-state [file]  - Restore game state from backup
  view-bug-reports      - View recent bug reports from players

Note: These commands should be run while the server is STOPPED.
"""
import argparse
import sys
import os
import shutil
import yaml
import getpass
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

    # Confirm if state file exists (skip if --force)
    persistence = GameStatePersistence()
    if persistence.save_file.exists() and not args.force:
        response = input(f"\n⚠️  Existing game state found at {persistence.save_file}\n"
                        "This will DELETE the current game. Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return
    elif persistence.save_file.exists():
        print(f"\n⚠️  Existing game state found at {persistence.save_file}")
        print("Force mode enabled - proceeding without confirmation...")

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


def reset_all(args):
    """Reset everything - game state, accounts, sessions, and games."""
    from pathlib import Path

    print("=" * 60)
    print("StarWeb - Complete Reset")
    print("=" * 60)

    # List what will be deleted
    files_to_delete = []
    data_dir = Path("data")

    if (data_dir / "gamestate.json").exists():
        files_to_delete.append("Game state")
    if (data_dir / "accounts.json").exists():
        files_to_delete.append("Player accounts")
    if (data_dir / "sessions.json").exists():
        files_to_delete.append("Active sessions")
    if (data_dir / "games.json").exists():
        files_to_delete.append("Game instances")

    if not files_to_delete:
        print("\n✓ No data files found. System is already clean.")
        return 0

    print(f"\nThis will delete:")
    for item in files_to_delete:
        print(f"  - {item}")

    if not args.force:
        response = input("\n⚠️  This will DELETE ALL game data. Continue? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return 0

    # Create backup
    backup_dir = data_dir / "backups" / f"reset_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    backup_dir.mkdir(parents=True, exist_ok=True)

    print(f"\nCreating backup in: {backup_dir}")
    for filename in ["gamestate.json", "accounts.json", "sessions.json", "games.json"]:
        source = data_dir / filename
        if source.exists():
            shutil.copy(source, backup_dir / filename)
            print(f"  ✓ Backed up {filename}")

    # Delete files
    print("\nDeleting data files...")
    for filename in ["gamestate.json", "accounts.json", "sessions.json", "games.json"]:
        filepath = data_dir / filename
        if filepath.exists():
            filepath.unlink()
            print(f"  ✓ Deleted {filename}")

    print("\n" + "=" * 60)
    print("Reset complete!")
    print(f"Backup saved to: {backup_dir}")
    print("\nRestart the server to begin with a clean state.")
    print("=" * 60)
    return 0


def view_bug_reports(args):
    """View recent bug reports from players."""
    from server.bug_reporter import BugReporter

    reporter = BugReporter()
    reports = reporter.get_recent_reports(limit=args.limit)

    if not reports:
        print("No bug reports found.")
        return 0

    print("=" * 80)
    print(f"Bug Reports ({len(reports)} most recent)")
    print("=" * 80)

    for i, report in enumerate(reports, 1):
        print(f"\n[Report #{i}]")
        print(f"  Submitted:     {report['timestamp']}")
        print(f"  Player:        {report['player_name']} (ID: {report['player_id']})")
        print(f"  Character:     {report.get('character_type', 'Unknown')}")
        print(f"  Game Turn:     {report['game_turn']}")
        print(f"  Description:")
        # Indent description
        for line in report['description'].split('\n'):
            print(f"    {line}")
        print("-" * 80)

    print(f"\nTotal reports in database: {reporter.get_report_count()}")
    print(f"Reports file: {reporter.reports_file}")
    print("=" * 80)
    return 0


def bootstrap_admin(args):
    """Bootstrap first admin account and update config."""
    from server.auth.auth_manager import get_auth_manager
    from server.persistence.accounts import get_account_persistence

    print("=" * 60)
    print("StarWeb - Bootstrap Admin Account")
    print("=" * 60)

    # Get username and password
    username = args.username or input("Admin username: ")
    password = args.password
    if not password:
        password = getpass.getpass("Admin password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("✗ Passwords do not match")
            return 1

    email = args.email or input("Admin email (optional): ") or None

    # Create account
    auth_manager = get_auth_manager()
    persistence = get_account_persistence()

    # Load existing accounts
    try:
        accounts_data = persistence.load_accounts()
        auth_manager.load_accounts(accounts_data)
    except:
        # No existing accounts, that's fine
        pass

    success, message, session = auth_manager.signup(username, password, email)

    if not success:
        print(f"✗ Failed to create admin account: {message}")
        return 1

    print(f"✓ Admin account created: {username}")

    # Save accounts
    persistence.save_accounts(auth_manager.get_all_accounts())
    print(f"✓ Saved account data")

    # Update config file
    config_file = Path("game_config.yaml")
    try:
        with open(config_file, 'r') as f:
            config = yaml.safe_load(f)

        if 'admin' not in config:
            config['admin'] = {}
        if 'users' not in config['admin']:
            config['admin']['users'] = []

        if username not in config['admin']['users']:
            config['admin']['users'].append(username)

        config['admin']['enabled'] = True
        config['admin']['audit_log'] = 'data/admin_audit.jsonl'

        with open(config_file, 'w') as f:
            yaml.dump(config, f, default_flow_style=False)

        print(f"✓ Updated {config_file}")
    except Exception as e:
        print(f"✗ Failed to update config: {e}")
        return 1

    print()
    print("=" * 60)
    print("Bootstrap complete! Admin account ready.")
    print("=" * 60)
    return 0


def admin_list_users(args):
    """List all user accounts."""
    from server.auth.auth_manager import get_auth_manager
    from server.persistence.accounts import get_account_persistence

    auth_manager = get_auth_manager()
    persistence = get_account_persistence()

    # Load accounts
    try:
        accounts_data = persistence.load_accounts()
        auth_manager.load_accounts(accounts_data)
    except Exception as e:
        print(f"✗ Failed to load accounts: {e}")
        return 1

    accounts = auth_manager.get_all_accounts()

    print("=" * 80)
    print(f"User Accounts ({len(accounts)} total)")
    print("=" * 80)

    for username, account in sorted(accounts.items()):
        admin_flag = "[ADMIN]" if account.is_admin() else ""
        print(f"{username:20s} {admin_flag:8s} ID: {account.id}")
        print(f"  Email: {account.email or 'N/A'}")
        print(f"  Created: {account.created_at}")
        print(f"  Last Login: {account.last_login or 'Never'}")
        print()

    return 0


def admin_create_user(args):
    """Create a new user account."""
    from server.auth.auth_manager import get_auth_manager
    from server.persistence.accounts import get_account_persistence

    auth_manager = get_auth_manager()
    persistence = get_account_persistence()

    # Load accounts
    try:
        accounts_data = persistence.load_accounts()
        auth_manager.load_accounts(accounts_data)
    except:
        pass

    # Create account
    success, message, session = auth_manager.signup(args.username, args.password, args.email)

    if not success:
        print(f"✗ Failed to create user: {message}")
        return 1

    print(f"✓ User '{args.username}' created successfully")

    # Save accounts
    persistence.save_accounts(auth_manager.get_all_accounts())
    print(f"✓ Saved account data")

    return 0


def admin_delete_user(args):
    """Delete a user account."""
    from server.auth.auth_manager import get_auth_manager
    from server.persistence.accounts import get_account_persistence

    auth_manager = get_auth_manager()
    persistence = get_account_persistence()

    # Load accounts
    try:
        accounts_data = persistence.load_accounts()
        auth_manager.load_accounts(accounts_data)
    except Exception as e:
        print(f"✗ Failed to load accounts: {e}")
        return 1

    # Confirm deletion
    if not args.force:
        response = input(f"Delete user '{args.username}'? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return 0

    # Delete account
    success, message = auth_manager.delete_account(args.username)

    if not success:
        print(f"✗ {message}")
        return 1

    print(f"✓ {message}")

    # Save accounts
    persistence.save_accounts(auth_manager.get_all_accounts())
    print(f"✓ Saved account data")

    return 0


def admin_reset_password(args):
    """Reset user password."""
    from server.auth.auth_manager import get_auth_manager
    from server.persistence.accounts import get_account_persistence

    auth_manager = get_auth_manager()
    persistence = get_account_persistence()

    # Load accounts
    try:
        accounts_data = persistence.load_accounts()
        auth_manager.load_accounts(accounts_data)
    except Exception as e:
        print(f"✗ Failed to load accounts: {e}")
        return 1

    # Get password
    password = args.password
    if not password:
        password = getpass.getpass("New password: ")
        password_confirm = getpass.getpass("Confirm password: ")
        if password != password_confirm:
            print("✗ Passwords do not match")
            return 1

    # Reset password
    success, message = auth_manager.reset_password(args.username, password)

    if not success:
        print(f"✗ {message}")
        return 1

    print(f"✓ {message}")

    # Save accounts
    persistence.save_accounts(auth_manager.get_all_accounts())
    print(f"✓ Saved account data")

    return 0


def admin_change_email(args):
    """Change user email."""
    from server.auth.auth_manager import get_auth_manager
    from server.persistence.accounts import get_account_persistence

    auth_manager = get_auth_manager()
    persistence = get_account_persistence()

    # Load accounts
    try:
        accounts_data = persistence.load_accounts()
        auth_manager.load_accounts(accounts_data)
    except Exception as e:
        print(f"✗ Failed to load accounts: {e}")
        return 1

    # Change email
    success, message = auth_manager.change_email(args.username, args.email)

    if not success:
        print(f"✗ {message}")
        return 1

    print(f"✓ {message}")

    # Save accounts
    persistence.save_accounts(auth_manager.get_all_accounts())
    print(f"✓ Saved account data")

    return 0


def admin_list_games(args):
    """List all game instances."""
    from server.game_manager import get_game_manager

    game_manager = get_game_manager()
    games = game_manager.list_games()

    print("=" * 80)
    print(f"Game Instances ({len(games)} total)")
    print("=" * 80)

    for game in games:
        print(f"\n{game.name}")
        print(f"  ID: {game.id}")
        print(f"  Status: {game.status}")
        print(f"  Players: {len(game.players)}/{game.max_players}")
        print(f"  Created by: {game.created_by}")

        if args.detailed and len(game.players) > 0:
            print(f"  Player list:")
            for player_id, player in game.players.items():
                print(f"    - {player.player_name} ({player.character_type})")

    return 0


def admin_force_start(args):
    """Force-start a game."""
    from server.game_manager import get_game_manager

    game_manager = get_game_manager()
    game = game_manager.get_game(args.game_id)

    if not game:
        print(f"✗ Game not found: {args.game_id}")
        return 1

    # Confirm
    if not args.force:
        response = input(f"Force-start game '{game.name}'? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return 0

    # Start game
    try:
        game.start_game()
        print(f"✓ Game '{game.name}' started")
        return 0
    except Exception as e:
        print(f"✗ Failed to start game: {e}")
        return 1


def admin_kick_player(args):
    """Kick player from game."""
    from server.game_manager import get_game_manager

    game_manager = get_game_manager()
    game = game_manager.get_game(args.game_id)

    if not game:
        print(f"✗ Game not found: {args.game_id}")
        return 1

    # Confirm
    if not args.force:
        response = input(f"Kick player '{args.player_id}' from game '{game.name}'? (yes/no): ")
        if response.lower() not in ['yes', 'y']:
            print("Cancelled.")
            return 0

    # Kick player
    success, message = game.remove_player(args.player_id)

    if not success:
        print(f"✗ {message}")
        return 1

    print(f"✓ {message}")
    return 0


def admin_view_audit(args):
    """View admin audit log."""
    from server.admin.audit_logger import get_audit_logger

    audit_logger = get_audit_logger()
    entries = audit_logger.get_recent_actions(limit=args.limit)

    if not entries:
        print("No audit entries found.")
        return 0

    print("=" * 80)
    print(f"Admin Audit Log ({len(entries)} most recent)")
    print("=" * 80)

    for i, entry in enumerate(entries, 1):
        print(f"\n[Entry #{i}]")
        print(f"  Timestamp: {entry['timestamp']}")
        print(f"  Admin:     {entry['admin']}")
        print(f"  Action:    {entry['action']}")
        print(f"  Details:   {entry['details']}")
        print("-" * 80)

    print(f"\nTotal entries: {audit_logger.get_entry_count()}")
    print(f"Audit file: {audit_logger.audit_file}")
    print("=" * 80)
    return 0


def main():
    parser = argparse.ArgumentParser(
        description="StarWeb Game Management CLI",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    subparsers = parser.add_subparsers(dest='command', help='Commands')

    # new-game command
    new_game_parser = subparsers.add_parser('new-game', help='Start a new game (clears existing state)')
    new_game_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
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

    # view-bug-reports command
    view_reports_parser = subparsers.add_parser('view-bug-reports', help='View recent bug reports from players')
    view_reports_parser.add_argument('--limit', type=int, default=20, help='Number of reports to show (default: 20)')
    view_reports_parser.set_defaults(func=view_bug_reports)

    # bootstrap-admin command
    bootstrap_parser = subparsers.add_parser('bootstrap-admin', help='Bootstrap first admin account')
    bootstrap_parser.add_argument('--username', help='Admin username')
    bootstrap_parser.add_argument('--password', help='Admin password')
    bootstrap_parser.add_argument('--email', help='Admin email')
    bootstrap_parser.set_defaults(func=bootstrap_admin)

    # admin-list-users command
    admin_list_users_parser = subparsers.add_parser('admin-list-users', help='List all user accounts')
    admin_list_users_parser.set_defaults(func=admin_list_users)

    # admin-create-user command
    admin_create_user_parser = subparsers.add_parser('admin-create-user', help='Create a new user account')
    admin_create_user_parser.add_argument('username', help='Username')
    admin_create_user_parser.add_argument('password', help='Password')
    admin_create_user_parser.add_argument('--email', help='Email address')
    admin_create_user_parser.set_defaults(func=admin_create_user)

    # admin-delete-user command
    admin_delete_user_parser = subparsers.add_parser('admin-delete-user', help='Delete a user account')
    admin_delete_user_parser.add_argument('username', help='Username to delete')
    admin_delete_user_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    admin_delete_user_parser.set_defaults(func=admin_delete_user)

    # admin-reset-password command
    admin_reset_password_parser = subparsers.add_parser('admin-reset-password', help='Reset user password')
    admin_reset_password_parser.add_argument('username', help='Username')
    admin_reset_password_parser.add_argument('--password', help='New password (prompts if not provided)')
    admin_reset_password_parser.set_defaults(func=admin_reset_password)

    # admin-change-email command
    admin_change_email_parser = subparsers.add_parser('admin-change-email', help='Change user email')
    admin_change_email_parser.add_argument('username', help='Username')
    admin_change_email_parser.add_argument('email', help='New email address')
    admin_change_email_parser.set_defaults(func=admin_change_email)

    # admin-list-games command
    admin_list_games_parser = subparsers.add_parser('admin-list-games', help='List all game instances')
    admin_list_games_parser.add_argument('--detailed', action='store_true', help='Show detailed info')
    admin_list_games_parser.set_defaults(func=admin_list_games)

    # admin-force-start command
    admin_force_start_parser = subparsers.add_parser('admin-force-start', help='Force-start a game')
    admin_force_start_parser.add_argument('game_id', help='Game ID')
    admin_force_start_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    admin_force_start_parser.set_defaults(func=admin_force_start)

    # admin-kick-player command
    admin_kick_parser = subparsers.add_parser('admin-kick-player', help='Kick player from game')
    admin_kick_parser.add_argument('game_id', help='Game ID')
    admin_kick_parser.add_argument('player_id', help='Player ID or username')
    admin_kick_parser.add_argument('--force', action='store_true', help='Skip confirmation')
    admin_kick_parser.set_defaults(func=admin_kick_player)

    # admin-view-audit command
    admin_audit_parser = subparsers.add_parser('admin-view-audit', help='View admin audit log')
    admin_audit_parser.add_argument('--limit', type=int, default=50, help='Number of entries to show (default: 50)')
    admin_audit_parser.set_defaults(func=admin_view_audit)

    # reset-all command
    reset_all_parser = subparsers.add_parser('reset-all', help='Reset everything (game state, accounts, sessions, games)')
    reset_all_parser.add_argument('--force', action='store_true', help='Skip confirmation prompt')
    reset_all_parser.set_defaults(func=reset_all)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
