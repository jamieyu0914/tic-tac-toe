"""
Game.py - 井字遊戲核心邏輯類別
負責管理遊戲狀態、勝負判定和遊戲流程控制
"""

from enum import Enum
from typing import Optional, List


class GameMode(Enum):
    """遊戲模式枚舉"""
    COMPUTER = "computer"  # 人機對戰
    PVP = "pvp"           # 玩家對戰


class Difficulty(Enum):
    """AI 難度枚舉"""
    SIMPLE = "simple"   # 簡單（隨機）
    NORMAL = "normal"   # 普通（策略）
    HARD = "hard"       # 困難（Minimax）


class Player(Enum):
    """玩家符號枚舉"""
    X = "X"
    O = "O"


class GameResult(Enum):
    """遊戲結果枚舉"""
    X_WIN = "X"
    O_WIN = "O"
    DRAW = "Draw"
    ONGOING = None


class Game:
    """
    井字遊戲核心類別
    負責：
    - 遊戲狀態管理（棋盤、輪次、勝負）
    - 勝負判定邏輯
    - 遊戲流程控制
    """
    
    # 勝利條件：所有可能的三連線組合
    WIN_CONDITIONS = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 橫向
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 縱向
        [0, 4, 8], [2, 4, 6]              # 對角線
    ]
    
    def __init__(self):
        """初始化遊戲狀態"""
        self.board: List[Optional[str]] = [None] * 9  # 棋盤（9格）
        self.turn: str = Player.X.value              # 當前回合（X 先手）
        self.winner: Optional[str] = None             # 勝者
        self.mode: str = GameMode.COMPUTER.value      # 遊戲模式
        self.difficulty: str = Difficulty.NORMAL.value # AI 難度
        self.started: bool = False                    # 遊戲是否已開始
    
    def reset(self):
        """重置遊戲狀態"""
        self.board = [None] * 9
        self.turn = Player.X.value
        self.winner = None
        self.started = False
    
    def set_mode(self, mode: str, difficulty: Optional[str] = None):
        """
        設置遊戲模式
        
        Args:
            mode: 遊戲模式 ('computer' 或 'pvp')
            difficulty: AI 難度（僅在 computer 模式下有效）
        """
        self.mode = mode
        if mode == GameMode.COMPUTER.value and difficulty:
            self.difficulty = difficulty
        self.reset()
    
    def start(self):
        """開始遊戲"""
        self.reset()
        self.started = True
    
    def make_move(self, position: int, player: Optional[str] = None) -> bool:
        """
        執行移動
        
        Args:
            position: 棋盤位置 (0-8)
            player: 玩家符號（若為 None 則使用當前回合玩家）
            
        Returns:
            bool: 移動是否成功
        """
        # 驗證遊戲狀態
        if not self.started:
            return False
        if self.winner is not None:
            return False
        
        # 驗證位置
        if not (0 <= position < 9):
            return False
        if self.board[position] is not None:
            return False
        
        # 執行移動
        move_player = player if player else self.turn
        self.board[position] = move_player #下棋
        
        # 檢查勝負
        self.winner = self._check_winner()
        
        # 切換回合
        if self.winner is None:
            self.turn = Player.O.value if self.turn == Player.X.value else Player.X.value
        
        return True
    
    def _check_winner(self) -> Optional[str]:
        """
        檢查勝負狀態
        
        Returns:
            Optional[str]: 勝者符號（'X', 'O', 'Draw'）或 None（遊戲繼續）
        """
        # 檢查所有勝利條件
        for condition in self.WIN_CONDITIONS:
            a, b, c = condition
            if (self.board[a] is not None and 
                self.board[a] == self.board[b] == self.board[c]):
                return self.board[a]
        
        # 檢查是否平局（棋盤已滿）
        if all(cell is not None for cell in self.board):
            return GameResult.DRAW.value
        
        # 遊戲繼續
        return None
    
    def get_available_moves(self) -> List[int]:
        """
        獲取所有可用的移動位置
        
        Returns:
            List[int]: 空位的索引列表
        """
        return [i for i, cell in enumerate(self.board) if cell is None]
    
    def is_valid_move(self, position: int) -> bool:
        """
        檢查移動是否有效
        
        Args:
            position: 棋盤位置
            
        Returns:
            bool: 移動是否有效
        """
        return (0 <= position < 9 and 
                self.board[position] is None and 
                self.winner is None and
                self.started)
    
    def get_state(self) -> dict:
        """
        獲取當前遊戲狀態
        
        Returns:
            dict: 包含完整遊戲狀態的字典
        """
        return {
            'board': self.board.copy(),    # 棋盤狀態
            'turn': self.turn,             # 紀錄當前回合玩家
            'winner': self.winner,         # None, 'X', 'O', 'Draw'
            'mode': self.mode,             # 'computer' 或 'pvp'
            'difficulty': self.difficulty, # AI 難度
            'started': self.started        # 遊戲是否已開始
        }
    
    def load_state(self, state: dict):
        """
        載入遊戲狀態
        
        Args:
            state: 遊戲狀態字典
        """
        self.board = state.get('board', [None] * 9)
        self.turn = state.get('turn', Player.X.value)
        self.winner = state.get('winner')
        self.mode = state.get('mode', GameMode.COMPUTER.value)
        self.difficulty = state.get('difficulty', Difficulty.NORMAL.value)
        self.started = state.get('started', False)
