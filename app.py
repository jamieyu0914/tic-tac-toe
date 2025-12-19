from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO

from tic_tac_toe import check_winner
from chatroom import register_chat_events

# Create an instance of the Flask class

app = Flask(__name__)
app.secret_key = 'tic-tac-toe-login-secret'
socketio = SocketIO(app)
register_chat_events(socketio)


# 登入頁
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        # 簡單帳密驗證（可改成資料庫驗證）
        if username == 'user' and password == '1234':
            session['user'] = username
            return redirect(url_for('home'))
        else:
            error = '帳號或密碼錯誤'
    return render_template('login.html', error=error)

# 首頁，需登入
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    return render_template('index.html', user=session['user'])

# 遊戲頁，需登入
@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'user' not in session:
        return redirect(url_for('login'))
    # 初始化遊戲狀態
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
        return redirect(url_for('game'))

    return render_template('game.html', board=board, turn=turn, winner=winner)


# 重置遊戲
@app.route('/reset')
def reset():
    session.pop('board', None)
    session.pop('turn', None)
    session.pop('winner', None)
    return redirect(url_for('game'))

# 登出
@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('login'))


# Run the app (optional, for running directly)
if __name__ == '__main__':
    socketio.run(app, debug=True)

