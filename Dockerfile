FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY server/ ./server/
COPY client/ ./client/
COPY *.py ./

# Create data directory for persistence
RUN mkdir -p /app/data

# Expose WebSocket port
EXPOSE 8765

# Run server
CMD ["python", "server.py"]
