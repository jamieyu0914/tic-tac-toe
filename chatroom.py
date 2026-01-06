"""
chatroom.py - Socket.IO 事件處理
負責處理聊天室和 PVP 對戰的即時通訊事件
"""

from flask import session, request
from flask_socketio import emit, join_room, leave_room
from RoomManager import RoomManager

# 創建全局房間管理器實例
room_manager = RoomManager()


def register_chat_events(socketio):
    """
    註冊 Socket.IO 事件處理函數
    
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
        user = session.get('user', '匿名')
        emit('chat message', f"{user}: {msg}", broadcast=True)
    
    @socketio.on('join_pvp')
    def handle_join_pvp():
        """
        處理玩家加入 PVP 配對
        流程：
        1. 尋找等待中的房間
        2. 若有空房間，加入並開始遊戲
        3. 若無空房間，創建新房間並等待對手
        """
        username = session.get('user', '匿名')
        sid = request.sid
        
        # 嘗試尋找可用房間
        room_id = room_manager.get_available_room()
        
        if room_id:
            # 加入現有房間
            success = room_manager.join_room(room_id, sid, username)
            if success:
                join_room(room_id)
                room = room_manager.get_room(room_id)
                room_state = room.get_state()
                
                # 通知每位玩家遊戲開始（包含各自的符號）
                for player in room.players:
                    emit('game_start', {
                        'room_id': room_id,
                        'players': room_state['players'],
                        'board': room_state['board'],
                        'turn': room_state['turn'],
                        'your_symbol': player.symbol
                    }, room=player.sid)
        else:
            # 創建新房間
            room_id = room_manager.create_room(sid, username)
            join_room(room_id)
            emit('waiting_for_opponent', {'room_id': room_id})
    
    @socketio.on('make_move')
    def handle_make_move(data):
        """
        處理玩家移動
        
        Args:
            data: 包含移動資訊的字典 {'cell': position}
        """
        sid = request.sid
        cell_index = data.get('cell')
        
        # 獲取玩家所在房間
        room_id = room_manager.get_room_by_sid(sid)
        if not room_id:
            return
        
        # 執行移動
        room_state = room_manager.make_move(room_id, sid, cell_index)
        if room_state:
            # 廣播更新後的遊戲狀態給房間內所有玩家
            emit('game_update', {
                'board': room_state['board'],
                'turn': room_state['turn'],
                'winner': room_state['winner']
            }, room=room_id)
    
    @socketio.on('reset_game')
    def handle_reset_game():
        """
        處理遊戲重置請求
        """
        sid = request.sid
        room_id = room_manager.get_room_by_sid(sid)
        
        if room_id:
            room_state = room_manager.reset_room(room_id)
            if room_state:
                # 廣播重置後的遊戲狀態
                emit('game_update', {
                    'board': room_state['board'],
                    'turn': room_state['turn'],
                    'winner': room_state['winner']
                }, room=room_id)
    
    @socketio.on('disconnect')
    def handle_disconnect():
        """
        處理玩家斷線
        當玩家離開時，通知房間內的其他玩家
        """
        sid = request.sid
        room_id = room_manager.leave_room(sid)
        
        if room_id:
            # 通知對手玩家已離開
            emit('opponent_left', room=room_id)

