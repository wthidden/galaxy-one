#!/bin/bash
# StarWeb Docker Server Reset Script
# Stops Docker containers, clears all data, and restarts

echo "===================================================="
echo "StarWeb Docker Server Reset"
echo "===================================================="
echo ""
echo "This will:"
echo "  - Stop Docker containers"
echo "  - Delete all game data (games, accounts, state)"
echo "  - Restart containers with fresh state"
echo ""
read -p "Continue? (yes/no): " confirm

if [ "$confirm" != "yes" ] && [ "$confirm" != "y" ]; then
    echo "Cancelled."
    exit 0
fi

echo ""
echo "Stopping Docker containers..."
docker-compose down

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
echo "✓ Containers stopped"
echo "✓ Data cleared"
echo "✓ Backup saved to: $BACKUP_DIR"
echo ""
echo "Starting Docker containers..."
docker-compose up -d

echo ""
echo "Waiting for server to initialize..."
sleep 5

# Check if containers are running
if docker-compose ps | grep -q "Up"; then
    echo "✓ Server started successfully"
    echo ""
    echo "Server is now accessible at:"
    echo "  - WebSocket: ws://your-domain:8765"
    echo "  - HTTP: http://your-domain (via nginx)"
    echo ""
    echo "Check logs with: docker-compose logs -f starweb-server"
else
    echo "✗ Failed to start containers"
    echo "Check logs with: docker-compose logs starweb-server"
    exit 1
fi

echo ""
echo "===================================================="
echo "Reset complete!"
echo "===================================================="
