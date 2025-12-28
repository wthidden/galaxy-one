# StarWeb Deployment Guide

## Current Architecture Analysis

**Technology Stack:**
- **Backend**: Python WebSocket server (asyncio + websockets)
- **Frontend**: Static HTML/CSS/JavaScript (no build step)
- **State**: In-memory (no database)
- **Real-time**: WebSocket connections for multiplayer

**Current Limitations:**
- ❌ No persistence (game state lost on restart)
- ❌ No user accounts/authentication
- ❌ Single game instance only
- ❌ No SSL/HTTPS support
- ⚠️ No production-ready server configuration

---

## Recommended Deployment Strategies

### 🚀 Option 1: Quick Start (Railway/Render) **[RECOMMENDED FOR MVP]**

**Best for**: Getting online quickly, testing with real players

**Platforms**:
- [Railway.app](https://railway.app) - Easiest, $5-10/month
- [Render.com](https://render.com) - Free tier available
- [Fly.io](https://fly.io) - Good WebSocket support

#### Pros:
- ✅ Deploy in minutes
- ✅ Automatic SSL/HTTPS
- ✅ Free tier available (Render, Fly.io)
- ✅ Git integration (auto-deploy on push)
- ✅ Easy environment variables

#### Cons:
- ⚠️ Can be expensive as you scale
- ⚠️ Platform lock-in
- ⚠️ Less control over infrastructure

#### Implementation Steps:

**1. Add Production Server**

Create `server/main.py`:
```python
import asyncio
import os
from server.websocket_handler import WebSocketHandler

async def main():
    # Get port from environment (Railway/Render provide this)
    port = int(os.environ.get("PORT", 8765))
    host = "0.0.0.0"  # Listen on all interfaces

    handler = WebSocketHandler()

    print(f"Starting StarWeb server on {host}:{port}")

    async with websockets.serve(handler.handle_connection, host, port):
        await asyncio.Future()  # Run forever

if __name__ == "__main__":
    asyncio.run(main())
```

**2. Add Procfile (for Railway/Render)**
```
web: python -m server.main
```

**3. Update requirements.txt**
```
websockets>=12.0
```

**4. Deploy on Railway:**
```bash
# Install Railway CLI
npm install -g @railway/cli

# Login and deploy
railway login
railway init
railway up
```

**5. Configure Environment Variables:**
- `PORT`: Auto-set by platform
- `TURN_DURATION`: 180 (3 minutes)
- `MAX_PLAYERS`: 10

**Cost**: ~$5-10/month

---

### 🐳 Option 2: Docker + VPS **[RECOMMENDED FOR PRODUCTION]**

**Best for**: Full control, cost efficiency, production deployment

**Platforms**:
- DigitalOcean Droplet ($6-12/month)
- Linode ($5-10/month)
- AWS EC2 (t3.micro ~$8/month)
- Hetzner Cloud ($4-8/month, Europe)

#### Pros:
- ✅ Full control
- ✅ Very cost-effective
- ✅ Easy to scale
- ✅ Portable (works anywhere)
- ✅ Can run multiple games

#### Cons:
- ⚠️ Requires server management
- ⚠️ Need to set up SSL manually
- ⚠️ More initial setup

#### Implementation Files:

**1. Create Dockerfile:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose WebSocket port
EXPOSE 8765

# Run server
CMD ["python", "-m", "server.main"]
```

**2. Create docker-compose.yml:**
```yaml
version: '3.8'

services:
  starweb-server:
    build: .
    ports:
      - "8765:8765"
    environment:
      - PORT=8765
      - TURN_DURATION=180
    restart: unless-stopped
    volumes:
      - ./data:/app/data  # For future persistence
    networks:
      - starweb-net

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - ./client:/usr/share/nginx/html
      - ./certbot/conf:/etc/letsencrypt
      - ./certbot/www:/var/www/certbot
    depends_on:
      - starweb-server
    networks:
      - starweb-net

networks:
  starweb-net:
```

**3. Create nginx.conf:**
```nginx
events {
    worker_connections 1024;
}

http {
    upstream starweb_backend {
        server starweb-server:8765;
    }

    server {
        listen 80;
        server_name yourdomain.com;

        # Static files
        location / {
            root /usr/share/nginx/html;
            try_files $uri $uri/ /index.html;
        }

        # WebSocket proxy
        location /ws {
            proxy_pass http://starweb_backend;
            proxy_http_version 1.1;
            proxy_set_header Upgrade $http_upgrade;
            proxy_set_header Connection "upgrade";
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
            proxy_read_timeout 86400;
        }
    }
}
```

**4. Deploy to VPS:**
```bash
# On your VPS
git clone your-repo
cd starweb

# Install Docker & Docker Compose
curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh

# Start the application
docker-compose up -d

# Get SSL certificate (Let's Encrypt)
docker run -it --rm \
  -v ./certbot/conf:/etc/letsencrypt \
  -v ./certbot/www:/var/www/certbot \
  certbot/certbot certonly --webroot \
  -w /var/www/certbot \
  -d yourdomain.com
```

**Cost**: ~$5-12/month

---

### ☁️ Option 3: Serverless (NOT RECOMMENDED)

**Why not?**
- WebSocket connections require persistent servers
- Serverless (Lambda, Cloud Functions) are for short-lived requests
- Would need AWS API Gateway WebSocket or similar (complex, expensive)

---

## Critical Pre-Deployment Tasks

### 1. Add Persistence (Database)

**Current Issue**: Game state lost on server restart

**Solution**: Add PostgreSQL or SQLite

**Quick SQLite Implementation:**

Create `server/database.py`:
```python
import sqlite3
import json
from typing import Optional

class GameDatabase:
    def __init__(self, db_path="data/starweb.db"):
        self.db_path = db_path
        self.init_db()

    def init_db(self):
        """Create tables if they don't exist"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS game_state (
                id INTEGER PRIMARY KEY,
                turn INTEGER,
                state_json TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS players (
                id INTEGER PRIMARY KEY,
                name TEXT UNIQUE,
                character_type TEXT,
                score INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    def save_game_state(self, turn: int, state: dict):
        """Save current game state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "INSERT INTO game_state (turn, state_json) VALUES (?, ?)",
            (turn, json.dumps(state))
        )

        conn.commit()
        conn.close()

    def load_latest_game_state(self) -> Optional[dict]:
        """Load most recent game state"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        cursor.execute(
            "SELECT state_json FROM game_state ORDER BY turn DESC LIMIT 1"
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            return json.loads(row[0])
        return None
```

### 2. Add Environment Configuration

Create `.env.example`:
```bash
# Server Configuration
PORT=8765
HOST=0.0.0.0

# Game Settings
TURN_DURATION=180
MAX_TURN_DURATION=480
MAX_PLAYERS=10
MAP_SIZE=255

# Database
DATABASE_URL=sqlite:///data/starweb.db

# Security
ALLOWED_ORIGINS=https://yourdomain.com
SESSION_SECRET=your-secret-key-here
```

### 3. Add Health Check Endpoint

Add to server:
```python
async def health_check(websocket, path):
    if path == "/health":
        await websocket.send(json.dumps({"status": "ok", "players": len(players)}))
        await websocket.close()
```

### 4. Add Proper Logging

```python
import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('starweb.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger('starweb')
```

---

## Domain & SSL Setup

### 1. Get a Domain Name
- **Namecheap**: ~$10/year
- **Google Domains**: ~$12/year
- **Cloudflare**: ~$10/year (includes DDoS protection)

### 2. Point Domain to Server
```
A Record: @ -> YOUR_SERVER_IP
CNAME: www -> yourdomain.com
```

### 3. Get SSL Certificate (Free)

**Using Let's Encrypt:**
```bash
# Install certbot
sudo apt install certbot python3-certbot-nginx

# Get certificate
sudo certbot --nginx -d yourdomain.com -d www.yourdomain.com

# Auto-renewal
sudo certbot renew --dry-run
```

---

## Multi-Game Support (Future Enhancement)

**Current**: Single game instance
**Future**: Multiple game rooms

### Game Lobby System

Create `server/lobby.py`:
```python
class GameLobby:
    def __init__(self):
        self.games = {}  # game_id -> GameState
        self.waiting_players = []

    def create_game(self, game_id: str, settings: dict):
        """Create a new game room"""
        self.games[game_id] = GameState(settings)

    def join_game(self, game_id: str, player):
        """Add player to specific game"""
        if game_id in self.games:
            self.games[game_id].add_player(player)

    def list_games(self):
        """Return list of active games"""
        return [
            {
                "id": gid,
                "players": len(game.players),
                "turn": game.game_turn,
                "status": game.status
            }
            for gid, game in self.games.items()
        ]
```

Update client to show lobby:
```javascript
// Connect to lobby
const lobbyWs = new WebSocket('wss://yourdomain.com/lobby');

// List games
lobbyWs.send(JSON.stringify({ action: 'list_games' }));

// Create game
lobbyWs.send(JSON.stringify({
    action: 'create_game',
    settings: { map_size: 255, turn_duration: 180 }
}));

// Join game
lobbyWs.send(JSON.stringify({
    action: 'join_game',
    game_id: 'game-123'
}));
```

---

## Monitoring & Analytics

### Basic Monitoring

**1. Server Health:**
```bash
# Check if server is running
curl https://yourdomain.com/health

# Monitor logs
tail -f starweb.log

# Docker logs
docker-compose logs -f starweb-server
```

**2. Player Analytics:**
```python
# Add to server
async def log_player_action(player, action):
    logger.info(f"Player {player.name} - {action}")

    # Optional: Send to analytics service
    # analytics.track(player.id, action)
```

**3. Uptime Monitoring:**
- [UptimeRobot](https://uptimerobot.com) - Free tier
- [Pingdom](https://pingdom.com)
- [StatusCake](https://statuscake.com)

---

## Performance Optimization

### 1. Enable Gzip Compression
```nginx
gzip on;
gzip_types text/plain text/css application/json application/javascript;
gzip_min_length 1000;
```

### 2. Cache Static Assets
```nginx
location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg)$ {
    expires 1y;
    add_header Cache-Control "public, immutable";
}
```

### 3. WebSocket Connection Limits
```python
# Limit connections per IP
from collections import defaultdict

connection_counts = defaultdict(int)
MAX_CONNECTIONS_PER_IP = 5

async def handle_connection(websocket, path):
    ip = websocket.remote_address[0]

    if connection_counts[ip] >= MAX_CONNECTIONS_PER_IP:
        await websocket.close(1008, "Too many connections")
        return

    connection_counts[ip] += 1
    try:
        # Handle connection
        pass
    finally:
        connection_counts[ip] -= 1
```

---

## Security Considerations

### 1. Rate Limiting
```python
from time import time

class RateLimiter:
    def __init__(self, max_requests=10, window=60):
        self.max_requests = max_requests
        self.window = window
        self.requests = defaultdict(list)

    def is_allowed(self, identifier):
        now = time()
        # Remove old requests
        self.requests[identifier] = [
            req for req in self.requests[identifier]
            if now - req < self.window
        ]

        if len(self.requests[identifier]) >= self.max_requests:
            return False

        self.requests[identifier].append(now)
        return True
```

### 2. Input Validation
```python
def validate_command(command: str) -> bool:
    # Limit command length
    if len(command) > 200:
        return False

    # Only allow alphanumeric + basic chars
    if not re.match(r'^[A-Z0-9\s]+$', command.upper()):
        return False

    return True
```

### 3. WebSocket Origin Checking
```python
async def check_origin(websocket):
    origin = websocket.request_headers.get("Origin")
    allowed_origins = os.environ.get("ALLOWED_ORIGINS", "").split(",")

    if origin not in allowed_origins:
        await websocket.close(1008, "Invalid origin")
        return False

    return True
```

---

## Deployment Checklist

### Pre-Launch:
- [ ] Test game with 2-4 players locally
- [ ] Add database persistence
- [ ] Set up error logging
- [ ] Add health check endpoint
- [ ] Configure environment variables
- [ ] Test WebSocket reconnection
- [ ] Add rate limiting
- [ ] Validate all user inputs

### Infrastructure:
- [ ] Choose deployment platform
- [ ] Get domain name
- [ ] Configure DNS
- [ ] Set up SSL certificate
- [ ] Configure firewall (ports 80, 443, 8765)
- [ ] Set up backups (database)
- [ ] Configure monitoring/uptime checks

### Post-Launch:
- [ ] Monitor server logs
- [ ] Track player count
- [ ] Monitor WebSocket connections
- [ ] Check database size
- [ ] Set up automated backups
- [ ] Plan for scaling

---

## Cost Breakdown

### Option 1: Railway (Easiest)
- **Platform**: $5-10/month
- **Domain**: $10/year
- **Total**: ~$6-11/month

### Option 2: VPS (Best Value)
- **VPS**: $5-12/month (DigitalOcean/Linode)
- **Domain**: $10/year
- **Total**: ~$6-13/month

### Option 3: Premium (Scale Ready)
- **VPS**: $12-20/month (larger instance)
- **Database**: $15/month (managed PostgreSQL)
- **CDN**: $5-10/month (Cloudflare Pro)
- **Monitoring**: $10/month (Datadog/NewRelic)
- **Total**: ~$42-55/month

---

## Recommended Deployment Path

### Phase 1: MVP (Week 1)
1. Deploy on Railway or Render
2. Get basic domain + SSL
3. Add simple SQLite persistence
4. Test with friends

**Cost**: ~$5-10/month

### Phase 2: Production (Month 1-2)
1. Move to VPS with Docker
2. Add PostgreSQL database
3. Implement game lobby system
4. Set up monitoring
5. Add user accounts

**Cost**: ~$10-15/month

### Phase 3: Scale (Month 3+)
1. Load balancer for multiple servers
2. Redis for session management
3. CDN for static assets
4. Advanced analytics
5. Premium features

**Cost**: ~$30-50/month

---

## Quick Start: Deploy to Railway in 5 Minutes

```bash
# 1. Install Railway CLI
npm install -g @railway/cli

# 2. Login to Railway
railway login

# 3. Initialize project
railway init

# 4. Set environment variables
railway variables set PORT=8765
railway variables set TURN_DURATION=180

# 5. Deploy!
railway up

# 6. Get your URL
railway domain
```

Done! Your game is now live at `https://your-project.railway.app`

---

## Need Help?

**Common Issues:**
- **WebSocket not connecting**: Check firewall, nginx config
- **Game state lost**: Add database persistence
- **Slow performance**: Enable compression, add CDN
- **Too expensive**: Start with VPS instead of PaaS

**Resources:**
- [WebSocket Deployment Guide](https://websockets.readthedocs.io/en/stable/deployment.html)
- [Let's Encrypt Certbot](https://certbot.eff.org/)
- [Railway Documentation](https://docs.railway.app/)
- [Docker Compose Docs](https://docs.docker.com/compose/)

---

**Recommendation**: Start with **Railway** for MVP, then migrate to **VPS + Docker** when you have regular players and want to save costs.
