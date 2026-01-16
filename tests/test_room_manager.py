"""
test_room_manager.py - RoomManager 及 GameRoom 單元測試
"""

import unittest
import sys
import os
import random

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from RoomManager import RoomManager, GameRoom, PlayerInfo
from Game import Player

class TestPlayerInfo(unittest.TestCase):
    """測試 PlayerInfo 類別"""
    
    def test_player_info_creation(self):
        """測試 PlayerInfo 創建"""
        player = PlayerInfo('sid123', 'TestUser', 'X')
        self.assertEqual(player.sid, 'sid123')
        self.assertEqual(player.username, 'TestUser')
        self.assertEqual(player.symbol, 'X')
    
    def test_to_dict(self):
        """測試 to_dict 方法"""
        player = PlayerInfo('sid123', 'TestUser', 'X')
        result = player.to_dict()
        expected = {
            'sid': 'sid123',
            'username': 'TestUser',
            'symbol': 'X'
        }
        self.assertEqual(result, expected)

class TestGameRoom(unittest.TestCase):
    """測試 GameRoom 類別"""
    
    def setUp(self):
        """設置測試環境"""
        self.room_id = 'test_room_123'
        self.creator_sid = 'sid1'
        self.creator_username = 'Player1'
        self.room = GameRoom(self.room_id, self.creator_sid, self.creator_username)
    
    def test_room_creation(self):
        """測試房間創建"""
        self.assertEqual(self.room.room_id, self.room_id)
        self.assertEqual(len(self.room.players), 1)
        self.assertEqual(self.room.players[0].sid, self.creator_sid)
        self.assertEqual(self.room.players[0].username, self.creator_username)
        self.assertTrue(self.room.waiting)
        self.assertIsNotNone(self.room.game)
        
    def test_add_player(self):
        """測試添加玩家"""
        second_sid = 'sid2'
        second_username = 'Player2'
        
        success = self.room.add_player(second_sid, second_username)
        self.assertTrue(success)
        self.assertEqual(len(self.room.players), 2)
        self.assertFalse(self.room.waiting)
        self.assertTrue(self.room.game.started)
        
    def test_add_player_to_full_room(self):
        """測試向滿員房間添加玩家"""
        # 添加第二個玩家
        self.room.add_player('sid2', 'Player2')
        
        # 嘗試添加第三個玩家
        success = self.room.add_player('sid3', 'Player3')
        self.assertFalse(success)
        self.assertEqual(len(self.room.players), 2)
        
    def test_remove_player(self):
        """測試移除玩家"""
        self.room.add_player('sid2', 'Player2')
        
        # 移除第二個玩家
        removed = self.room.remove_player('sid2')
        self.assertTrue(removed)
        self.assertEqual(len(self.room.players), 1)
        # waiting狀態可能不會自動更新，這取決於實現
        
        # 嘗試移除不存在的玩家
        removed = self.room.remove_player('non_existent')
        self.assertFalse(removed)
        
    def test_is_empty_simulation(self):
        """測試房間空狀態的模擬"""
        # 有一個玩家，不為空
        self.assertFalse(len(self.room.players) == 0)
        
        # 移除玩家後為空
        self.room.remove_player(self.creator_sid)
        self.assertTrue(len(self.room.players) == 0)
        
    def test_make_move_valid(self):
        """測試有效移動"""
        # 添加第二個玩家開始遊戲
        self.room.add_player('sid2', 'Player2')
        
        # 獲取當前輪次的玩家
        current_player_sid = self.room.left_player.sid if self.room.game.turn == self.room.left_player.symbol else self.room.right_player.sid
        
        success = self.room.make_move(current_player_sid, 0, 0)
        self.assertTrue(success)
        self.assertIsNotNone(self.room.game.board[0][0])
        
    def test_make_move_invalid_player(self):
        """測試無效玩家移動"""
        self.room.add_player('sid2', 'Player2')
        
        # 使用不存在的玩家SID
        success = self.room.make_move('invalid_sid', 0, 0)
        self.assertFalse(success)
        
    def test_make_move_wrong_turn(self):
        """測試錯誤輪次移動"""
        self.room.add_player('sid2', 'Player2')
        
        # 獲取非當前輪次的玩家
        wrong_player_sid = self.room.right_player.sid if self.room.game.turn == self.room.left_player.symbol else self.room.left_player.sid
        
        success = self.room.make_move(wrong_player_sid, 0, 0)
        self.assertFalse(success)
        
    def test_reset_room(self):
        """測試房間重置"""
        self.room.add_player('sid2', 'Player2')
        
        # 進行一些移動
        current_player_sid = self.room.left_player.sid if self.room.game.turn == self.room.left_player.symbol else self.room.right_player.sid
        self.room.make_move(current_player_sid, 0, 0)
        
        # 重置房間
        self.room.reset()
        
        # 檢查重置結果
        self.assertEqual(self.room.game.board, [[None] * 3 for _ in range(3)])
        self.assertTrue(self.room.game.started)
        
    def test_get_state(self):
        """測試獲取房間狀態"""
        self.room.add_player('sid2', 'Player2')
        
        state = self.room.get_state()
        
        # 檢查狀態包含必要字段
        required_fields = ['room_id', 'players', 'waiting', 'board', 'turn', 
                          'winner', 'scores', 'round_count', 'match_finished',
                          'left_player', 'right_player', 'current_first_player']
        
        for field in required_fields:
            self.assertIn(field, state)
            
        self.assertEqual(state['room_id'], self.room_id)
        self.assertEqual(len(state['players']), 2)
        self.assertFalse(state['waiting'])
        
    def test_assign_seats_and_symbols(self):
        """測試座位和符號分配"""
        self.room.add_player('sid2', 'Player2')
        
        # 檢查座位和符號是否正確分配
        self.assertIsNotNone(self.room.left_player)
        self.assertIsNotNone(self.room.right_player)
        self.assertIn(self.room.left_player.symbol, ['X', 'O'])
        self.assertIn(self.room.right_player.symbol, ['X', 'O'])
        self.assertNotEqual(self.room.left_player.symbol, self.room.right_player.symbol)

