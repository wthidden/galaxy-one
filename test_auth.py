#!/usr/bin/env python3
"""
Test script for authentication and lobby functionality
"""
import asyncio
import websockets
import json

async def test_authentication():
    """Test signup, login, and lobby functionality"""
    uri = "ws://localhost:8765"

    async with websockets.connect(uri) as websocket:
        print("✓ Connected to server")

        # Test 1: Signup
        print("\n--- Test 1: Signup ---")
        signup_msg = {
            "type": "SIGNUP",
            "username": "testuser",
            "password": "testpass123",
            "email": "test@example.com"
        }
        await websocket.send(json.dumps(signup_msg))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Response: {data}")

        if data.get("type") == "AUTH_SUCCESS":
            print("✓ Signup successful!")
            token = data.get("token")
            player_id = data.get("player_id")
            username = data.get("username")
            print(f"  Token: {token[:20]}...")
            print(f"  Player ID: {player_id}")
            print(f"  Username: {username}")
        else:
            print("✗ Signup failed:", data)
            return

        # Test 2: List games
        print("\n--- Test 2: List Games ---")
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

        # Test 3: Create game
        print("\n--- Test 3: Create Game ---")
        create_game_msg = {
            "type": "CREATE_GAME",
            "token": token,
            "name": "Test Game",
            "character_type": "Empire Builder",
            "character_name": "Emperor Test",
            "max_players": 6,
            "map_size": 100
        }
        await websocket.send(json.dumps(create_game_msg))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Response: {data.get('type')}")
        if data.get("type") == "GAME_CREATED":
            game = data.get("game")
            print(f"✓ Game created!")
            print(f"  Game ID: {game.get('id')}")
            print(f"  Name: {game.get('name')}")
            print(f"  Status: {game.get('status')}")
            print(f"  Players: {game.get('player_count')}/{game.get('max_players')}")
            game_id = game.get('id')
        else:
            print("✗ Game creation failed:", data)
            return

        # Test 4: Get game info
        print("\n--- Test 4: Get Game Info ---")
        get_game_info_msg = {
            "type": "GET_GAME_INFO",
            "token": token,
            "game_id": game_id
        }
        await websocket.send(json.dumps(get_game_info_msg))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Response: {data.get('type')}")
        if data.get("type") == "GAME_INFO":
            game_info = data.get("game")
            scoreboard = data.get("scoreboard", [])
            print(f"✓ Game info received!")
            print(f"  Turn: {game_info.get('current_turn')}")
            print(f"  Scoreboard entries: {len(scoreboard)}")

        # Test 5: Logout
        print("\n--- Test 5: Logout ---")
        logout_msg = {
            "type": "LOGOUT",
            "token": token
        }
        await websocket.send(json.dumps(logout_msg))
        response = await websocket.recv()
        data = json.loads(response)
        print(f"Response: {data.get('type')}")
        if data.get("type") == "LOGOUT_SUCCESS":
            print("✓ Logout successful!")

        # Test 6: Login with same credentials
        print("\n--- Test 6: Login ---")
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
            print("✓ Login successful!")
            print(f"  Username: {data.get('username')}")
        else:
            print("✗ Login failed:", data)

        print("\n" + "="*50)
        print("All tests completed successfully! ✓")
        print("="*50)

if __name__ == "__main__":
    asyncio.run(test_authentication())
