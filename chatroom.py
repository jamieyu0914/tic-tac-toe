from flask import session, request
from flask_socketio import emit, join_room, leave_room
from game_rooms import (
    create_room, join_room as join_game_room, get_available_room,
    get_room_by_sid, get_room, make_move, leave_room as leave_game_room,
    reset_room
)

def register_chat_events(socketio):
    @socketio.on('chat message')
    def handle_chat_message(msg):
        user = session.get('user', '匿名')
        emit('chat message', f"{user}: {msg}", broadcast=True)
    
    @socketio.on('join_pvp')
    def handle_join_pvp():
        """Handle a player joining PvP matchmaking."""
        username = session.get('user', '匿名')
        sid = request.sid
        
        # Try to find an available room
        room_id = get_available_room()
        
        if room_id:
            # Join existing room
            success = join_game_room(room_id, sid, username)
            if success:
                join_room(room_id)
                room = get_room(room_id)
                # Notify each player individually with their symbol
                for player in room['players']:
                    emit('game_start', {
                        'room_id': room_id,
                        'players': [{'username': p['username'], 'symbol': p['symbol']} for p in room['players']],
                        'board': room['board'],
                        'turn': room['turn'],
                        'your_symbol': player['symbol']
                    }, room=player['sid'])
        else:
            # Create new room
            room_id = create_room(sid, username)
            join_room(room_id)
            emit('waiting_for_opponent', {'room_id': room_id})
    
    @socketio.on('make_move')
    def handle_make_move(data):
        """Handle a player making a move."""
        sid = request.sid
        cell_index = data.get('cell')
        
        room_id = get_room_by_sid(sid)
        if not room_id:
            return
        
        room = make_move(room_id, sid, cell_index)
        if room:
            # Broadcast the updated game state to both players
            emit('game_update', {
                'board': room['board'],
                'turn': room['turn'],
                'winner': room['winner']
            }, room=room_id)
    
    @socketio.on('reset_game')
    def handle_reset_game():
        """Handle resetting the game."""
        sid = request.sid
        room_id = get_room_by_sid(sid)
        
        if room_id:
            room = reset_room(room_id)
            if room:
                emit('game_update', {
                    'board': room['board'],
                    'turn': room['turn'],
                    'winner': room['winner']
                }, room=room_id)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """Handle player disconnection."""
        sid = request.sid
        room_id = leave_game_room(sid)
        
        if room_id:
            # Notify the other player
            emit('opponent_left', room=room_id)
