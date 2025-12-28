# StarWeb VPS Setup - Step by Step

## Overview

This guide will walk you through deploying StarWeb on a VPS from scratch.

**Time required**: 30-45 minutes
**Cost**: $4-6/month
**Result**: Production-ready game server with SSL

---

## Step 1: Choose and Create Your VPS

### Recommended Providers

#### Option A: DigitalOcean ($6/month)
- **Best for**: Beginners, great documentation
- **Sign up**: https://digitalocean.com
- **Droplet to create**: Basic Droplet
  - Image: Ubuntu 22.04 LTS
  - Plan: Basic ($6/mo - 1GB RAM, 25GB SSD)
  - Datacenter: Closest to your players
  - Authentication: SSH keys (recommended) or password

#### Option B: Linode ($5/month)
- **Best for**: Value, excellent support
- **Sign up**: https://linode.com
- **Linode to create**: Shared CPU
  - Distribution: Ubuntu 22.04 LTS
  - Plan: Nanode 1GB ($5/mo)
  - Region: Closest to your players

#### Option C: Hetzner Cloud ($4/month - Europe)
- **Best for**: Best price, Europe-based
- **Sign up**: https://hetzner.com/cloud
- **Server to create**: CX11
  - Image: Ubuntu 22.04
  - Type: CX11 (€3.79/mo ~ $4/mo)
  - Location: Closest to your players

#### Option D: Vultr ($6/month)
- **Best for**: Global locations
- **Sign up**: https://vultr.com
- **Cloud Compute**: Regular Performance
  - OS: Ubuntu 22.04
  - Plan: 1GB RAM ($6/mo)

### What You'll Get

After creating your VPS, you'll receive:
- **IP Address**: e.g., 159.89.123.45
- **Root Password**: (if not using SSH keys)
- **SSH Access**: Port 22

**Write these down!**

---

## Step 2: Initial Server Setup

### 2.1 Connect to Your Server

**On Mac/Linux:**
```bash
ssh root@YOUR_SERVER_IP
# Enter password when prompted
```

**On Windows:**
- Use **PuTTY** or **Windows Terminal**
```powershell
ssh root@YOUR_SERVER_IP
```

### 2.2 Update System

```bash
# Update package list
apt update

# Upgrade packages
apt upgrade -y

# Install essential tools
apt install -y git curl wget ufw
```

### 2.3 Set Up Firewall

```bash
# Allow SSH (IMPORTANT: Do this first!)
ufw allow 22

# Allow HTTP/HTTPS
ufw allow 80
ufw allow 443

# Allow WebSocket port
ufw allow 8765

# Enable firewall
ufw enable

# Check status
ufw status
```

You should see:
```
Status: active

To                         Action      From
--                         ------      ----
22                         ALLOW       Anywhere
80                         ALLOW       Anywhere
443                        ALLOW       Anywhere
8765                       ALLOW       Anywhere
```

### 2.4 Create Non-Root User (Optional but Recommended)

```bash
# Create user
adduser starweb

# Add to sudo group
usermod -aG sudo starweb

# Switch to new user
su - starweb
```

---

## Step 3: Install Docker & Docker Compose

### 3.1 Install Docker

```bash
# Download Docker installation script
curl -fsSL https://get.docker.com -o get-docker.sh

# Run installation
sudo sh get-docker.sh

# Add current user to docker group (if not root)
sudo usermod -aG docker $USER

# Clean up
rm get-docker.sh

# Verify installation
docker --version
```

### 3.2 Install Docker Compose

```bash
# Download Docker Compose
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Make executable
sudo chmod +x /usr/local/bin/docker-compose

# Verify installation
docker-compose --version
```

You should see something like:
```
Docker Compose version v2.24.0
```

---

## Step 4: Deploy StarWeb

### 4.1 Clone Repository

