"""
Game room management for PvP matches.
Each room has two players and maintains shared game state.
"""
import random

# In-memory storage for game rooms
# Structure: {room_id: {'players': [sid1, sid2], 'board': [...], 'turn': 'X', 'winner': None, 'started': False}}
game_rooms = {}

# Map socket id to room id
player_to_room = {}

def create_room(sid, username):
    """Create a new game room with the first player."""
    room_id = f"room_{sid[:8]}_{random.randint(1000, 9999)}"
    game_rooms[room_id] = {
        'players': [{'sid': sid, 'username': username, 'symbol': 'X'}],
        'board': [None] * 9,
        'turn': 'X',
        'winner': None,
        'started': False,
        'waiting': True
    }
    player_to_room[sid] = room_id
    return room_id

def join_room(room_id, sid, username):
    """Add a second player to an existing room."""
    if room_id not in game_rooms:
        return False
    
    room = game_rooms[room_id]
    if len(room['players']) >= 2:
        return False
    
    room['players'].append({'sid': sid, 'username': username, 'symbol': 'O'})
    room['waiting'] = False
    room['started'] = True
    player_to_room[sid] = room_id
    return True

def get_available_room():
    """Find a room that is waiting for a second player."""
    for room_id, room in game_rooms.items():
        if room['waiting'] and len(room['players']) == 1:
            return room_id
    return None

def get_room_by_sid(sid):
    """Get the room ID for a given socket ID."""
    return player_to_room.get(sid)

def get_room(room_id):
    """Get room data by room ID."""
    return game_rooms.get(room_id)

def make_move(room_id, sid, cell_index):
    """
    Make a move in the room. Returns the updated room state or None if invalid.
    """
    if room_id not in game_rooms:
        return None
    
    room = game_rooms[room_id]
    
    # Check if game has started
    if not room['started']:
        return None
    
    # Check if there's already a winner
    if room['winner']:
        return None
    
    # Find the player making the move
    player = next((p for p in room['players'] if p['sid'] == sid), None)
    if not player:
        return None
    
    # Check if it's this player's turn
    if room['turn'] != player['symbol']:
        return None
    
    # Validate cell index
    if not (0 <= cell_index < 9):
        return None
    
    # Check if cell is empty
    if room['board'][cell_index] is not None:
        return None
    
    # Make the move
    room['board'][cell_index] = player['symbol']
    
    # Check for winner
    from tic_tac_toe import check_winner
    winner = check_winner(room['board'])
    room['winner'] = winner
    
    # Toggle turn
    room['turn'] = 'O' if room['turn'] == 'X' else 'X'
    
    return room

def leave_room(sid):
    """Remove a player from their room."""
    room_id = player_to_room.pop(sid, None)
    if room_id and room_id in game_rooms:
        room = game_rooms[room_id]
        room['players'] = [p for p in room['players'] if p['sid'] != sid]
        
        # If room is empty, delete it
        if len(room['players']) == 0:
            del game_rooms[room_id]
        
        return room_id
    return None

def reset_room(room_id):
    """Reset the game state in a room."""
    if room_id in game_rooms:
        room = game_rooms[room_id]
        room['board'] = [None] * 9
        room['turn'] = 'X'
        room['winner'] = None
        return room
    return None
