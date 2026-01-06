"""
RoomManager.py - 遊戲房間管理類別
負責管理 PVP 模式的房間創建、玩家加入、遊戲狀態同步
"""

import random
from typing import Optional, Dict, List
from Game import Game, Player


class PlayerInfo:
    """玩家資訊類別"""
    
    def __init__(self, sid: str, username: str, symbol: str):
        """
        初始化玩家資訊
        
        Args:
            sid: Socket ID
            username: 玩家名稱
            symbol: 玩家符號 ('X' 或 'O')
        """
        self.sid = sid
        self.username = username
        self.symbol = symbol
    
    def to_dict(self) -> dict:
        """轉換為字典格式"""
        return {
            'sid': self.sid,
            'username': self.username,
            'symbol': self.symbol
        }


class GameRoom:
    """
    遊戲房間類別
    管理一個房間內的遊戲狀態和玩家資訊
    """
    
    def __init__(self, room_id: str, creator_sid: str, creator_username: str):
        """
        初始化遊戲房間
        
        Args:
            room_id: 房間 ID
            creator_sid: 創建者 Socket ID
            creator_username: 創建者名稱
        """
        self.room_id = room_id
        self.game = Game()  # 遊戲實例
        self.players: List[PlayerInfo] = [] # 玩家列表
        self.waiting = True  # 等待第二位玩家
        
        # 第一位玩家使用 'X'
        first_player = PlayerInfo(creator_sid, creator_username, Player.X.value)
        self.players.append(first_player)
    
    def add_player(self, sid: str, username: str) -> bool:
        """
        添加第二位玩家到房間
        
        Args:
            sid: 玩家 Socket ID
            username: 玩家名稱
            
        Returns:
            bool: 是否成功添加
        """
        if len(self.players) >= 2:
            return False
        
        # 第二位玩家使用 'O'
        second_player = PlayerInfo(sid, username, Player.O.value)
        self.players.append(second_player)
        self.waiting = False # 已有兩位玩家，停止等待
        self.game.start()  # 開始遊戲
        return True
    
    def remove_player(self, sid: str) -> bool:
        """
        移除玩家
        
        Args:
            sid: 玩家 Socket ID
            
        Returns:
            bool: 是否成功移除
        """
        for player in self.players:
            if player.sid == sid:
                self.players.remove(player)
                return True
        return False
    
    def get_player_by_sid(self, sid: str) -> Optional[PlayerInfo]:
        """
        根據 Socket ID 獲取玩家資訊
        
        Args:
            sid: Socket ID
            
        Returns:
            Optional[PlayerInfo]: 玩家資訊，若不存在則返回 None
        """
        for player in self.players:
            if player.sid == sid:
                return player
        return None
    
    def make_move(self, sid: str, position: int) -> bool:
        """
        執行移動
        
        Args:
            sid: 玩家 Socket ID
            position: 棋盤位置
            
        Returns:
            bool: 移動是否成功
        """
        # 獲取玩家資訊
        player = self.get_player_by_sid(sid)
        if not player:
            return False
        
        # 檢查是否輪到該玩家
        if self.game.turn != player.symbol:
            return False
        
        # 執行移動
        return self.game.make_move(position, player.symbol) # (下棋位置, 玩家符號 X 或 O)
    
    def reset(self):
        """重置遊戲"""
        self.game.start()
    
    def get_state(self) -> dict:
        """
        獲取房間狀態
        
        Returns:
            dict: 房間狀態字典
        """
        return {
            'room_id': self.room_id,
            'players': [player.to_dict() for player in self.players],
            'board': self.game.board,
            'turn': self.game.turn,
            'winner': self.game.winner,
            'waiting': self.waiting,
            'started': self.game.started
        }