**Option A: From GitHub (if you've pushed your code)**
```bash
cd ~
git clone https://github.com/YOUR_USERNAME/starweb.git
cd starweb
```

**Option B: Transfer from Local Machine**

On your local machine:
```bash
# Compress the project
cd /home/whidden/Projects
tar -czf starweb.tar.gz starweb/

# Upload to server (replace IP)
scp starweb.tar.gz root@YOUR_SERVER_IP:/root/

# On server
cd ~
tar -xzf starweb.tar.gz
cd starweb
```

### 4.2 Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit environment file
nano .env
```

Update these values:
```bash
PORT=8765
HOST=0.0.0.0
TURN_DURATION=180
MAX_TURN_DURATION=480
MAX_PLAYERS=10
MAP_SIZE=255
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

### 4.3 Update WebSocket URL

**Important**: Update the client to connect to your server

```bash
# Edit WebSocket client
nano client/network/WebSocketClient.js
```

Find line ~4 and change:
```javascript
// FROM:
this.url = 'ws://localhost:8765';

// TO (replace with your IP):
this.url = 'ws://YOUR_SERVER_IP:8765';
```

Save: `Ctrl+O`, Enter, `Ctrl+X`

### 4.4 Deploy with Docker

```bash
# Make deploy script executable
chmod +x deploy.sh

# Run deployment
./deploy.sh
```

This will:
- Install Docker (if not already installed)
- Build containers
- Start the game server

### 4.5 Verify Deployment

```bash
# Check running containers
docker-compose ps
```

You should see:
```
NAME                    STATUS              PORTS
starweb-nginx           Up X seconds        0.0.0.0:80->80/tcp, 0.0.0.0:443->443/tcp
starweb-server          Up X seconds        0.0.0.0:8765->8765/tcp
```

Check logs:
```bash
# View server logs
docker-compose logs -f starweb-server

# Press Ctrl+C to exit
```

---

## Step 5: Test Your Deployment

### 5.1 Test HTTP Access

Open browser and go to:
```
http://YOUR_SERVER_IP
```

You should see the StarWeb login screen!

### 5.2 Test Game Functionality

1. **Join game** with a test player name
2. **Check console** (F12 → Console tab)
   - Should see: "WebSocket connected"
   - Should NOT see connection errors
3. **Try commands**: Type `HELP` and press Send
4. **Check status**: Should see your player info

### 5.3 Test from Another Device

- Open on your phone or another computer
- Use: `http://YOUR_SERVER_IP`
- Join with different name
- Verify both players can see each other

---

## Step 6: Get a Domain (Optional but Recommended)

### 6.1 Purchase Domain

Recommended registrars:
- **Namecheap**: https://namecheap.com (~$10/year)
- **Google Domains**: https://domains.google (~$12/year)
- **Cloudflare**: https://cloudflare.com (~$10/year)

Example domains:
- `playstaurweb.com`
- `starweb-game.com`
- `your-starweb.net`

### 6.2 Configure DNS

In your domain registrar's DNS settings, add:

```
Type    Host    Value               TTL
A       @       YOUR_SERVER_IP      3600
A       www     YOUR_SERVER_IP      3600
```

**Wait 10-60 minutes** for DNS to propagate.

Check propagation:
```bash
# On your local machine
dig +short yourdomain.com

# Should show YOUR_SERVER_IP
```

---

## Step 7: Set Up SSL (HTTPS)

### 7.1 Update Nginx Configuration

```bash
cd ~/starweb

# Edit nginx config
nano nginx.conf
```

Find and replace `server_name _;` with your domain:
```nginx
server_name yourdomain.com www.yourdomain.com;
```

Save and exit.

### 7.2 Run SSL Setup Script

```bash
# Make script executable
chmod +x setup-ssl.sh

# Run SSL setup (replace with your domain)
./setup-ssl.sh yourdomain.com
```

This will:
1. Check DNS configuration
2. Request SSL certificate from Let's Encrypt
3. Update nginx to use HTTPS
4. Restart services

### 7.3 Update WebSocket URL for SSL

```bash
nano client/network/WebSocketClient.js
```

Change to use WSS (secure WebSocket):
```javascript
// FROM:
this.url = 'ws://YOUR_SERVER_IP:8765';

// TO:
this.url = 'wss://yourdomain.com/ws';
```

Save and rebuild:
```bash
docker-compose down
docker-compose up --build -d
```

### 7.4 Test HTTPS

Visit: `https://yourdomain.com`

- Should show 🔒 lock icon
- Should redirect from HTTP to HTTPS
- Game should work normally

---

## Step 8: Set Up Auto-Restart and Monitoring

### 8.1 Enable Auto-Restart on Server Reboot

Already configured! Docker Compose has:
```yaml
restart: unless-stopped
```

Test it:
```bash
# Reboot server
sudo reboot

# Wait 2 minutes, then check
ssh root@YOUR_SERVER_IP
docker-compose ps
# Should show containers running
```

### 8.2 Set Up Uptime Monitoring

**Use UptimeRobot (Free):**
1. Sign up: https://uptimerobot.com
2. Add New Monitor:
   - Monitor Type: HTTP(s)
   - URL: `https://yourdomain.com`
   - Monitoring Interval: 5 minutes
3. Get alerts via email/SMS when site goes down

### 8.3 Set Up Log Rotation

```bash
# Create log rotation config
sudo nano /etc/logrotate.d/starweb
```

Add:
```
/root/starweb/*.log {
    daily
    rotate 7
    compress
    delaycompress
    missingok
    notifempty
}
```

---

## Step 9: Backup Strategy

### 9.1 Create Backup Directory

```bash
mkdir -p /root/backups
```

### 9.2 Create Backup Script

```bash
nano /root/backup-starweb.sh
```

Add:
```bash
#!/bin/bash
DATE=$(date +%Y%m%d_%H%M%S)
cd /root/starweb

# Backup game data
tar -czf /root/backups/starweb_data_$DATE.tar.gz data/

# Backup configuration
tar -czf /root/backups/starweb_config_$DATE.tar.gz .env nginx.conf docker-compose.yml

# Keep only last 7 days
find /root/backups -name "starweb_*.tar.gz" -mtime +7 -delete

echo "Backup completed: $DATE"
```

Make executable:
```bash
chmod +x /root/backup-starweb.sh
```

### 9.3 Schedule Daily Backups

```bash
# Edit crontab
crontab -e

# Add this line (runs at 2 AM daily):
0 2 * * * /root/backup-starweb.sh >> /var/log/starweb-backup.log 2>&1
```

Test backup:
```bash
/root/backup-starweb.sh
ls -lh /root/backups/
```

---

## Useful Commands Reference

### Docker Management

```bash
# View running containers
docker-compose ps

# View logs
docker-compose logs -f starweb-server
docker-compose logs -f nginx

# Restart services
docker-compose restart

# Stop services
docker-compose stop

# Start services
docker-compose start

# Stop and remove containers
docker-compose down

# Rebuild and start
docker-compose up --build -d

# View resource usage
docker stats
```

### Server Management

```bash
# Check disk space
df -h

# Check memory usage
free -h

# Check CPU/processes
htop  # (install: apt install htop)

# View system logs
journalctl -xe

# Restart server
sudo reboot
```

### Firewall Management

```bash
# Check firewall status
sudo ufw status

# Allow new port
sudo ufw allow 1234

# Delete rule
sudo ufw delete allow 1234

# Disable firewall (careful!)
sudo ufw disable
```

### SSL Management

```bash
# Test certificate renewal
docker-compose run --rm certbot renew --dry-run

# Force renewal
docker-compose run --rm certbot renew --force-renewal

# Restart nginx after cert renewal
docker-compose restart nginx
```

---

## Troubleshooting

### Can't Connect to Server

**Check 1: Is server running?**
```bash
docker-compose ps
```

**Check 2: Is firewall blocking?**
```bash
sudo ufw status
# Should show ports 80, 443, 8765 allowed
```

**Check 3: Is Docker listening?**
```bash
sudo netstat -tulpn | grep :8765
```

### WebSocket Won't Connect

**Check 1: Browser console errors**
- Open browser Dev Tools (F12)
- Look for WebSocket errors
- Verify URL is correct

**Check 2: Server logs**
```bash
docker-compose logs starweb-server
# Look for connection attempts and errors
```

**Check 3: Test WebSocket directly**
```bash
# Install wscat
npm install -g wscat

# Test connection
wscat -c ws://YOUR_SERVER_IP:8765
```

### SSL Certificate Fails

**Issue: DNS not propagated**
```bash
# Check DNS
dig +short yourdomain.com
# Should return YOUR_SERVER_IP
```

**Issue: Port 80 blocked**
```bash
sudo ufw allow 80
docker-compose restart nginx
```

**Issue: Certificate expired**
```bash
# Renew certificate
docker-compose run --rm certbot renew --force-renewal
docker-compose restart nginx
```

### Out of Disk Space

```bash
# Check space
df -h

# Clean Docker images
docker system prune -a

# Clean logs
sudo journalctl --vacuum-time=7d
```

---

## Performance Tuning

### If Server Feels Slow

**Add swap space:**
```bash
# Create 2GB swap
sudo fallocate -l 2G /swapfile
sudo chmod 600 /swapfile
sudo mkswap /swapfile
sudo swapon /swapfile

# Make permanent
echo '/swapfile none swap sw 0 0' | sudo tee -a /etc/fstab
```

**Limit Docker memory:**
Edit `docker-compose.yml`:
```yaml
services:
  starweb-server:
    mem_limit: 512m
    memswap_limit: 1g
```

### If Many Players

**Upgrade server:**
- DigitalOcean: $12/mo (2GB RAM)
- Linode: $10/mo (2GB RAM)

**Or optimize nginx:**
Edit `nginx.conf`:
```nginx
worker_processes auto;
worker_connections 2048;
```

---

## Next Steps

Your StarWeb server is now live! 🎉

**Share with players:**
- URL: `https://yourdomain.com` (or `http://YOUR_SERVER_IP`)
- Send to friends
- Post on forums/Discord

**Monitor and maintain:**
- Check logs weekly: `docker-compose logs`
- Monitor uptime: UptimeRobot
- Test backups monthly
- Update software: `apt update && apt upgrade`

**Future enhancements:**
1. Add database persistence
2. Create multiple game rooms
3. Add player accounts
4. Build admin panel
5. Add game statistics

See `DEPLOYMENT_GUIDE.md` for advanced topics!

---

## Cost Summary

| Item | Cost | Frequency |
|------|------|-----------|
| VPS | $4-6 | Monthly |
| Domain | $10-12 | Yearly |
| SSL | FREE | (Let's Encrypt) |
| **Total** | **~$5-7/mo** | |

Plus $10-12 one-time for domain.

**You now have a production game server for less than the cost of lunch!** 🚀
