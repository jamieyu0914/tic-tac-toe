from flask import session
from flask_socketio import emit

def register_chat_events(socketio):
    @socketio.on('chat message')
    def handle_chat_message(msg):
        user = session.get('user', '匿名')
        emit('chat message', f"{user}: {msg}", broadcast=True)
