# StarWeb Admin Guide

This guide covers game administration and configuration.

## Quick Start

### Initialize a New Game

```bash
./starweb-admin new-game
```

This creates a fresh game with:
- No players
- Newly generated map
- Default configuration settings

### View Current Configuration

```bash
./starweb-admin show-config
```

Shows all game settings from `game_config.yaml`.

### Backup Game State

```bash
./starweb-admin backup-state
```

Creates a timestamped backup of the current game.

### Restore from Backup

```bash
./starweb-admin restore-state data/gamestate.json.backup.20251229_120000
```

Restores game state from a backup file.

## Configuration

Game settings are stored in `game_config.yaml`. Edit this file to customize:

### Game Settings

```yaml
game:
  map_size: 255                    # Number of worlds
  default_turn_duration: 3600      # 60 minutes in seconds
  min_turn_duration: 300           # 5 minutes minimum
  max_turn_duration: 86400         # 24 hours maximum
  default_target_score: 8000       # Victory score
```

### Homeworld Resources

```yaml
game:
  homeworld:
    population: 25
    industry: 15
    mines: 10
    metal: 50
    limit: 50
    ships_per_fleet: 25
    num_fleets: 5
```

### World Generation

```yaml
worlds:
  industry_range: [0, 10]          # Random range for neutral worlds
  mines_range: [0, 10]
  population_range: [0, 50]
  limit_range: [10, 50]
  min_connections: 2               # Hyperspace lanes per world
  max_connections: 4
```

### Artifact Configuration

```yaml
artifacts:
  # Standard artifact types (combined with items)
  types:
    - Platinum
    - Ancient
    - Vegan
    # ... etc

  items:
    - Lodestar
    - Pyramid
    - Stardust
    # ... etc

  # Special artifacts with unique properties
  special_artifacts:
    - name: "Treasure of Polaris"
      points: 50
      effect: "navigation_bonus"

    - name: "Black Box"
      points: 100
      effect: "intelligence"

    - name: "Lesser of Two Evils"
      points: -10
      effect: "curse"
```

**Note**: `effect` field is for future implementation of artifact powers. Currently only `points` is used.

### Character Type Modifiers

```yaml
characters:
  "Empire Builder":
    industry_bonus: true           # 4 industry per build instead of 5

  "Merchant":
    cargo_capacity_multiplier: 2   # 2 cargo per ship

  "Pirate":
    capture_ratio: 3               # 3:1 to auto-capture fleets
```

## CLI Commands

### new-game

Start a fresh game with no players.

```bash
./starweb-admin new-game
```

- Backs up existing game state (if any)
- Creates new map based on configuration
- Saves to `data/gamestate.json`

### show-config

Display current configuration settings.

```bash
./starweb-admin show-config
```

Shows:
- Game settings (map size, turn timers, target score)
- Homeworld resources
- World generation parameters
- Artifact configuration
- Character type modifiers

### validate-config

Validate configuration file syntax.

```bash
./starweb-admin validate-config
./starweb-admin validate-config --config my_config.yaml
```

Checks for:
- Valid YAML syntax
- Required fields present
- Proper data types

### backup-state

Backup current game state.

```bash
./starweb-admin backup-state
./starweb-admin backup-state --output my_backup.json
```

Creates timestamped backup in `data/` directory.

### restore-state

Restore game from backup.

```bash
./starweb-admin restore-state data/gamestate.json.backup.20251229_120000
```

- Backs up current state first
- Restores from specified backup
- Validates restored state

### view-bug-reports

View bug reports submitted by players.

```bash
./starweb-admin view-bug-reports
./starweb-admin view-bug-reports --limit 50
```

Shows:
- Player name and ID
- Timestamp of submission
- Game turn when bug occurred
- Bug description
- Character type (for context)

Bug reports are stored in `data/bug_reports.jsonl` (JSON Lines format, one report per line).

## Workflow Examples

### Starting a New Game

```bash
# 1. View current configuration
./starweb-admin show-config

# 2. (Optional) Edit game_config.yaml to customize settings

# 3. Validate configuration
./starweb-admin validate-config

# 4. Initialize new game
./starweb-admin new-game

# 5. Start server
docker-compose up -d
# OR
python3 -m server.main
```

