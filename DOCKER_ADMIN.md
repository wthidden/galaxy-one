# StarWeb Docker Admin Commands

## Production Deployment via Docker

Your StarWeb server runs in Docker containers:
- **starweb-server**: Python WebSocket server (port 8765)
- **nginx**: Web server serving static files and proxying requests (ports 80/443)

Data is persisted in the `./data` directory which is mounted as a Docker volume.

## Quick Reset (Recommended)

```bash
./reset_docker.sh
```

This will:
1. Stop Docker containers
2. Backup all data to `data/backups/`
3. Clear all game data
4. Restart containers with fresh state

## Manual Docker Commands

### View Running Containers
```bash
docker-compose ps
```

### View Server Logs
```bash
# Follow logs in real-time
docker-compose logs -f starweb-server

# View last 50 lines
docker-compose logs --tail=50 starweb-server

# View nginx logs
docker-compose logs -f nginx
```

### Restart Server
```bash
# Restart just the game server
docker-compose restart starweb-server

# Restart all containers
docker-compose restart
```

### Stop/Start
```bash
# Stop all containers
docker-compose down

# Start all containers
docker-compose up -d

# Rebuild and start (after code changes)
docker-compose up -d --build
```

### Reset Game Data (Manual)

```bash
# Stop containers
docker-compose down

# Backup current data
mkdir -p data/backups/manual_$(date +%Y%m%d_%H%M%S)
cp data/*.json data/backups/manual_$(date +%Y%m%d_%H%M%S)/ 2>/dev/null || true

# Clear data
rm -f data/gamestate.json data/accounts.json data/sessions.json data/games.json

# Restart
docker-compose up -d
```

## CLI Commands (via Docker)

You can run CLI commands inside the Docker container:

### Reset Everything
```bash
# Execute CLI command in container
docker-compose exec starweb-server python3 -m server.cli reset-all --force

# Then restart to apply changes
docker-compose restart starweb-server
```

### Create New Game Map
```bash
docker-compose exec starweb-server python3 -m server.cli new-game --force
docker-compose restart starweb-server
```

### View Configuration
```bash
docker-compose exec starweb-server python3 -m server.cli show-config
```

### View Bug Reports
```bash
docker-compose exec starweb-server python3 -m server.cli view-bug-reports --limit 50
```

### Backup Current State
```bash
docker-compose exec starweb-server python3 -m server.cli backup-state
```

## Update Admin Message

Edit the admin message that players see:

```bash
# Edit the message file (changes are live-reloaded)
nano admin_message.txt

# No restart needed - changes are detected automatically
```

## Deployment Updates

### Update Code and Restart
```bash
# Pull latest code
git pull

# Rebuild and restart containers
docker-compose up -d --build

# View logs to verify
docker-compose logs -f starweb-server
```

### Update Just Static Files (HTML/CSS/JS)
```bash
# No rebuild needed - nginx serves files directly
# Just refresh browser with Ctrl+Shift+R (hard refresh)
```

## Monitor Server Health

### Check if Server is Running
```bash
# Check containers
docker-compose ps

# Check if WebSocket is responding
curl -i http://localhost:8765
# Should get: "Upgrade required" error (that's normal - it needs WebSocket)

# Check nginx
curl http://localhost
# Should return HTML
```

### Check Resource Usage
```bash
# Container stats
docker stats

# Or just StarWeb containers
docker stats starweb-server nginx
```

### Verify Data Persistence
```bash
# List data files
ls -lh data/

# View game state info
cat data/gamestate.json | python3 -m json.tool | head -50
```

## Troubleshooting

### Server Won't Start
```bash
# Check logs
docker-compose logs starweb-server

# Check if ports are in use
lsof -ti:8765
lsof -ti:80

# Kill local development server if running
lsof -ti:8000 | xargs kill -9
```

### Data Not Persisting
```bash
# Verify volume mount
docker-compose config | grep -A5 volumes

# Check data directory permissions
ls -ld data/
# Should be writable by Docker user
```

### Container Keeps Restarting
```bash
# View full logs
docker-compose logs starweb-server

# Check for Python errors in startup
docker-compose logs starweb-server | grep -i error

# Try running interactively to see errors
docker-compose run --rm starweb-server python3 -m server.main
```

## Production URLs

After deployment, your server is accessible at:
- **WebSocket**: `ws://your-domain:8765` or `wss://your-domain:8765` (with SSL)
- **Web Interface**: `http://your-domain` or `https://your-domain` (via nginx)

The localhost:8000 server is only for local development and is **NOT accessible remotely**.

## Quick Reference

| Task | Command |
|------|---------|
| Full reset | `./reset_docker.sh` |
| View logs | `docker-compose logs -f starweb-server` |
| Restart server | `docker-compose restart starweb-server` |
| Stop all | `docker-compose down` |
| Start all | `docker-compose up -d` |
| Rebuild & start | `docker-compose up -d --build` |
| Edit admin msg | `nano admin_message.txt` |
| View config | `docker-compose exec starweb-server python3 -m server.cli show-config` |
| Shell access | `docker-compose exec starweb-server /bin/bash` |