class TestRoomManager(unittest.TestCase):
    def setUp(self):
        self.manager = RoomManager()
        self.sid1 = 'sid1'
        self.sid2 = 'sid2'
        self.username1 = 'Alice'
        self.username2 = 'Bob'

    def tearDown(self):
        """清理測試環境"""
        self.manager.rooms.clear()
        self.manager.player_to_room.clear()

    def test_create_room(self):
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.assertIn(room_id, self.manager.rooms)
        room = self.manager.get_room(room_id)
        self.assertEqual(room.players[0].sid, self.sid1)
        self.assertEqual(room.players[0].username, self.username1)
        self.assertTrue(room.waiting)

    def test_join_room(self):
        room_id = self.manager.create_room(self.sid1, self.username1)
        success = self.manager.join_room(room_id, self.sid2, self.username2)
        self.assertTrue(success)
        room = self.manager.get_room(room_id)
        self.assertEqual(len(room.players), 2)
        self.assertFalse(room.waiting)

    def test_join_full_room(self):
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        sid3 = 'sid3'
        username3 = 'Charlie'
        success = self.manager.join_room(room_id, sid3, username3)
        self.assertFalse(success)

    def test_join_nonexistent_room(self):
        """測試加入不存在的房間"""
        success = self.manager.join_room('nonexistent', self.sid1, self.username1)
        self.assertFalse(success)

    def test_leave_room(self):
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        left_room = self.manager.leave_room(self.sid2)
        self.assertEqual(left_room, room_id)
        room = self.manager.get_room(room_id)
        self.assertIsNone(room)

    def test_leave_room_not_in_any_room(self):
        """測試離開不在任何房間的玩家"""
        result = self.manager.leave_room('nonexistent_sid')
        self.assertIsNone(result)

    def test_make_move(self):
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        # 取得先手玩家
        first_sid = room.left_player.sid if room.game.turn == room.left_player.symbol else room.right_player.sid
        state = self.manager.make_move(room_id, first_sid, 0, 0)
        self.assertIsNotNone(state)
        self.assertIn(state['board'][0][0], [Player.X.value, Player.O.value])

    def test_make_move_nonexistent_room(self):
        """測試在不存在的房間中移動"""
        state = self.manager.make_move('nonexistent', self.sid1, 0, 0)
        self.assertIsNone(state)

    def test_get_available_room(self):
        room_id = self.manager.create_room(self.sid1, self.username1)
        available = self.manager.get_available_room()
        self.assertEqual(available, room_id)
        self.manager.join_room(room_id, self.sid2, self.username2)
        available2 = self.manager.get_available_room()
        self.assertNotEqual(available2, room_id)

    def test_get_available_room_none(self):
        """測試沒有可用房間的情況"""
        available = self.manager.get_available_room()
        self.assertIsNone(available)

    def test_reset_room(self):
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        state = self.manager.reset_room(room_id)
        self.assertIsInstance(state, dict)
        self.assertEqual(state['round_count'], 1)

    def test_reset_nonexistent_room(self):
        """測試重置不存在的房間"""
        state = self.manager.reset_room('nonexistent')
        self.assertIsNone(state)

    def test_get_room_by_sid(self):
        """測試通過SID獲取房間"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        found_room_id = self.manager.get_room_by_sid(self.sid1)
        self.assertEqual(found_room_id, room_id)
        
        # 測試不存在的SID
        not_found = self.manager.get_room_by_sid('nonexistent')
        self.assertIsNone(not_found)

    def test_get_active_game_count(self):
        """測試獲取活躍遊戲數量"""
        # 初始為0
        count = self.manager.get_active_game_count()
        self.assertEqual(count, 0)
        
        # 創建房間但未滿員
        self.manager.create_room(self.sid1, self.username1)
        count = self.manager.get_active_game_count()
        self.assertEqual(count, 0)
        
        # 房間滿員，遊戲開始
        room_id = list(self.manager.rooms.keys())[0]
        self.manager.join_room(room_id, self.sid2, self.username2)
        count = self.manager.get_active_game_count()
        self.assertEqual(count, 1)

    def test_multiple_rooms_management(self):
        """測試多房間管理"""
        # 創建多個房間
        room1_id = self.manager.create_room('sid1', 'User1')
        room2_id = self.manager.create_room('sid3', 'User3')
        
        self.assertNotEqual(room1_id, room2_id)
        self.assertEqual(len(self.manager.rooms), 2)
        
        # 加入玩家
        self.manager.join_room(room1_id, 'sid2', 'User2')
        self.manager.join_room(room2_id, 'sid4', 'User4')
        
        # 檢查活躍遊戲數量
        count = self.manager.get_active_game_count()
        self.assertEqual(count, 2)
        
        # 離開房間
        self.manager.leave_room('sid2')
        self.manager.leave_room('sid4')
        
        # 房間應該被清理
        self.assertEqual(len(self.manager.rooms), 0)

    def test_room_cleanup_on_empty(self):
        """測試房間清空時的清理"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        
        # 移除所有玩家
        self.manager.leave_room(self.sid1)
        self.manager.leave_room(self.sid2)
        
        # 房間和玩家映射應被清理
        self.assertNotIn(room_id, self.manager.rooms)
        self.assertNotIn(self.sid1, self.manager.player_to_room)
        self.assertNotIn(self.sid2, self.manager.player_to_room)

    def test_player_rejoin_after_leave(self):
        """測試玩家離開後重新加入"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.leave_room(self.sid1)
        
        # 同一個玩家創建新房間
        new_room_id = self.manager.create_room(self.sid1, self.username1)
        self.assertIsNotNone(new_room_id)
        self.assertIn(self.sid1, self.manager.player_to_room)

    def test_room_reset_match_finished_condition(self):
        """測試房間重置時比賽結束的條件"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置比賽已結束狀態
        room.match_finished = True
        
        # 嘗試重置，應該不會做任何操作
        room.reset()
        self.assertTrue(room.match_finished)  # 狀態不變

    def test_room_reset_with_score_limit_reached(self):
        """測試當有一方達到3勝時的重置"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置左方玩家已達3勝
        room.scores = {'left': 3, 'right': 1, 'draw': 0}
        room.match_finished = False  # 先設為未結束
        
        # 重置會檢查分數並設置比賽結束
        room.reset()
        self.assertTrue(room.match_finished)

    def test_room_reset_with_max_rounds_reached(self):
        """測試當達到最大回合數時的重置"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置已打完5戰（round_count == 4）
        room.round_count = 4
        room.match_finished = False  # 先設為未結束
        
        # 重置會檢查回合數並設置比賽結束
        room.reset()
        self.assertTrue(room.match_finished)

    def test_check_round_end_with_draw(self):
        """測試回合結束檢查 - 平局情況"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置遊戲結果為平局
        room.game.winner = 'Draw'
        
        # 檢查回合結束
        result = room.check_round_end()
        self.assertTrue(result)
        self.assertEqual(room.scores['draw'], 1)

    def test_check_round_end_with_left_player_win(self):
        """測試回合結束檢查 - 左玩家獲勝"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置左玩家獲勝
        room.game.winner = room.left_player.symbol
        
        # 檢查回合結束
        result = room.check_round_end()
        self.assertTrue(result)
        self.assertEqual(room.scores['left'], 1)

    def test_check_round_end_with_right_player_win(self):
        """測試回合結束檢查 - 右玩家獲勝"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置右玩家獲勝
        room.game.winner = room.right_player.symbol
        
        # 檢查回合結束
        result = room.check_round_end()
        self.assertTrue(result)
        self.assertEqual(room.scores['right'], 1)

    def test_check_round_end_match_finish_by_score(self):
        """測試因分數達標而結束比賽"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置左玩家已有2勝，這次再勝一場達到3勝
        room.scores = {'left': 2, 'right': 1, 'draw': 0}
        room.game.winner = room.left_player.symbol
        
        # 檢查回合結束
        result = room.check_round_end()
        self.assertTrue(result)
        self.assertEqual(room.scores['left'], 3)
        self.assertTrue(room.match_finished)

    def test_check_round_end_match_finish_by_rounds(self):
        """測試因回合數達標而結束比賽"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置已經是第5回合（round_count == 4）
        room.round_count = 4
        room.game.winner = room.left_player.symbol
        
        # 檢查回合結束
        result = room.check_round_end()
        self.assertTrue(result)
        self.assertTrue(room.match_finished)

    def test_check_round_end_no_winner(self):
        """測試回合結束檢查 - 沒有獲勝者"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置遊戲沒有獲勝者
        room.game.winner = None
        
        # 檢查回合結束
        result = room.check_round_end()
        self.assertFalse(result)
        self.assertFalse(room.match_finished)

    def test_reset_alternates_first_player_to_right(self):
        """測試重置時輪替先手到右玩家"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 初始先手是 left
        room.current_first_player = 'left'
        
        # 重置後應該變成 right
        room.reset()
        self.assertEqual(room.current_first_player, 'right')
        self.assertEqual(room.game.turn, room.right_player.symbol)

    def test_get_waiting_room_count(self):
        """測試獲取等待中房間數量"""
        # 初始沒有房間
        self.assertEqual(self.manager.get_waiting_room_count(), 0)
        
        # 創建一個房間（等待中）
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.assertEqual(self.manager.get_waiting_room_count(), 1)
        
        # 加入第二個玩家後，不再等待
        self.manager.join_room(room_id, self.sid2, self.username2)
        self.assertEqual(self.manager.get_waiting_room_count(), 0)

    def test_get_active_room_count(self):
        """測試獲取進行中房間數量"""
        # 初始沒有房間
        self.assertEqual(self.manager.get_active_room_count(), 0)
        
        # 創建一個房間（等待中，不算進行中）
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.assertEqual(self.manager.get_active_room_count(), 0)
        
        # 加入第二個玩家後，變成進行中
        self.manager.join_room(room_id, self.sid2, self.username2)
        self.assertEqual(self.manager.get_active_room_count(), 1)

    def test_get_active_game_count(self):
        """測試獲取正在進行的遊戲數量"""
        # 初始沒有遊戲
        self.assertEqual(self.manager.get_active_game_count(), 0)
        
        # 創建房間並加入玩家
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        
        # 遊戲已開始
        self.assertEqual(self.manager.get_active_game_count(), 1)

    def test_make_move_through_manager_returns_none_for_invalid(self):
        """測試通過 manager 進行無效移動返回 None"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        
        # 對不存在的房間進行移動
        result = self.manager.make_move('non_existent_room', self.sid1, 0, 0)
        self.assertIsNone(result)

    def test_reset_alternates_first_player_to_left(self):
        """測試重置時輪替先手從 right 回到 left (line 194)"""
        room_id = self.manager.create_room(self.sid1, self.username1)
        self.manager.join_room(room_id, self.sid2, self.username2)
        room = self.manager.get_room(room_id)
        
        # 設置當前先手為 right
        room.current_first_player = 'right'
        
        # 重置後應該變成 left
        room.reset()
        self.assertEqual(room.current_first_player, 'left')
        self.assertEqual(room.game.turn, room.left_player.symbol)

    def test_get_room_count(self):
        """測試獲取房間數量 (line 341)"""
        # 初始沒有房間
        self.assertEqual(self.manager.get_room_count(), 0)
        
        # 創建一個房間
        self.manager.create_room(self.sid1, self.username1)
        self.assertEqual(self.manager.get_room_count(), 1)
        
        # 創建另一個房間
        self.manager.create_room(self.sid2, self.username2)
        self.assertEqual(self.manager.get_room_count(), 2)


if __name__ == '__main__':
    unittest.main()