### Changing Game Settings Mid-Game

```bash
# 1. Backup current game
./starweb-admin backup-state

# 2. Edit game_config.yaml
nano game_config.yaml

# 3. Restart server to apply changes
docker-compose restart starweb-server
```

**Note**: Most config changes (like artifact points, turn timers) take effect on next game initialization. Some settings (like turn duration) are read dynamically.

### Recovering from Crashes

```bash
# Game state is auto-saved after each turn
# Just restart the server - it will load the latest state

docker-compose up -d

# If state is corrupted, restore from backup:
./starweb-admin restore-state data/gamestate.json.bak
```

### Monitoring Bug Reports

Players can submit bug reports from the game UI using the 🐛 button.

```bash
# View recent reports
./starweb-admin view-bug-reports

# View more reports
./starweb-admin view-bug-reports --limit 50

# Read raw reports file
cat data/bug_reports.jsonl | jq .

# Search for specific issues
grep "fleet" data/bug_reports.jsonl
```

**Tip**: Check bug reports regularly to identify common issues and improve the game.

### Testing Different Configurations

```bash
# Create a custom config
cp game_config.yaml test_config.yaml
nano test_config.yaml  # Edit settings

# Validate custom config
./starweb-admin validate-config --config test_config.yaml

# Use custom config (set environment variable)
export STARWEB_CONFIG=test_config.yaml
python3 -m server.main
```

## File Locations

```
starweb/
├── game_config.yaml              # Game configuration
├── starweb-admin                 # Admin CLI wrapper
├── server/
│   ├── cli.py                    # CLI implementation
│   └── config.py                 # Config loader
└── data/
    ├── gamestate.json            # Current game state
    ├── gamestate.json.bak        # Automatic backup
    └── gamestate.json.backup.*   # Manual backups
```

## Artifact Effects (Future Implementation)

The configuration supports artifact `effect` fields for future features:

- `navigation_bonus` - Extra movement range
- `stealth` - Harder to detect in combat
- `weapon_boost` - Increased combat damage
- `intelligence` - Reveal enemy information
- `curse` - Negative effects (already implemented via negative points)

To implement these effects, modify `server/game/combat.py` and `server/game/turn_processor.py` to check artifact effects during combat and movement.

## Advanced Configuration

### Custom Map Sizes

For smaller/faster games:

```yaml
game:
  map_size: 100          # Smaller galaxy

fleets:
  num_neutral_fleets: 100
```

For epic games:

```yaml
game:
  map_size: 500          # Huge galaxy
  default_turn_duration: 7200  # 2 hour turns

fleets:
  num_neutral_fleets: 500
```

### Tournament Mode

Quick games with aggressive settings:

```yaml
game:
  map_size: 150
  default_turn_duration: 1800    # 30 minute turns
  default_target_score: 5000     # Lower victory threshold

worlds:
  min_connections: 3
  max_connections: 5              # More connected map

game:
  homeworld:
    ships_per_fleet: 50           # Stronger starting position
```

## Troubleshooting

### "Config file not found"

Make sure `game_config.yaml` exists in the project root:

```bash
ls game_config.yaml
```

### "Failed to load configuration"

Validate YAML syntax:

```bash
./starweb-admin validate-config
```

Common issues:
- Inconsistent indentation (use spaces, not tabs)
- Missing colons after keys
- Unquoted strings with special characters

### "Game state failed validation"

The saved state may be corrupted. Restore from backup:

```bash
./starweb-admin restore-state data/gamestate.json.bak
```

### Changes not taking effect

Some settings require game restart:

```bash
docker-compose restart starweb-server
```

Or for fresh game with new settings:

```bash
./starweb-admin new-game
docker-compose restart starweb-server
```

## Security Notes

- Game config files are not validated for malicious content
- Only run `./starweb-admin` with trusted configuration files
- Backup game state before making major changes
- Keep backups in secure location for important games

## Support

For issues or questions:
- Check logs: `docker-compose logs -f starweb-server`
- File issues: https://github.com/anthropics/claude-code/issues
