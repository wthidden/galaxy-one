# StarWeb Quick Deployment Guide

## Choose Your Deployment Method

### 🚀 Method 1: Railway (Easiest - 5 Minutes)

**Perfect for**: Testing, small groups, getting online fast

1. **Sign up at [Railway.app](https://railway.app)**

2. **Install Railway CLI:**
   ```bash
   npm install -g @railway/cli
   railway login
   ```

3. **Deploy:**
   ```bash
   cd starweb
   railway init
   railway up
   ```

4. **Get your URL:**
   ```bash
   railway domain
   ```

5. **Update WebSocket URL in client:**
   Edit `client/network/WebSocketClient.js`:
   ```javascript
   // Change from:
   this.url = 'ws://localhost:8765';
   // To:
   this.url = 'wss://your-project.railway.app';
   ```

6. **Redeploy:**
   ```bash
   railway up
   ```

**Cost**: ~$5-10/month
**Setup time**: 5 minutes
**Pros**: Automatic SSL, easy updates
**Cons**: Can get expensive

---

### 🐳 Method 2: VPS with Docker (Best Value)

**Perfect for**: Production, cost-effective hosting, full control

#### Step 1: Get a VPS

Choose a provider:
- **DigitalOcean**: Create droplet ($6/mo) - [Sign up](https://digitalocean.com)
- **Linode**: Create Linode ($5/mo) - [Sign up](https://linode.com)
- **Hetzner**: Create Cloud Server ($4/mo) - [Sign up](https://hetzner.com)

Requirements: Ubuntu 22.04, 1GB RAM, 25GB storage

#### Step 2: Get a Domain (Optional but recommended)

- **Namecheap**: ~$10/year
- **Google Domains**: ~$12/year

Point domain to your VPS:
```
A Record:  @     -> YOUR_VPS_IP
A Record:  www   -> YOUR_VPS_IP
```

#### Step 3: Deploy

SSH into your VPS:
```bash
ssh root@YOUR_VPS_IP
```

Clone the repository:
```bash
git clone https://github.com/yourusername/starweb.git
cd starweb
```

Run deployment script:
```bash
./deploy.sh
```

Update WebSocket URL in `client/network/WebSocketClient.js`:
```javascript
this.url = 'ws://YOUR_VPS_IP:8765';
// Or with domain:
this.url = 'wss://yourdomain.com/ws';
```

Rebuild:
```bash
docker-compose down
docker-compose up --build -d
```

#### Step 4: Get SSL (if you have a domain)

```bash
./setup-ssl.sh yourdomain.com
```

**Done!** Visit `https://yourdomain.com`

**Cost**: ~$5-6/month
**Setup time**: 15-20 minutes
**Pros**: Cheap, full control, scalable
**Cons**: Requires some Linux knowledge

---

## Post-Deployment Checklist

### 1. Test the Game

- [ ] Open game in browser
- [ ] Join with a player name
- [ ] Create some fleets/worlds
- [ ] Submit turn
- [ ] Verify WebSocket connection works

### 2. Monitor

Check logs:
```bash
# Railway
railway logs

# Docker
docker-compose logs -f starweb-server
```

Check running containers:
```bash
docker-compose ps
```

### 3. Backup (Important!)

Create backup script `/root/backup-starweb.sh`:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
tar -czf /root/backups/starweb_$DATE.tar.gz /path/to/starweb/data
# Keep last 7 days
find /root/backups -name "starweb_*.tar.gz" -mtime +7 -delete
```

Make executable and add to cron:
```bash
chmod +x /root/backup-starweb.sh
crontab -e
# Add: 0 2 * * * /root/backup-starweb.sh
```

---

## Troubleshooting

### WebSocket Won't Connect

**Problem**: Client can't connect to server

**Solution**:
1. Check WebSocket URL in `client/network/WebSocketClient.js`
2. Verify port 8765 is open: `sudo ufw allow 8765`
3. Check server is running: `docker-compose ps`
4. View logs: `docker-compose logs starweb-server`

### "Connection Refused"

**Problem**: Can't reach server at all

**Solution**:
1. Check firewall: `sudo ufw status`
2. Allow ports: `sudo ufw allow 80 && sudo ufw allow 443 && sudo ufw allow 8765`
3. Check nginx is running: `docker-compose ps nginx`

### SSL Certificate Fails

**Problem**: `setup-ssl.sh` fails

**Solution**:
1. Verify DNS: `dig +short yourdomain.com` (should show your server IP)
2. Check port 80 is open and not in use
3. Stop nginx: `docker-compose stop nginx`
4. Try again: `./setup-ssl.sh yourdomain.com`

### Game State Lost on Restart

**Problem**: Players and worlds disappear when server restarts

**Solution**:
Currently the game uses in-memory storage. To add persistence:
1. See `DEPLOYMENT_GUIDE.md` section on "Add Persistence"
2. Or wait for database support in future version

### Players Can't Join

**Problem**: Players get error when trying to join

**Solution**:
1. Check server logs: `docker-compose logs starweb-server`
2. Verify WebSocket connection in browser console (F12)
3. Check if game is full (MAX_PLAYERS limit)

---

## Updating Your Deployment

### Railway

```bash
git pull
railway up
```

### Docker/VPS

```bash
cd starweb
git pull
docker-compose down
docker-compose up --build -d
```

---

## Useful Commands

### Railway

```bash
railway logs              # View logs
railway logs -f           # Follow logs
railway status            # Check status
railway variables         # List environment variables
railway variables set KEY=VALUE  # Set variable
railway domain            # Get your URL
```

### Docker

```bash
docker-compose ps         # List containers
docker-compose logs -f    # View logs
docker-compose restart    # Restart all services
docker-compose stop       # Stop all services
docker-compose down       # Stop and remove containers
docker-compose up -d      # Start in background
```

### Server Monitoring

```bash
# Check disk space
df -h

# Check memory
free -h

# Check processes
htop

# View nginx logs
docker-compose logs nginx

# View game server logs
docker-compose logs starweb-server
```

---

## Performance Tips

### For VPS:

1. **Enable UFW (firewall):**
   ```bash
   sudo ufw allow 22
   sudo ufw allow 80
   sudo ufw allow 443
   sudo ufw allow 8765
   sudo ufw enable
   ```

2. **Set up swap (if low memory):**
   ```bash
   sudo fallocate -l 2G /swapfile
   sudo chmod 600 /swapfile
   sudo mkswap /swapfile
   sudo swapon /swapfile
   echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
   ```

3. **Auto-restart on crash:**
   Already configured in `docker-compose.yml`:
   ```yaml
   restart: unless-stopped
   ```

---

## Scaling Up

When you get more players:

### 1. Upgrade Server Resources
- Railway: Automatic scaling
- VPS: Upgrade to larger droplet/linode

### 2. Add Database
- PostgreSQL for persistent storage
- See full guide in `DEPLOYMENT_GUIDE.md`

### 3. Add CDN
- Cloudflare (free tier)
- Speeds up static file delivery

### 4. Monitor Performance
- Set up monitoring: UptimeRobot (free)
- Track players and performance

---

## Cost Comparison

| Method | Monthly Cost | Setup Time | Difficulty |
|--------|-------------|------------|-----------|
| Railway | $5-10 | 5 min | ⭐ Easy |
| DigitalOcean VPS | $6 | 20 min | ⭐⭐ Medium |
| Linode VPS | $5 | 20 min | ⭐⭐ Medium |
| Hetzner Cloud | $4 | 20 min | ⭐⭐ Medium |

**Recommendation**:
- Start with **Railway** for instant deployment
- Move to **VPS** when you have regular players to save money

---

## Next Steps

After deployment:
1. ✅ Share the URL with friends
2. ✅ Set up monitoring (UptimeRobot)
3. ✅ Add database persistence (see full guide)
4. ✅ Create game lobby system for multiple games
5. ✅ Add player accounts and authentication

See `DEPLOYMENT_GUIDE.md` for advanced topics!

---

## Need Help?

- Check logs first: `docker-compose logs -f`
- Review full guide: `DEPLOYMENT_GUIDE.md`
- GitHub Issues: Report bugs and ask questions
- Test locally first: `python server.py`

**Happy deploying! 🚀**
