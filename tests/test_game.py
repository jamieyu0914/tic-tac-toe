"""
test_game.py - 井字遊戲單元測試
測試 Game.py 的所有核心功能
"""

import unittest
import sys
import os

# 添加 app 目錄到路徑
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from Game import Game, Player, GameResult


class TestGame(unittest.TestCase):
    """Game 類別的單元測試"""
    
    def setUp(self):
        """每個測試前初始化遊戲實例"""
        self.game = Game()
    
    # ==================== 初始化測試 ====================
    
    def test_initial_state(self):
        """測試遊戲初始狀態"""
        self.assertEqual(self.game.board, [None] * 9)
        self.assertEqual(self.game.turn, Player.X.value)
        self.assertIsNone(self.game.winner)
        self.assertFalse(self.game.started)
    
    def test_reset(self):
        """測試遊戲重置功能"""
        # 先進行一些操作
        self.game.start()
        self.game.make_move(0)
        self.game.make_move(1)
        
        # 重置
        self.game.reset()
        
        # 驗證狀態
        self.assertEqual(self.game.board, [None] * 9)
        self.assertEqual(self.game.turn, Player.X.value)
        self.assertIsNone(self.game.winner)
        self.assertFalse(self.game.started)
    
    # ==================== 遊戲開始測試 ====================
    
    def test_start_game(self):
        """測試開始遊戲"""
        self.game.start()
        self.assertTrue(self.game.started)
        self.assertEqual(self.game.board, [None] * 9)
    
    # ==================== 移動測試 ====================
    
    def test_make_move_success(self):
        """測試成功的移動"""
        self.game.start()
        result = self.game.make_move(0)
        self.assertTrue(result)
        self.assertEqual(self.game.board[0], Player.X.value)
        self.assertEqual(self.game.turn, Player.O.value)
    
    def test_make_move_before_start(self):
        """測試在遊戲開始前移動"""
        result = self.game.make_move(0)
        self.assertFalse(result)
        self.assertEqual(self.game.board[0], None)
    
    def test_make_move_occupied_position(self):
        """測試在已佔用的位置移動"""
        self.game.start()
        self.game.make_move(0)
        result = self.game.make_move(0)
        self.assertFalse(result)
        self.assertEqual(self.game.turn, Player.O.value)  # 回合不應改變
    
    def test_make_move_invalid_position(self):
        """測試無效的位置"""
        self.game.start()
        result1 = self.game.make_move(-1)
        result2 = self.game.make_move(9)
        result3 = self.game.make_move(100)
        
        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)
    
    def test_make_move_with_specific_player(self):
        """測試指定玩家移動"""
        self.game.start()
        result = self.game.make_move(0, Player.O.value)
        self.assertTrue(result)
        self.assertEqual(self.game.board[0], Player.O.value)
    
    def test_turn_switching(self):
        """測試回合切換"""
        self.game.start()
        
        self.assertEqual(self.game.turn, Player.X.value)
        self.game.make_move(0)
        
        self.assertEqual(self.game.turn, Player.O.value)
        self.game.make_move(1)
        
        self.assertEqual(self.game.turn, Player.X.value)
    
    # ==================== 勝負判定測試 ====================
    
    def test_win_horizontal_top(self):
        """測試第一行獲勝"""
        self.game.start()
        moves = [0, 3, 1, 4, 2]  # X 贏在第一行
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_horizontal_middle(self):
        """測試第二行獲勝"""
        self.game.start()
        moves = [3, 0, 4, 1, 5]  # X 贏在第二行
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_horizontal_bottom(self):
        """測試第三行獲勝"""
        self.game.start()
        moves = [6, 0, 7, 1, 8]  # X 贏在第三行
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_vertical_left(self):
        """測試第一列獲勝"""
        self.game.start()
        moves = [0, 1, 3, 2, 6]  # X 贏在第一列
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_vertical_middle(self):
        """測試第二列獲勝"""
        self.game.start()
        moves = [1, 0, 4, 2, 7]  # X 贏在第二列
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_vertical_right(self):
        """測試第三列獲勝"""
        self.game.start()
        moves = [2, 0, 5, 1, 8]  # X 贏在第三列
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_diagonal_main(self):
        """測試主對角線獲勝"""
        self.game.start()
        moves = [0, 1, 4, 2, 8]  # X 贏在主對角線
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_diagonal_anti(self):
        """測試副對角線獲勝"""
        self.game.start()
        moves = [2, 0, 4, 1, 6]  # X 贏在副對角線
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_player_o_wins(self):
        """測試 O 玩家獲勝"""
        self.game.start()
        moves = [1, 0, 2, 3, 7, 6]  # O 贏在第一列
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, Player.O.value)
    
    def test_draw(self):
        """測試平局"""
        self.game.start()
        # O X X
        # X X O
        # O O X
        moves = [1, 0, 2, 4, 3, 5, 7, 6, 8]
        for pos in moves:
            self.game.make_move(pos)
        
        self.assertEqual(self.game.winner, GameResult.DRAW.value)
    
    def test_no_move_after_win(self):
        """測試獲勝後無法繼續移動"""
        self.game.start()
        moves = [0, 3, 1, 4, 2]  # X 贏
        for pos in moves:
            self.game.make_move(pos)
        
        # 嘗試繼續移動
        result = self.game.make_move(5)
        self.assertFalse(result)
        self.assertIsNone(self.game.board[5])
    
    # ==================== 輔助方法測試 ====================
    
    def test_get_available_moves(self):
        """測試獲取可用移動位置"""
        self.game.start()
        
        # 初始狀態
        available = self.game.get_available_moves()
        self.assertEqual(len(available), 9)
        self.assertEqual(available, [0, 1, 2, 3, 4, 5, 6, 7, 8])
        
        # 下一步
        self.game.make_move(0)
        available = self.game.get_available_moves()
        self.assertEqual(len(available), 8)
        self.assertNotIn(0, available)
        
        # 再下一步
        self.game.make_move(4)
        available = self.game.get_available_moves()
        self.assertEqual(len(available), 7)
        self.assertNotIn(0, available)
        self.assertNotIn(4, available)
    
    def test_is_valid_move(self):
        """測試移動有效性檢查"""
        self.game.start()
        
        # 有效移動
        self.assertTrue(self.game.is_valid_move(0))
        self.assertTrue(self.game.is_valid_move(4))
        self.assertTrue(self.game.is_valid_move(8))
        
        # 無效位置
        self.assertFalse(self.game.is_valid_move(-1))
        self.assertFalse(self.game.is_valid_move(9))
        
        # 已佔用位置
        self.game.make_move(0)
        self.assertFalse(self.game.is_valid_move(0))
        
        # 遊戲結束後
        self.game.start()
        moves = [0, 3, 1, 4, 2]  # X 贏
        for pos in moves:
            self.game.make_move(pos)
        self.assertFalse(self.game.is_valid_move(5))
    
    # ==================== 狀態管理測試 ====================
    
    def test_get_state(self):
        """測試獲取遊戲狀態"""
        self.game.start()
        self.game.make_move(0)
        
        state = self.game.get_state()
        
        self.assertIsInstance(state, dict)
        self.assertIn('board', state)
        self.assertIn('turn', state)
        self.assertIn('winner', state)
        self.assertIn('started', state)
        
        self.assertEqual(state['board'][0], Player.X.value)
        self.assertEqual(state['turn'], Player.O.value)
        self.assertIsNone(state['winner'])
        self.assertTrue(state['started'])
    
    def test_load_state(self):
        """測試載入遊戲狀態"""
        # 創建狀態
        state = {
            'board': ['X', 'O', None, 'X', None, None, None, None, None],
            'turn': Player.O.value,
            'winner': None,
            'started': True
        }
        
        # 載入狀態
        self.game.load_state(state)
        
        # 驗證
        self.assertEqual(self.game.board, state['board'])
        self.assertEqual(self.game.turn, Player.O.value)
        self.assertIsNone(self.game.winner)
        self.assertTrue(self.game.started)
    
    def test_state_immutability(self):
        """測試狀態獲取時的不可變性"""
        self.game.start()
        self.game.make_move(0)
        
        state = self.game.get_state()
        original_board = self.game.board.copy()
        
        # 修改返回的狀態
        state['board'][1] = 'X'
        
        # 驗證原始遊戲狀態未被修改
        self.assertEqual(self.game.board, original_board)
    
    # ==================== 邊界條件測試 ====================
    
    def test_full_game_sequence(self):
        """測試完整的遊戲流程"""
        self.game.start()
        
        # 完整遊戲流程
        moves = [0, 1, 3, 4, 6]  # X 贏在第一列
        
        for i, pos in enumerate(moves):
            result = self.game.make_move(pos)
            self.assertTrue(result)
            
            if i < len(moves) - 1:
                self.assertIsNone(self.game.winner)
            else:
                self.assertEqual(self.game.winner, Player.X.value)
    
    def test_multiple_games(self):
        """測試多次遊戲"""
        for _ in range(3):
            self.game.start()
            self.game.make_move(0)
            self.game.make_move(1)
            self.game.reset()
            
            # 每次重置後應回到初始狀態
            self.assertEqual(self.game.board, [None] * 9)
            self.assertEqual(self.game.turn, Player.X.value)
            self.assertIsNone(self.game.winner)


