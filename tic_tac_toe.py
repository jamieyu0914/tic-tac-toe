
# Helper function to check winner
def check_winner(board):
    win_conditions = [
        [0, 1, 2], [3, 4, 5], [6, 7, 8],  # rows
        [0, 3, 6], [1, 4, 7], [2, 5, 8],  # columns
        [0, 4, 8], [2, 4, 6]              # diagonals
    ]
    for cond in win_conditions:
        a, b, c = cond
        if board[a] and board[a] == board[b] == board[c]:
            return board[a]
    if all(board):
        return 'Draw'
    return None
