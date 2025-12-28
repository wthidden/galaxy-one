# StarWeb Game

This is a basic implementation of the StarWeb game using Python, WebSockets, and HTML/CSS/JS.

## Prerequisites

- Python 3.7+
- `pip`

## Installation

1.  Install the required Python packages:
    ```bash
    pip install -r requirements.txt
    ```

## Running the Game

1.  Start the server:
    ```bash
    python server.py
    ```
    The server will start on `ws://localhost:8765`.

2.  Open `index.html` in your web browser.

## How to Play

- Upon connection, you will be assigned a starting world and 5 fleets (keys).
- The game interface shows the JSON representation of the worlds and fleets you can see.
- You can issue commands in the text box. Currently, only a simple `MOVE` command is supported:
    ```
    MOVE <fleet_id> <destination_world_id>
    ```
    Example: `MOVE 1 2` (moves Fleet 1 to World 2, if connected).

## Project Structure

- `server.py`: The main Python server handling game logic and WebSockets.
- `index.html`: The frontend HTML file.
- `style.css`: Styles for the frontend.
- `game.js`: JavaScript for WebSocket communication and UI updates.
- `requirements.txt`: Python dependencies.
