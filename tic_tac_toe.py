from flask import Flask, render_template, request, redirect, url_for, session

app = Flask(__name__)
app.secret_key = 'tic-tac-toe-secret-key'

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

@app.route('/', methods=['GET', 'POST'])
def index():
    if 'board' not in session:
        session['board'] = [None] * 9
        session['turn'] = 'X'
        session['winner'] = None
    board = session['board']
    turn = session['turn']
    winner = session['winner']

    if request.method == 'POST' and not winner:
        idx = int(request.form['cell'])
        if board[idx] is None:
            board[idx] = turn
            winner = check_winner(board)
            session['winner'] = winner
            session['turn'] = 'O' if turn == 'X' else 'X'
            session['board'] = board
        return redirect(url_for('index'))

    return render_template('index.html', board=board, turn=turn, winner=winner)

@app.route('/reset')
def reset():
    session.pop('board', None)
    session.pop('turn', None)
    session.pop('winner', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)
