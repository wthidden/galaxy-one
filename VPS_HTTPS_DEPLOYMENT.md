# VPS HTTPS Deployment Checklist

## What You Need to Do on Your VPS

Since you've updated the code locally to support HTTPS, you now need to deploy these changes to your VPS.

## Step-by-Step Deployment

### 1. Upload Updated Files to VPS

**Files that changed:**
- `client/network/WebSocketClient.js` - Updated to use wss:// and nginx proxy
- `docker-compose.yml` - Port 8765 no longer exposed externally
- `nginx.conf` - HTTPS server block enabled
- `generate-self-signed-cert.sh` - Certificate generation script

**Methods to upload:**

**Option A: Using Git (recommended)**
```bash
# On your local machine, commit and push
git add .
git commit -m "Enable HTTPS with self-signed certificates"
git push

# On your VPS, pull the changes
cd /path/to/starweb
git pull
```

**Option B: Using SCP**
```bash
# From your local machine
scp client/network/WebSocketClient.js user@vps:/path/to/starweb/client/network/
scp docker-compose.yml user@vps:/path/to/starweb/
scp nginx.conf user@vps:/path/to/starweb/
scp generate-self-signed-cert.sh user@vps:/path/to/starweb/
```

**Option C: Manual Copy-Paste**
- Edit each file on the VPS to match your local version

### 2. Generate SSL Certificates on VPS

```bash
# On your VPS
cd /path/to/starweb
chmod +x generate-self-signed-cert.sh
./generate-self-signed-cert.sh
```

This will create:
- `certbot/conf/live/localhost/fullchain.pem`
- `certbot/conf/live/localhost/privkey.pem`

### 3. Rebuild and Restart Containers

```bash
# Stop current containers
docker-compose down

# Rebuild with new client code (important!)
docker-compose build --no-cache

# Start containers
docker-compose up -d

# Restart nginx to load certificates
docker-compose restart nginx
```

### 4. Verify Deployment

```bash
# Check containers are running
docker-compose ps

# Both should show "Up":
# - nginx (ports 80, 443)
# - starweb-server (no external ports)

# Check for errors
docker-compose logs nginx | grep -i error
docker-compose logs starweb-server | tail -20
```

### 5. Test HTTPS

**From your VPS:**
```bash
# Test HTTP redirects to HTTPS
curl -I http://localhost

# Should show: HTTP/1.1 301 Moved Permanently

# Test HTTPS works
curl -k -I https://localhost

# Should show: HTTP/2 200
```

**From your browser:**
1. Navigate to `https://YOUR_VPS_IP`
2. Accept the self-signed certificate warning
3. Open browser console (F12)
4. Look for: `Connecting to WebSocket: wss://YOUR_VPS_IP/ws`
5. Game should connect

## Troubleshooting

### Issue: "Unable to connect to game server"

**Check browser console (F12):**

**If you see:** `Connecting to WebSocket: ws://YOUR_IP:8765`
- **Problem:** Old client code is still running
- **Solution:** You didn't rebuild containers with new code
  ```bash
  docker-compose down
  docker-compose build --no-cache
  docker-compose up -d
  ```

**If you see:** `Connecting to WebSocket: wss://YOUR_IP/ws`
- **Good!** Client is using the right URL
- Check if nginx can reach backend:
  ```bash
  docker-compose exec nginx nc -zv starweb-server 8765
  # Should show: starweb-server (172.x.x.x:8765) open
  ```

**If you see:** `WebSocket connection to 'wss://...' failed`
- Check nginx logs:
  ```bash
  docker-compose logs nginx | grep -i error
  ```
- Check starweb-server logs:
  ```bash
  docker-compose logs starweb-server | tail -20
  ```

### Issue: nginx won't start

**Check certificate files exist:**
```bash
ls -la certbot/conf/live/localhost/
# Should see: fullchain.pem and privkey.pem
```

**If missing:**
```bash
./generate-self-signed-cert.sh
docker-compose restart nginx
```

### Issue: Browser shows security warning

**This is expected!** Self-signed certificates always show warnings.

**To proceed:**
- Chrome/Edge: Click "Advanced" → "Proceed to [IP] (unsafe)"
- Firefox: Click "Advanced" → "Accept the Risk and Continue"
- Safari: Click "Show Details" → "visit this website"

### Issue: WebSocket errors in starweb-server logs

**If you see:** `EOFError: line without CRLF` or `InvalidMessage`
- **Before fix:** These happened because port 8765 was exposed to internet
- **After fix:** Port 8765 is no longer exposed, errors should stop
- If errors continue, check that docker-compose.yml has ports commented out

## Verifying Everything Works

Run this test script on your VPS:
```bash
chmod +x test-websocket.sh
./test-websocket.sh
```

## Quick Reference

**Deploy updates:**
```bash
git pull  # or scp files
docker-compose down
docker-compose build --no-cache
docker-compose up -d
docker-compose restart nginx
```

**Check status:**
```bash
docker-compose ps
docker-compose logs nginx | tail -20
docker-compose logs starweb-server | tail -20
```

**Test connection:**
```bash
curl -I http://YOUR_VPS_IP    # Should redirect to HTTPS
curl -k -I https://YOUR_VPS_IP  # Should return 200
```

## Important Notes

1. **Always rebuild after code changes:** `docker-compose build --no-cache`
2. **Port 8765 is no longer accessible externally** - this is correct and secure
3. **All WebSocket connections go through nginx on port 443**
4. **Browser will cache JavaScript** - do a hard refresh (Ctrl+F5) if needed

## What Changed

**Before (HTTP):**
- Client connects directly to `ws://server:8765`
- Port 8765 exposed to internet
- No encryption

**After (HTTPS):**
- Client connects to `wss://server/ws` (port 443)
- Nginx proxies to internal `starweb-server:8765`
- Port 8765 NOT exposed to internet
- All traffic encrypted

## Next Steps

Once you have a domain name:
1. Point domain DNS to your VPS IP
2. Run: `./setup-ssl.sh yourdomain.com`
3. This replaces self-signed cert with Let's Encrypt
4. No more browser warnings!
