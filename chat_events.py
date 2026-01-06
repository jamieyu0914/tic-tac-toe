"""
chat_events.py - 聊天室事件處理
負責處理聊天消息的即時通訊
"""

from flask import session
from flask_socketio import emit
from datetime import datetime


def register_chat_events(socketio):
    """
    註冊聊天相關的 Socket.IO 事件
    
    Args:
        socketio: SocketIO 實例
    """
    
    @socketio.on('chat message')
    def handle_chat_message(msg):
        """
        處理聊天消息
        
        Args:
            msg: 聊天消息內容
        """
        user = session.get('user', '隱藏玩家') # 如果沒有用戶名，則顯示為隱藏玩家
        # 加上時間
        timestamp = datetime.now().strftime('%H:%M:%S')
        emit('chat message', f"[{timestamp}] {user}: {msg}", broadcast=True)
