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
        self.assertEqual(self.game.board, [[None] * 3 for _ in range(3)])
        self.assertEqual(self.game.turn, Player.X.value)
        self.assertIsNone(self.game.winner)
        self.assertFalse(self.game.started)
    
    def test_reset(self):
        """測試遊戲重置功能"""
        # 先進行一些操作
        self.game.start()
        self.game.make_move(0, 0)  # (0, 0)
        self.game.make_move(0, 1)  # (0, 1)
        
        # 重置
        self.game.reset()
        
        # 驗證狀態
        self.assertEqual(self.game.board, [[None] * 3 for _ in range(3)])
        self.assertEqual(self.game.turn, Player.X.value)
        self.assertIsNone(self.game.winner)
        self.assertFalse(self.game.started)
    
    # ==================== 遊戲開始測試 ====================
    
    def test_start_game(self):
        """測試開始遊戲"""
        self.game.start()
        self.assertTrue(self.game.started)
        self.assertEqual(self.game.board, [[None] * 3 for _ in range(3)])
    
    # ==================== 移動測試 ====================
    
    def test_make_move_success(self):
        """測試成功的移動"""
        self.game.start()
        result = self.game.make_move(0, 0)  # 位置 (0, 0)
        self.assertTrue(result)
        self.assertEqual(self.game.board[0][0], Player.X.value)
        self.assertEqual(self.game.turn, Player.O.value)
    
    def test_make_move_before_start(self):
        """測試在遊戲開始前移動"""
        result = self.game.make_move(0, 0)
        self.assertFalse(result)
        self.assertEqual(self.game.board[0][0], None)
    
    def test_make_move_occupied_position(self):
        """測試在已佔用的位置移動"""
        self.game.start()
        self.game.make_move(0, 0)
        result = self.game.make_move(0, 0)
        self.assertFalse(result)
        self.assertEqual(self.game.turn, Player.O.value)  # 回合不應改變
    
    def test_make_move_invalid_position(self):
        """測試無效的位置"""
        self.game.start()
        result1 = self.game.make_move(-1, 0)
        result2 = self.game.make_move(0, 3)
        result3 = self.game.make_move(5, 5)
        
        self.assertFalse(result1)
        self.assertFalse(result2)
        self.assertFalse(result3)
    
    def test_make_move_with_specific_player(self):
        """測試指定玩家移動"""
        self.game.start()
        result = self.game.make_move(0, 0, Player.O.value)
        self.assertTrue(result)
        self.assertEqual(self.game.board[0][0], Player.O.value)
    
    def test_turn_switching(self):
        """測試回合切換"""
        self.game.start()
        
        self.assertEqual(self.game.turn, Player.X.value)
        self.game.make_move(0, 0)
        
        self.assertEqual(self.game.turn, Player.O.value)
        self.game.make_move(0, 1)
        
        self.assertEqual(self.game.turn, Player.X.value)
    
    # ==================== 勝負判定測試 ====================
    
    def test_win_horizontal_top(self):
        """測試第一行獲勝"""
        self.game.start()
        # X 贏在第一行: (0,0), (0,1), (0,2)
        moves = [(0,0), (1,0), (0,1), (1,1), (0,2)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_horizontal_middle(self):
        """測試第二行獲勝"""
        self.game.start()
        # X 贏在第二行: (1,0), (1,1), (1,2)
        moves = [(1,0), (0,0), (1,1), (0,1), (1,2)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_horizontal_bottom(self):
        """測試第三行獲勝"""
        self.game.start()
        # X 贏在第三行: (2,0), (2,1), (2,2)
        moves = [(2,0), (0,0), (2,1), (0,1), (2,2)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_vertical_left(self):
        """測試第一列獲勝"""
        self.game.start()
        # X 贏在第一列: (0,0), (1,0), (2,0)
        moves = [(0,0), (0,1), (1,0), (0,2), (2,0)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_vertical_middle(self):
        """測試第二列獲勝"""
        self.game.start()
        # X 贏在第二列: (0,1), (1,1), (2,1)
        moves = [(0,1), (0,0), (1,1), (0,2), (2,1)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_vertical_right(self):
        """測試第三列獲勝"""
        self.game.start()
        # X 贏在第三列: (0,2), (1,2), (2,2)
        moves = [(0,2), (0,0), (1,2), (0,1), (2,2)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_diagonal_main(self):
        """測試主對角線獲勝"""
        self.game.start()
        # X 贏在主對角線: (0,0), (1,1), (2,2)
        moves = [(0,0), (0,1), (1,1), (0,2), (2,2)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_win_diagonal_anti(self):
        """測試副對角線獲勝"""
        self.game.start()
        # X 贏在副對角線: (0,2), (1,1), (2,0)
        moves = [(0,2), (0,0), (1,1), (0,1), (2,0)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.X.value)
    
    def test_player_o_wins(self):
        """測試 O 玩家獲勝"""
        self.game.start()
        # O 贏在第一列: (0,0), (1,0), (2,0)
        moves = [(0,1), (0,0), (0,2), (1,0), (2,1), (2,0)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, Player.O.value)
    
    def test_draw(self):
        """測試平局"""
        self.game.start()
        # O X X
        # X X O
        # O O X
        moves = [(0,1), (0,0), (0,2), (1,1), (1,0), (1,2), (2,1), (2,0), (2,2)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        self.assertEqual(self.game.winner, GameResult.DRAW.value)
        
        self.assertEqual(self.game.winner, GameResult.DRAW.value)
    
    def test_no_move_after_win(self):
        """測試獲勝後無法繼續移動"""
        self.game.start()
        # X 贏在第一行
        moves = [(0,0), (1,0), (0,1), (1,1), (0,2)]
        for row, col in moves:
            self.game.make_move(row, col)
        
        # 嘗試繼續移動
        result = self.game.make_move(1, 2)
        self.assertFalse(result)
        self.assertIsNone(self.game.board[1][2])
    
    # ==================== 輔助方法測試 ====================
    
    # ==================== 邊界條件測試 ====================
    
    def test_full_game_sequence(self):
        """測試完整的遊戲流程"""
        self.game.start()
        
        # 完整遊戲流程 - X 贏在第一列
        moves = [(0,0), (0,1), (1,0), (1,1), (2,0)]
        
        for i, (row, col) in enumerate(moves):
            result = self.game.make_move(row, col)
            self.assertTrue(result)
            
            if i < len(moves) - 1:
                self.assertIsNone(self.game.winner)
            else:
                self.assertEqual(self.game.winner, Player.X.value)
    
    def test_multiple_games(self):
        """測試多次遊戲"""
        for _ in range(3):
            self.game.start()
            self.game.make_move(0, 0)
            self.game.make_move(0, 1)
            self.game.reset()
            
            # 每次重置後應回到初始狀態
            self.assertEqual(self.game.board, [[None] * 3 for _ in range(3)])
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
        self.game.make_move(0, 0)  # X
        self.game.make_move(1, 0)  # O
        self.game.make_move(0, 1)  # X
        
        self.assertIsNone(self.game.winner)
    
    def test_all_positions(self):
        """測試所有位置都可以正確下棋"""
        for row in range(3):
            for col in range(3):
                game = Game()
                game.start()
                result = game.make_move(row, col)
                self.assertTrue(result)
                self.assertEqual(game.board[row][col], Player.X.value)


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
