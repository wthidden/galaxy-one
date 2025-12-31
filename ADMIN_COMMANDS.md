# StarWeb Admin Commands

**⚠️ PRODUCTION SERVERS**: If you're running via Docker (docker-compose), use **[DOCKER_ADMIN.md](DOCKER_ADMIN.md)** instead!

This guide is for **local development** only (running `python3 -m server.main` directly).

---

## Quick Reset (Recommended)

The easiest way to reset everything:

```bash
./reset_server.sh
```

This will:
- Stop the running server
- Backup all current data
- Clear all games, accounts, and state
- Optionally restart the server

**Note**: This only works for local development, not Docker deployments.

## CLI Commands

These commands should be run **while the server is STOPPED**.

### Reset Everything
```bash
# Stop server first
lsof -ti:8765 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Reset all data (creates backup)
python3 -m server.cli reset-all

# Or skip confirmation
python3 -m server.cli reset-all --force

# Restart server
python3 -m server.main
```

### Create New Game (Just Map)
```bash
# Stop server first
lsof -ti:8765 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Create new game map
python3 -m server.cli new-game

# Or skip confirmation
python3 -m server.cli new-game --force

# Restart server
python3 -m server.main
```

### View Configuration
```bash
python3 -m server.cli show-config
```

### Backup Current State
```bash
python3 -m server.cli backup-state
# Or specify output file
python3 -m server.cli backup-state --output my-backup.json
```

### Restore from Backup
```bash
# Stop server first
lsof -ti:8765 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Restore
python3 -m server.cli restore-state data/backups/reset_20250101_120000/gamestate.json

# Restart server
python3 -m server.main
```

### View Bug Reports
```bash
# View last 20 bug reports
python3 -m server.cli view-bug-reports

# View last 50
python3 -m server.cli view-bug-reports --limit 50
```

## Data Files

The server stores data in the `data/` directory:

- `gamestate.json` - Current game universe (worlds, fleets, artifacts)
- `accounts.json` - Player accounts
- `sessions.json` - Active login sessions
- `games.json` - Multi-game lobby instances (if implemented)

Backups are saved to `data/backups/`.

## Common Scenarios

### Start Completely Fresh
```bash
./reset_server.sh
# Select "yes" to confirm
# Select "yes" to restart
```

### Keep Accounts, Reset Game
```bash
# Stop server
lsof -ti:8765 | xargs kill -9
lsof -ti:8000 | xargs kill -9

# Delete only game state
rm data/gamestate.json

# Restart - new map will be generated
python3 -m server.main
```

### Testing: Quick Reset Loop
```bash
# Add this to a script for rapid testing
while true; do
    lsof -ti:8765 | xargs kill -9 2>/dev/null
    lsof -ti:8000 | xargs kill -9 2>/dev/null
    rm -f data/*.json
    python3 -m server.main
    read -p "Press enter to reset again (Ctrl+C to stop)..."
done
```

## Notes

- Always **stop the server** before running CLI commands
- CLI commands automatically create backups before deleting data
- Backups include timestamps for easy identification
- The `--force` flag skips confirmation prompts (useful for scripts)
