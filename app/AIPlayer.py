"""
AIPlayer.py - AI 玩家類別
負責實現不同難度的電腦對手邏輯
"""

import random
from typing import Optional, List
from Game import Game, Player


class AIPlayer:
    """
    AI 玩家類別
    提供三種難度的 AI 對手：
    - Simple: 隨機走法
    - Normal: 策略的走法（贏 > 擋 > 中心 > 角落 > 隨機）
    - Hard: Minimax 走法
    """
    
    def __init__(self, difficulty: str = 'normal'):
        """
        初始化 AI 玩家
        
        Args:
            difficulty: 難度等級 ('simple', 'normal', 'hard')
        """
        self.difficulty = difficulty
        self.symbol = Player.O.value  # AI 固定使用 'O'
    
    def get_move(self, board: List[Optional[str]]) -> Optional[int]:
        """
        根據難度獲取 AI 的下一步
        
        Args:
            board: 當前棋盤狀態
            
        Returns:
            Optional[int]: 要走的位置，若無可用位置則返回 None
        """
        available = self._get_available_moves(board)
        if not available:
            return None
        
        if self.difficulty == 'simple':
            return self._simple_move(available)
        elif self.difficulty == 'normal':
            return self._normal_move(board, available)
        elif self.difficulty == 'hard':
            return self._hard_move(board, available)
        else:
            return self._normal_move(board, available)
    
    def _get_available_moves(self, board: List[Optional[str]]) -> List[int]:
        """
        獲取所有可用的移動位置
        
        Args:
            board: 棋盤狀態
            
        Returns:
            List[int]: 空位的索引列表 -> 即棋盤剩餘可走的位置
        """
        return [i for i, cell in enumerate(board) if cell is None]
    
    def _simple_move(self, available: List[int]) -> int:
        """
        簡單模式：隨機選擇一個空位
        
        Args:
            available: 可用位置列表
            
        Returns:
            int: 選擇的位置
        """
        return random.choice(available)
    
    def _normal_move(self, board: List[Optional[str]], available: List[int]) -> int:
        """
        普通模式：使用策略選擇
        策略優先級：贏 > 擋 > 中心 > 角落 > 隨機
        
        Args:
            board: 棋盤狀態
            available: 可用的位置
            
        Returns:
            int: 選擇的位置
        """
        # 1. 如果可以贏，直接走贏棋的步
        win_move = self._find_winning_move(board, self.symbol)
        if win_move is not None:
            return win_move
        
        # 2. 如果對手可以贏，擋住對手
        opponent = Player.X.value
        block_move = self._find_winning_move(board, opponent)
        if block_move is not None:
            return block_move
        
        # 3. 優先走中心位置
        center_position = 4
        if center_position in available:
            return center_position
        
        # 4. 走角落位置
        corner_positions = [0, 2, 6, 8] # 定義角落位置
        corners = []
        for pos in corner_positions:
            if pos in available:
                corners.append(pos)
        if corners:
            return random.choice(corners)
        
        # 5. 隨機選擇剩餘位置
        return random.choice(available)
    
    def _hard_move(self, board: List[Optional[str]], available: List[int]) -> int:
        """
        困難模式：使用 Minimax 走法
        
        Args:
            board: 棋盤狀態
            available: 可用的位置
            
        Returns:
            int: 選擇的位置
        """
        _, best_move = self._minimax(board.copy(), self.symbol)
        if best_move is None: #防止 None 發生
            return random.choice(available)
        return best_move
    
    def _find_winning_move(self, board: List[Optional[str]], player: str) -> Optional[int]:
        """
        找出能夠獲勝的走法
        
        Args:
            board: 棋盤狀態
            player: 玩家符號
            
        Returns:
            Optional[int]: 獲勝的位置，若不存在則返回 None
        """
        available = self._get_available_moves(board)
        for pos in available:
            # 模擬走這一步
            test_board = board.copy() # 傳copy避免修改原board
            test_board[pos] = player
            # 檢查是否獲勝
            if self._check_winner(test_board) == player:
                return pos
        return None
    
    def _minimax(self, board: List[Optional[str]], player: str) -> tuple:
        """
        使用Minimax 演算法
        
        Args:
            board: 棋盤狀態
            player: 當前玩家符號
            
        Returns:
            tuple: (分數, 最佳移動位置)
                  分數：1 (O贏), -1 (X贏), 0 (平局)
        """
        # 檢查遊戲是否結束
        winner = self._check_winner(board)
        if winner == self.symbol:  # O 贏
            return (1, None)
        if winner == Player.X.value:  # X 贏
            return (-1, None)
        if winner == 'Draw':  # 平局
            return (0, None)
        
        available = self._get_available_moves(board)
        
        # O 的回合（最大化）
        if player == self.symbol:
            best_score = -999 # 初始化為極小值，任何分數都會比這個大
            best_move = None # 初始化最佳位置

            # 遍歷所有可用位置，找出分數最高的位置
            for move in available: # 例如遍歷剩餘位置 eg. [0, 3, 5]
                board[move] = self.symbol  # 模擬：AI 下在這個位置
                score, _ = self._minimax(board, Player.X.value) # 遞迴：假設 AI 下了這步後，輪到對手 (X)，看對手會得多少分

                board[move] = None #恢復棋盤，準備試下一個位置

                # 更新最佳分數和位置（AI 要找分數最高的）
                if score > best_score: # 找到更好的走法，更新分數跟位置
                    best_score = score 
                    best_move = move
            return (best_score, best_move) # 返回 AI 的最佳選擇：(最高分, 對應位置)
        
        # X 的回合（最小化）
        else:
            best_score = 999 # 初始化為極大值，任何分數都會比這個小
            best_move = None
            for move in available:
                board[move] = Player.X.value
                score, _ = self._minimax(board, self.symbol) # 遞迴：假設對手下了這步後，輪到 AI (O)，看 AI 會得多少分
                board[move] = None

                # 更新最低分數和位置（要找讓 AI 得分最低的）
                if score < best_score: # 找到對 AI 更不利的走法
                    best_score = score
                    best_move = move
            
             # 這個最低分會返回給上一層的 AI，告訴 AI「如果你走這步，對手會讓你得這麼多分」
            return (best_score, best_move) # 返回對手的選擇：(最低分, 對應位置)
    
    def _check_winner(self, board: List[Optional[str]]) -> Optional[str]:
        """
        檢查棋盤的勝負狀態
        
        Args:
            board: 棋盤狀態
            
        Returns:
            Optional[str]: 'X', 'O', 'Draw' 或 None
        """
        win_conditions = [
            [0, 1, 2], [3, 4, 5], [6, 7, 8],  # 橫向
            [0, 3, 6], [1, 4, 7], [2, 5, 8],  # 縱向
            [0, 4, 8], [2, 4, 6]              # 對角線
        ]
        
        for condition in win_conditions:
            a, b, c = condition
            if (board[a] is not None and  
                board[a] == board[b] == board[c]):
                return board[a] # 返回贏家符號 O 或 X

        # 檢查平局 -> 是否全部格子都被填滿
        if all(cell is not None for cell in board):
            return 'Draw'
        
        return None
