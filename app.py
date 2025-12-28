from flask import Flask, render_template, request, redirect, url_for, session
import random
from flask_socketio import SocketIO

from chatroom import register_chat_events
from pvp import init_game_state, set_mode, join_pvp, start_game, handle_cell_click

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
        username = request.form.get('username', '').strip()
        icon = request.form.get('icon')
        shown_icons = session.get('login_icons', [])
        if not username:
            error = '請輸入使用者名稱'
        elif not icon:
            error = '請選擇一個圖示'
        elif icon not in shown_icons:
            error = '所選圖示無效，請重新選擇'
        else:
            session.pop('login_icons', None)
            session['user'] = username
            session['icon'] = icon
            return redirect(url_for('home'))
        
    ICON_POOL = ['😺','🐶','🐼','🚀','🎃','🐧','🐵','🐸','🦊','🐢','🐟','🐯','🦁','🐷','🦄']

    icons = random.sample(ICON_POOL, 5)
    session['login_icons'] = icons
    return render_template('login.html', error=error, icons=icons)

# 首頁，需登入
@app.route('/')
def home():
    if 'user' not in session:
        return redirect(url_for('login'))
    theme = request.args.get('theme', '').lower()
    if not theme:
        theme = random.choice(['christmas', 'newyear'])
    return render_template('index.html', user=session['user'], theme=theme)

# 遊戲頁，需登入
@app.route('/game', methods=['GET', 'POST'])
def game():
    if 'user' not in session:
        return redirect(url_for('login'))
    # 初始化遊戲狀態 (moved to pvp module)
    init_game_state(session)
    board = session['board']
    turn = session['turn']
    winner = session['winner']
    mode = session.get('mode', 'computer')
    difficulty = session.get('difficulty', 'normal')
    pvp_waiting = session.get('pvp_waiting', False)

    if request.method == 'POST':
        # Mode selection form
        if request.form.get('action') == 'set_mode':
            set_mode(session, request.form)
            return redirect(url_for('game'))

        # join pvp (placeholder for multiplayer)
        if request.form.get('action') == 'join_pvp':
            join_pvp(session)
            return redirect(url_for('game'))

        # start game after selecting mode
        if request.form.get('action') == 'start_game':
            start_game(session)
            return redirect(url_for('game'))

        # Cell click (player move)
        # ignore cell clicks if game hasn't been started (handled in pvp.handle_cell_click)
        if 'cell' in request.form:
            handle_cell_click(session, request.form)
        return redirect(url_for('game'))

    return render_template('game.html', board=board, turn=turn, winner=winner,
                           mode=mode, difficulty=difficulty, pvp_waiting=pvp_waiting,
                           started=session.get('started', False))


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
    session.pop('icon', None)
    return redirect(url_for('login'))


# Run the app (optional, for running directly)
if __name__ == '__main__':
    socketio.run(app, debug=True)

