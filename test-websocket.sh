#!/bin/bash

# Test WebSocket connection through nginx proxy

echo "Testing WebSocket connection..."
echo "================================"
echo ""

# Check if containers are running
echo "1. Checking containers..."
docker-compose ps

echo ""
echo "2. Testing internal WebSocket connection..."
# Test if nginx can reach the WebSocket server
docker-compose exec nginx nc -zv starweb-server 8765

echo ""
echo "3. Checking nginx WebSocket proxy config..."
docker-compose exec nginx grep -A5 "location /ws" /etc/nginx/nginx.conf

echo ""
echo "4. Recent nginx logs..."
docker-compose logs nginx | tail -10

echo ""
echo "5. Recent starweb-server logs..."
docker-compose logs starweb-server | tail -10

echo ""
echo "================================"
echo "Next: Open your browser console and check what WebSocket URL it's trying to connect to."
echo "Should see: 'Connecting to WebSocket: wss://YOUR_SERVER/ws'"
echo "If you see 'ws://YOUR_SERVER:8765', the client code needs to be rebuilt."
