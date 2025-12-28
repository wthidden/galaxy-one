#!/bin/bash

# StarWeb Deployment Script
# Run this on your VPS to deploy the game

set -e  # Exit on error

echo "🚀 StarWeb Deployment Script"
echo "=============================="

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker not found. Installing Docker..."
    curl -fsSL https://get.docker.com -o get-docker.sh
    sh get-docker.sh
    rm get-docker.sh
    echo "✅ Docker installed"
else
    echo "✅ Docker already installed"
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose not found. Installing..."
    sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    echo "✅ Docker Compose installed"
else
    echo "✅ Docker Compose already installed"
fi

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your settings before running"
    echo "   Run: nano .env"
    exit 0
fi

# Create data directory
mkdir -p data
mkdir -p certbot/conf
mkdir -p certbot/www

echo ""
echo "🏗️  Building and starting containers..."
docker-compose down
docker-compose up --build -d

echo ""
echo "✅ Deployment complete!"
echo ""
echo "🌐 Your StarWeb server is running!"
echo ""
echo "Next steps:"
echo "1. Open your browser to http://YOUR_SERVER_IP"
echo "2. For SSL: Run ./setup-ssl.sh yourdomain.com"
echo "3. Check logs: docker-compose logs -f"
echo ""
echo "Useful commands:"
echo "  Stop:    docker-compose stop"
echo "  Restart: docker-compose restart"
echo "  Logs:    docker-compose logs -f starweb-server"
echo "  Status:  docker-compose ps"
echo ""
