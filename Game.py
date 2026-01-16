"""
Game.py - 井字遊戲核心邏輯類別
負責管理遊戲狀態、勝負判定和遊戲流程控制
"""

from enum import Enum
from typing import Optional


class Player(Enum):
    """X 和 O 的枚舉"""
    X = "X"
    O = "O"


class GameResult(Enum):
    """遊戲結果枚舉"""
    X_WIN = "X"
    O_WIN = "O"
    DRAW = "Draw"


class Game:
    """
    井字遊戲核心類別
    負責：
    - 遊戲狀態管理（棋盤、輪次、勝負）
    - 勝負判定邏輯
    - 遊戲流程控制
    """
    
    # 所有贏的組合 (橫3直3斜2) - 使用座標 (row, col)
    WIN_CONDITIONS = [
        [(0, 0), (0, 1), (0, 2)], [(1, 0), (1, 1), (1, 2)], [(2, 0), (2, 1), (2, 2)],  # 橫排
        [(0, 0), (1, 0), (2, 0)], [(0, 1), (1, 1), (2, 1)], [(0, 2), (1, 2), (2, 2)],  # 直排
        [(0, 0), (1, 1), (2, 2)], [(0, 2), (1, 1), (2, 0)]                            # 對角
    ]
    
    def __init__(self):
        """初始化 - 設定空白棋盤和遊戲狀態"""
        self.board = [[None] * 3 for _ in range(3)]  # 3x3棋盤用二維陣列存
        self.turn = Player.X.value              # 固定X永遠先手
        self.winner = None                     # 贏家是誰
        self.started = False                    # 遊戲開始了沒
    
    def reset(self):
        """清空棋盤，重新開始"""
        self.board = [[None] * 3 for _ in range(3)]
        self.turn = Player.X.value
        self.winner = None
        self.started = False
    
    def start(self):
        """開始遊戲"""
        self.reset()
        self.started = True
    
    def make_move(self, row: int, col: int, player=None) -> bool:
        """
        下棋 
        (可用 player 強制指定 X 或 O，不指定則按回合)
        """
        if not self.started:
            return False
        if self.winner is not None:
            return False
        
        # 驗證座標
        if not (0 <= row < 3 and 0 <= col < 3):
            return False
        if self.board[row][col] is not None:
            return False
        
        # 執行移動
        move_player = player if player else self.turn
        self.board[row][col] = move_player  # 下棋
        
        # 檢查勝負
        self.winner = self._check_winner()
        
        # 切換回合
        if self.winner is None:
            self.turn = Player.O.value if self.turn == Player.X.value else Player.X.value
        
        return True
    
    def _check_winner(self):
        """
        檢查勝負狀態，返回勝者符號 ('X', 'O', 'Draw') 或 None (遊戲繼續)
        """
        for condition in self.WIN_CONDITIONS:
            pos1, pos2, pos3 = condition
            r1, c1 = pos1
            r2, c2 = pos2
            r3, c3 = pos3
            if (self.board[r1][c1] is not None and 
                self.board[r1][c1] == self.board[r2][c2] == self.board[r3][c3]):
                # 直接返回勝者符號（'X' 或 'O'）
                return self.board[r1][c1]
        
        # 檢查是否平局（棋盤已滿）
        if all(self.board[row][col] is not None for row in range(3) for col in range(3)):
            return GameResult.DRAW.value
        
        # 遊戲繼續
        return None


if __name__ == '__main__':
    """測試井字遊戲邏輯"""
    
    print("===== 井字遊戲測試 =====\n")
    
    # 測試1: X獲勝（橫排）
    print("測試1: X獲勝（第一橫排）")
    game1 = Game()
    game1.start()
    moves1 = [(0, 0), (1, 0), (0, 1), (1, 1), (0, 2)]  # X贏在第一橫排
    for row, col in moves1:
        current_player = game1.turn  # 記錄當前玩家
        game1.make_move(row, col)
        status = '遊戲結束' if game1.winner else f"輪到 {game1.turn}"
        print(f"  {current_player} 下在 ({row}, {col}) -> {status}")
    print(f"  結果: {game1.winner}")
    print(f"  預期: {GameResult.X_WIN.value}")
    print(f"  測試{'通過' if game1.winner == GameResult.X_WIN.value else '失敗'}！\n")
    
    # 測試2: O獲勝（直排）
    print("測試2: O獲勝（第一直排）")
    game2 = Game()
    game2.start()
    moves2 = [(0, 1), (0, 0), (1, 1), (1, 0), (0, 2), (2, 0)]  # O贏在第一直排
    for row, col in moves2:
        current_player = game2.turn  # 記錄當前玩家
        game2.make_move(row, col)
        status = '遊戲結束' if game2.winner else f"輪到 {game2.turn}"
        print(f"  {current_player} 下在 ({row}, {col}) -> {status}")
    print(f"  結果: {game2.winner}")
    print(f"  預期: {GameResult.O_WIN.value}")
    print(f"  測試{'通過' if game2.winner == GameResult.O_WIN.value else '失敗'}！\n")
    
    # 測試3: 平局
    print("測試3: 平局")
    game3 = Game()
    game3.start()
    # X O X
    # O X X
    # O X O
    moves3 = [(0, 0), (0, 1), (0, 2), (1, 0), (1, 1), (2, 0), (1, 2), (2, 2), (2, 1)]
    for row, col in moves3:
        current_player = game3.turn  # 記錄當前玩家
        game3.make_move(row, col)
        status = '遊戲結束' if game3.winner else f"輪到 {game3.turn}"
        print(f"  {current_player} 下在 ({row}, {col}) -> {status}")
    print(f"  結果: {game3.winner}")
    print(f"  預期: {GameResult.DRAW.value}")
    print(f"  測試{'通過' if game3.winner == GameResult.DRAW.value else '失敗'}！\n")
    
    # 顯示平局的最終棋盤
    print("  平局棋盤:")
    for i, row in enumerate(game3.board):
        row_str = " | ".join([cell if cell else " " for cell in row])
        print(f"    第{i}行: {row_str}")
    
    # 測試4: X獲勝（對角線）
    print("測試4: X獲勝（對角線）")
    game4 = Game()
    game4.start()
    moves4 = [(0, 0), (0, 1), (1, 1), (0, 2), (2, 2)]  # X贏在對角線
    for row, col in moves4:
        current_player = game4.turn  # 記錄當前玩家
        game4.make_move(row, col)
        status = '遊戲結束' if game4.winner else f"輪到 {game4.turn}"
        print(f"  {current_player} 下在 ({row}, {col}) -> {status}")
    print(f"  結果: {game4.winner}")
    print(f"  預期: {GameResult.X_WIN.value}")
    print(f"  測試{'通過' if game4.winner == GameResult.X_WIN.value else '失敗'}！\n")
    
    # 測試5: 棋盤顯示
    print("測試5: 棋盤顯示（測試4的最終棋盤）")
    print("\n  座標系統說明:")
    print("    (0,0) | (0,1) | (0,2)")
    print("    ------+-------+------")
    print("    (1,0) | (1,1) | (1,2)")
    print("    ------+-------+------")
    print("    (2,0) | (2,1) | (2,2)")
    print("\n  實際棋盤:")
    for i, row in enumerate(game4.board):
        row_str = " | ".join([cell if cell else " " for cell in row])
        print(f"  第{i}行: {row_str}")
        if i < 2:
            print("        ---------")
    
    print("\n===== 所有測試完成 =====")

