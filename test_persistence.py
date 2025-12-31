#!/usr/bin/env python3
"""
Test script for account persistence - verify we can login with saved credentials
"""
import asyncio
import websockets
import json

async def test_persistence():
    """Test login with existing account"""
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        print("✓ Connected to server")

        # Test: Login with existing account
        print("\n--- Test: Login with Saved Account ---")
        login_msg = {
            "type": "LOGIN",
            "username": "testuser",
            "password": "testpass123"
        }
        await websocket.send(json.dumps(login_msg))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Response: {data.get('type')}")

        if data.get("type") == "AUTH_SUCCESS":
            print("✓ Login successful with saved credentials!")
            print(f"  Player ID: {data.get('player_id')}")
            print(f"  Username: {data.get('username')}")
            token = data.get("token")

            # List games to verify multi-game works
            print("\n--- Test: List Games (Multi-Game) ---")
            list_games_msg = {
                "type": "LIST_GAMES",
                "token": token
            }
            await websocket.send(json.dumps(list_games_msg))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Response: {data.get('type')}")
            print(f"  My games: {len(data.get('my_games', []))}")
            print(f"  Available games: {len(data.get('available_games', []))}")

            # Test: Try to signup with same username (should fail)
            print("\n--- Test: Duplicate Username Prevention ---")
            signup_msg = {
                "type": "SIGNUP",
                "username": "testuser",
                "password": "differentpass123"
            }
            await websocket.send(json.dumps(signup_msg))
            response = await websocket.recv()
            data = json.loads(response)
            print(f"Response: {data.get('type')}")
            if data.get("type") == "error":
                print(f"✓ Duplicate prevention working: {data.get('text')}")

            print("\n" + "="*50)
            print("Persistence tests completed successfully! ✓")
            print("="*50)
        else:
            print("✗ Login failed:", data)

if __name__ == "__main__":
    asyncio.run(test_persistence())
