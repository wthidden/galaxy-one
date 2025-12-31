#!/bin/bash
# StarWeb Server Reset Script
# Stops server, clears all data, and optionally restarts

echo "===================================================="
echo "StarWeb Server Reset"
echo "===================================================="
echo ""
echo "This will:"
echo "  - Stop the running server"
echo "  - Delete all game data (games, accounts, state)"
echo "  - Optionally restart with fresh state"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Stopping server..."
# Kill processes on ports 8765 and 8000
lsof -ti:8765 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
sleep 1

echo "Backing up current data..."
BACKUP_DIR="data/backups/reset_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"

if [ -f "data/gamestate.json" ]; then
    cp data/gamestate.json "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -f "data/accounts.json" ]; then
    cp data/accounts.json "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -f "data/sessions.json" ]; then
    cp data/sessions.json "$BACKUP_DIR/" 2>/dev/null || true
fi
if [ -f "data/games.json" ]; then
    cp data/games.json "$BACKUP_DIR/" 2>/dev/null || true
fi

echo "Backed up to: $BACKUP_DIR"

echo "Clearing data files..."
rm -f data/gamestate.json
rm -f data/accounts.json
rm -f data/sessions.json
rm -f data/games.json

echo ""
echo "✓ Server stopped"
echo "✓ Data cleared"
echo "✓ Backup saved to: $BACKUP_DIR"
echo ""
read -p "Start server now? (yes/no): " start_server

if [ "$start_server" == "yes" ] || [ "$start_server" == "y" ]; then
    echo ""
    echo "Starting server..."
    python3 -m server.main &
    sleep 2
    echo "✓ Server started on http://localhost:8000"
else
    echo ""
    echo "Server not started. Run 'python3 -m server.main' to start manually."
fi

echo ""
echo "===================================================="
echo "Reset complete!"
echo "===================================================="
