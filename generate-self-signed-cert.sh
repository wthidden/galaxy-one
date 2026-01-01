#!/bin/bash

# Generate Self-Signed SSL Certificate for StarWeb
# This creates a temporary SSL certificate for development/testing
# For production, use setup-ssl.sh with a real domain

set -e

echo "Generating self-signed SSL certificate for StarWeb"
echo "=================================================="
echo ""
echo "NOTE: This certificate is for development/testing only."
echo "Browsers will show a security warning (this is expected)."
echo ""

# Create directory if it doesn't exist
mkdir -p certbot/conf/live/localhost

# Check if certificate already exists
if [ -f certbot/conf/live/localhost/fullchain.pem ]; then
    echo "Existing certificate found. Checking expiration..."
    EXPIRY=$(openssl x509 -enddate -noout -in certbot/conf/live/localhost/fullchain.pem | cut -d= -f2)
    echo "Current certificate expires: $EXPIRY"
    echo ""
    read -p "Replace existing certificate? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo "Keeping existing certificate."
        exit 0
    fi
fi

# Generate self-signed certificate
echo "Generating new self-signed certificate..."
openssl req -x509 -nodes -days 365 -newkey rsa:2048 \
    -keyout certbot/conf/live/localhost/privkey.pem \
    -out certbot/conf/live/localhost/fullchain.pem \
    -subj "/C=US/ST=State/L=City/O=StarWeb/CN=localhost" \
    2>/dev/null

# Set permissions
chmod 644 certbot/conf/live/localhost/fullchain.pem
chmod 600 certbot/conf/live/localhost/privkey.pem

echo ""
echo "Certificate generated successfully!"
echo ""
echo "Certificate details:"
openssl x509 -in certbot/conf/live/localhost/fullchain.pem -noout -subject -dates

echo ""
echo "Next steps:"
echo "1. Update nginx.conf to enable HTTPS"
echo "2. Rebuild containers: docker-compose build --no-cache"
echo "3. Restart services: docker-compose down && docker-compose up -d"
echo "4. Access via https://YOUR_IP (accept browser security warning)"
echo ""
echo "To upgrade to Let's Encrypt (when you have a domain):"
echo "./setup-ssl.sh yourdomain.com"
echo ""
