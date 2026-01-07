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