# HTTPS Deployment Notes - StarWeb

## Current Configuration

**SSL Certificate Type:** Self-Signed Certificate
**Certificate Location:** `/certbot/conf/live/localhost/`
**Valid Until:** January 1, 2027 (365 days from generation)
**Protocol:** TLS 1.2 and TLS 1.3

## Browser Security Warnings

Since this deployment uses a self-signed certificate, browsers will show security warnings. This is **expected behavior** and does not indicate a problem with your deployment.

### How to Access

1. Navigate to `https://YOUR_SERVER_IP` in your browser
2. You will see a security warning specific to your browser:

**Chrome/Edge:**
- Warning: "Your connection is not private"
- Click "Advanced"
- Click "Proceed to [IP address] (unsafe)"

**Firefox:**
- Warning: "Warning: Potential Security Risk Ahead"
- Click "Advanced..."
- Click "Accept the Risk and Continue"

**Safari:**
- Warning: "This Connection Is Not Private"
- Click "Show Details"
- Click "visit this website"

3. After accepting the certificate, the page will load normally
4. Your browser may remember this exception for future visits

## Verifying HTTPS is Working

### Check Certificate Details

```bash
openssl x509 -in certbot/conf/live/localhost/fullchain.pem -text -noout
```

This will display the certificate information including:
- Issuer: StarWeb (self-signed)
- Subject: localhost
- Validity period
- Public key information

### Check HTTP to HTTPS Redirect

```bash
curl -I http://YOUR_SERVER_IP
```

Expected response:
```
HTTP/1.1 301 Moved Permanently
Location: https://YOUR_SERVER_IP/
```

### Check WebSocket Connection

1. Access the application via HTTPS
2. Open browser developer console (F12)
3. Look for the WebSocket connection message
4. Verify it shows `wss://` (WebSocket Secure) not `ws://`

Example log:
```
Connecting to WebSocket: wss://YOUR_IP/ws
```

## Service Status

### Check Running Containers

```bash
docker-compose ps
```

All services should show "Up" status:
- nginx (port 80, 443)
- starweb-server (port 8765)

### Check Nginx Logs

```bash
docker-compose logs nginx
```

Look for successful SSL initialization. There should be no errors about missing certificates.

### Check for Errors

```bash
docker-compose logs nginx | grep -i error
```

Should return no SSL-related errors.

## Certificate Information

**Generated:** December 31, 2025
**Expires:** January 1, 2027
**Algorithm:** RSA 2048-bit
**Signature:** SHA256

To view certificate expiration:
```bash
openssl x509 -enddate -noout -in certbot/conf/live/localhost/fullchain.pem
```

## Security Considerations

### Self-Signed Certificates Are For:
- Development and testing environments
- Internal networks and VPNs
- Proof of concept deployments
- Learning and experimentation

### Self-Signed Certificates Are NOT For:
- Public-facing production websites
- Applications requiring user trust
- Compliance requirements (PCI, HIPAA, etc.)
- Search engine optimization (SEO)

## Upgrading to Let's Encrypt (Production SSL)

When you're ready to deploy to production with a real domain, follow these steps:

### Prerequisites

1. **Acquire a domain name** from a registrar (e.g., Namecheap, Google Domains, Cloudflare)
2. **Configure DNS** to point to your server:
   - Create an A record for your domain pointing to your server's public IP
   - Wait for DNS propagation (10-60 minutes)
   - Verify: `dig +short yourdomain.com` should return your server IP
3. **Open firewall ports**:
   - Port 80 (HTTP) - required for Let's Encrypt validation
   - Port 443 (HTTPS)

### Upgrade Process

1. **Stop the containers:**
   ```bash
   docker-compose down
   ```

2. **Run the Let's Encrypt setup script:**
   ```bash
   ./setup-ssl.sh yourdomain.com
   ```

   This script will:
   - Validate your domain points to the server
   - Request a certificate from Let's Encrypt
   - Update nginx configuration
   - Restart services

