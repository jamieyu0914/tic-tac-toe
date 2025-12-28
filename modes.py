from tic_tac_toe import check_winner
import random


def available_moves(board):
    return [i for i, v in enumerate(board) if v is None]


def find_winning_move(board, player):
    for i in available_moves(board):
        board_copy = board.copy()
        board_copy[i] = player
        if check_winner(board_copy) == player:
            return i
    return None


def minimax(board, player):
    # returns (score, move_index)
    winner = check_winner(board)
    if winner == 'O':
        return (1, None)
    if winner == 'X':
        return (-1, None)
    if winner == 'Draw':
        return (0, None)

    moves = available_moves(board)
    if player == 'O':
        best_score = -999
        best_move = None
        for m in moves:
            board[m] = 'O'
            score, _ = minimax(board, 'X')
            board[m] = None
            if score > best_score:
                best_score = score
                best_move = m
        return (best_score, best_move)
    else:
        best_score = 999
        best_move = None
        for m in moves:
            board[m] = 'X'
            score, _ = minimax(board, 'O')
            board[m] = None
            if score < best_score:
                best_score = score
                best_move = m
        return (best_score, best_move)


def computer_move(board, difficulty):
    moves = available_moves(board)
    if not moves:
        return None
    # simple: random
    if difficulty == 'simple':
        return random.choice(moves)
    # normal: win > block > center > corner > random
    if difficulty == 'normal':
        win = find_winning_move(board, 'O')
        if win is not None:
            return win
        block = find_winning_move(board, 'X')
        if block is not None:
            return block
        if 4 in moves:
            return 4
        corners = [i for i in [0,2,6,8] if i in moves]
        if corners:
            return random.choice(corners)
        return random.choice(moves)
    # hard: minimax
    _, move = minimax(board.copy(), 'O')
    if move is None:
        return random.choice(moves)
    return move