class TestGameEdgeCases(unittest.TestCase):
    """Game 類別的邊界情況測試"""
    
    def setUp(self):
        """每個測試前初始化遊戲實例"""
        self.game = Game()
    
    def test_empty_board_no_winner(self):
        """測試空棋盤時無獲勝者"""
        self.game.start()
        self.assertIsNone(self.game._check_winner())
    
    def test_partial_line_no_winner(self):
        """測試部分連線時無獲勝者"""
        self.game.start()
        self.game.make_move(0)  # X
        self.game.make_move(3)  # O
        self.game.make_move(1)  # X
        
        self.assertIsNone(self.game.winner)
    
    def test_all_positions(self):
        """測試所有位置都可以正確下棋"""
        for pos in range(9):
            game = Game()
            game.start()
            result = game.make_move(pos)
            self.assertTrue(result)
            self.assertEqual(game.board[pos], Player.X.value)


def run_tests():
    """執行所有測試"""
    # 創建測試套件
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()
    
    # 添加所有測試
    suite.addTests(loader.loadTestsFromTestCase(TestGame))
    suite.addTests(loader.loadTestsFromTestCase(TestGameEdgeCases))
    
    # 執行測試
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # 顯示測試結果摘要
    print("\n" + "=" * 70)
    print("測試摘要")
    print("=" * 70)
    print(f"總測試數: {result.testsRun}")
    print(f"成功: {result.testsRun - len(result.failures) - len(result.errors)}")
    print(f"失敗: {len(result.failures)}")
    print(f"錯誤: {len(result.errors)}")
    print("=" * 70)
    
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