3. **Update nginx.conf (if needed):**

   The setup script updates most settings, but you may want to manually verify:
   - Line 33: `server_name yourdomain.com;` (HTTP block)
   - Line 49: `server_name yourdomain.com;` (HTTPS block)

4. **Restart services:**
   ```bash
   docker-compose up -d
   ```

5. **Verify the certificate:**
   ```bash
   openssl x509 -in certbot/conf/live/yourdomain.com/fullchain.pem -text -noout
   ```

   The issuer should now be "Let's Encrypt Authority"

### Important Notes About Let's Encrypt

- **Certificate Validity:** Let's Encrypt certificates are valid for 90 days
- **Auto-Renewal:** The certbot container will automatically renew certificates
- **Rate Limits:** Let's Encrypt has rate limits (5 failed attempts per hour)
- **Email:** The setup script uses `admin@yourdomain.com` for certificate notifications
- **No Browser Warnings:** Valid Let's Encrypt certificates are trusted by all major browsers

## Rollback to HTTP (If Needed)

If you need to temporarily disable HTTPS and return to HTTP-only:

1. **Edit nginx.conf:**
   - Comment out lines 40-43 (HTTP to HTTPS redirect)
   - Comment out lines 46-90 (HTTPS server block)
   - Uncomment the original HTTP-only configuration

2. **Restart nginx:**
   ```bash
   docker-compose restart nginx
   ```

3. **Update WebSocket client:**
   The client code is already protocol-aware and will automatically use `ws://` when accessed via HTTP.

## Troubleshooting

### "Unable to load certificate" Error

**Symptom:** Nginx logs show certificate loading errors

**Solution:**
```bash
# Check certificate files exist
ls -la certbot/conf/live/localhost/

# Check file permissions
chmod 644 certbot/conf/live/localhost/fullchain.pem
chmod 600 certbot/conf/live/localhost/privkey.pem

# Restart nginx
docker-compose restart nginx
```

### WebSocket Connection Fails

**Symptom:** Browser console shows WebSocket connection errors

**Solution:**
1. Check browser console for the WebSocket URL
2. Verify it's using `wss://` not `ws://`
3. Check nginx logs: `docker-compose logs nginx`
4. Verify nginx is proxying to correct backend:
   ```bash
   docker-compose exec nginx nginx -t
   ```

### HTTP Doesn't Redirect to HTTPS

**Symptom:** Accessing `http://` doesn't redirect

**Solution:**
1. Check nginx.conf lines 40-43 are uncommented
2. Restart nginx: `docker-compose restart nginx`
3. Clear browser cache
4. Test with curl: `curl -I http://YOUR_IP`

### Certificate Expired

**Symptom:** Browser shows expired certificate warning

**Solution:**
Self-signed certificates don't auto-renew. Either:
1. **Regenerate self-signed certificate:**
   ```bash
   ./generate-self-signed-cert.sh
   docker-compose restart nginx
   ```

2. **Upgrade to Let's Encrypt** (recommended for production):
   ```bash
   ./setup-ssl.sh yourdomain.com
   ```

## Additional Resources

- **Let's Encrypt Documentation:** https://letsencrypt.org/docs/
- **Nginx SSL Configuration Guide:** https://nginx.org/en/docs/http/configuring_https_servers.html
- **SSL Labs Server Test:** https://www.ssllabs.com/ssltest/ (test your domain after Let's Encrypt upgrade)
- **Mozilla SSL Configuration Generator:** https://ssl-config.mozilla.org/

## Support

For issues specific to StarWeb HTTPS configuration:
1. Check the troubleshooting section above
2. Review nginx logs: `docker-compose logs nginx`
3. Verify certificate files exist and have correct permissions
4. Ensure ports 80 and 443 are accessible from the internet

For Let's Encrypt specific issues:
- Visit https://letsencrypt.org/docs/faq/
- Check Let's Encrypt community forum
