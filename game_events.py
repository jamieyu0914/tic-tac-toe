"""
game_events.py - 遊戲事件處理
負責處理 PVP 對戰的遊戲邏輯和房間管理
"""

from flask import session, request
from flask_socketio import emit, join_room, leave_room
from RoomManager import RoomManager
import time

# 創建全局房間管理器實例
room_manager = RoomManager()


def register_game_events(socketio):
    """
    註冊遊戲相關的 Socket.IO 事件
    
    Args:
        socketio: SocketIO 實例
    """
    
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
                
                # 取得第一個玩家的名稱
                first_player_name = room_state['players'][0]['username']
                
                # 發送系統訊息到聊天室（兩則訊息都會被兩位玩家看到）
                emit('chat message', f'[系統提示] 強勁的棋手 {first_player_name} 已等候多時!', room=room_id)
                time.sleep(0.5)  # 確保訊息順序
                emit('chat message', f'[系統提示] 強勁的棋手 {username} 已抵達戰場!', room=room_id)
                
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
            emit('chat message', f'[系統提示] 請等候其他玩家加入！', room=room_id)
    
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