class RoomManager:
    """
    房間管理器類別
    負責管理所有遊戲房間和玩家對應關係
    """
    
    def __init__(self):
        """初始化房間管理器"""
        # 房間字典：{room_id: GameRoom}
        self.rooms: Dict[str, GameRoom] = {}
        # 玩家到房間的映射：{sid: room_id}
        self.player_to_room: Dict[str, str] = {}
    
    def create_room(self, sid: str, username: str) -> str:
        """
        創建新房間
        
        Args:
            sid: 創建者 Socket ID
            username: 創建者名稱
            
        Returns:
            str: 房間 ID
        """
        # 生成唯一房間 ID
        room_id = f"room_{sid[:8]}_{random.randint(1000, 9999)}" # eg. room_abcd1234_5678
        
        # 創建房間
        room = GameRoom(room_id, sid, username)
        self.rooms[room_id] = room
        self.player_to_room[sid] = room_id
        
        return room_id
    
    def join_room(self, room_id: str, sid: str, username: str) -> bool:
        """
        加入現有房間
        
        Args:
            room_id: 房間 ID
            sid: 玩家 Socket ID
            username: 玩家名稱
            
        Returns:
            bool: 是否成功加入
        """
        if room_id not in self.rooms:
            return False
        
        room = self.rooms[room_id]
        success = room.add_player(sid, username)
        
        if success:
            self.player_to_room[sid] = room_id
        
        return success
    
    def leave_room(self, sid: str) -> Optional[str]:
        """
        離開房間
        
        Args:
            sid: 玩家 Socket ID
            
        Returns:
            Optional[str]: 房間 ID，若玩家不在任何房間則返回 None
        """
        room_id = self.player_to_room.get(sid)
        if not room_id:
            return None
        
        room = self.rooms.get(room_id)
        if room:
            room.remove_player(sid)
            # 如果房間為空，刪除房間
            if len(room.players) == 0:
                del self.rooms[room_id]
            # 如果房間只剩一人且遊戲已開始，也可以選擇刪除房間
            # 或將其標記為等待狀態（這裡選擇保留房間讓玩家等待）
        
        del self.player_to_room[sid]
        return room_id
    
    def get_room_count(self) -> int:
        """
        獲取當前房間數量
        
        Returns:
            int: 房間數量
        """
        return len(self.rooms)
    
    def get_waiting_room_count(self) -> int:
        """
        獲取等待中的房間數量
        
        Returns:
            int: 等待中的房間數量
        """
        return sum(1 for room in self.rooms.values() if room.waiting)
    
    def get_active_room_count(self) -> int:
        """
        獲取進行中的房間數量
        
        Returns:
            int: 進行中的房間數量
        """
        return sum(1 for room in self.rooms.values() if not room.waiting)
    
    def get_available_room(self) -> Optional[str]:
        """
        獲取一個等待中的房間
        
        Returns:
            Optional[str]: 房間 ID，若無可用房間則返回 None
        """
        for room_id, room in self.rooms.items():
            if room.waiting and len(room.players) == 1:
                return room_id
        return None
    
    def get_room(self, room_id: str) -> Optional[GameRoom]:
        """
        獲取房間實例
        
        Args:
            room_id: 房間 ID
            
        Returns:
            Optional[GameRoom]: 房間實例，若不存在則返回 None
        """
        return self.rooms.get(room_id)
    
    def get_room_by_sid(self, sid: str) -> Optional[str]:
        """
        根據玩家 Socket ID 獲取房間 ID
        
        Args:
            sid: 玩家 Socket ID
            
        Returns:
            Optional[str]: 房間 ID，若玩家不在任何房間則返回 None
        """
        return self.player_to_room.get(sid)
    
    def make_move(self, room_id: str, sid: str, position: int) -> Optional[dict]:
        """
        在指定房間執行移動
        
        Args:
            room_id: 房間 ID
            sid: 玩家 Socket ID
            position: 棋盤位置
            
        Returns:
            Optional[dict]: 更新後的房間狀態，若失敗則返回 None
        """
        room = self.get_room(room_id)
        if not room:
            return None
        
        success = room.make_move(sid, position)
        if not success:
            return None
        
        return room.get_state()
    
    def reset_room(self, room_id: str) -> Optional[dict]:
        """
        重置指定房間的遊戲
        
        Args:
            room_id: 房間 ID
            
        Returns:
            Optional[dict]: 重置後的房間狀態，若房間不存在則返回 None
        """
        room = self.get_room(room_id)
        if not room:
            return None
        
        room.reset()
        return room.get_state()
