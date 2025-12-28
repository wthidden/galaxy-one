#!/bin/bash

# SSL Setup Script using Let's Encrypt
# Usage: ./setup-ssl.sh yourdomain.com

set -e

if [ -z "$1" ]; then
    echo "❌ Usage: ./setup-ssl.sh yourdomain.com"
    exit 1
fi

DOMAIN=$1

echo "🔒 Setting up SSL for $DOMAIN"
echo "================================"

# Check if domain points to this server
echo "Checking DNS..."
SERVER_IP=$(curl -s ifconfig.me)
DOMAIN_IP=$(dig +short $DOMAIN | head -n 1)

if [ "$SERVER_IP" != "$DOMAIN_IP" ]; then
    echo "⚠️  Warning: Domain $DOMAIN does not point to this server"
    echo "   Server IP: $SERVER_IP"
    echo "   Domain IP: $DOMAIN_IP"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Stop nginx temporarily
echo "Stopping nginx..."
docker-compose stop nginx

# Get certificate
echo "Requesting SSL certificate from Let's Encrypt..."
docker run -it --rm \
    -v $(pwd)/certbot/conf:/etc/letsencrypt \
    -v $(pwd)/certbot/www:/var/www/certbot \
    -p 80:80 \
    certbot/certbot certonly \
    --standalone \
    --email admin@$DOMAIN \
    --agree-tos \
    --no-eff-email \
    -d $DOMAIN \
    -d www.$DOMAIN

if [ $? -eq 0 ]; then
    echo "✅ Certificate obtained successfully!"

    # Update nginx config to use SSL
    echo "Updating nginx configuration..."

    # Backup original
    cp nginx.conf nginx.conf.bak

    # Update server_name in nginx.conf
    sed -i "s/server_name _;/server_name $DOMAIN;/g" nginx.conf
    sed -i "s/yourdomain.com/$DOMAIN/g" nginx.conf

    # Uncomment SSL sections
    sed -i 's/# return 301/return 301/g' nginx.conf
    sed -i '/# server {/,/# }/s/^# //g' nginx.conf

    echo "✅ Nginx configuration updated"

    # Restart services
    echo "Restarting services..."
    docker-compose up -d

    echo ""
    echo "🎉 SSL setup complete!"
    echo ""
    echo "Your site is now available at:"
    echo "  https://$DOMAIN"
    echo "  https://www.$DOMAIN"
    echo ""
    echo "Certificate will auto-renew. To test renewal:"
    echo "  docker-compose run --rm certbot renew --dry-run"
    echo ""
else
    echo "❌ Failed to obtain certificate"
    echo "Make sure:"
    echo "  1. Port 80 is open in your firewall"
    echo "  2. Domain points to this server"
    echo "  3. No other web server is running"
    exit 1
fi
