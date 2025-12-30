FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/
COPY client/ ./client/
COPY *.py ./
COPY index.html ./
COPY style.css ./
COPY favicon.svg ./
COPY favicon.ico ./
COPY admin_message.txt ./
COPY game_config.yaml ./
COPY PLAYER_MANUAL.md ./
COPY COMMANDS.md ./
COPY CHARACTER_GUIDE.md ./

# Create data directory for persistence
RUN mkdir -p /app/data

# Expose WebSocket port
EXPOSE 8765

# Run server
CMD ["python", "-m", "server.main"]
