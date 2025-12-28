"""
app.py - Flask 應用主程式
負責路由管理和 HTTP 請求處理
"""

from flask import Flask, render_template, request, redirect, url_for, session
import random
from flask_socketio import SocketIO
from flask_cors import CORS

from chatroom import register_chat_events
from Game import Game
from AIPlayer import AIPlayer

# 創建 Flask 應用實例
app = Flask(__name__)
CORS(app)
app.secret_key = 'tic-tac-toe-login-secret'

# 創建 Socket.IO 實例（用於聊天室和 PVP 對戰）
# 允許跨域連接，生產環境建議限制來源
socketio = SocketIO(app, cors_allowed_origins="*")
register_chat_events(socketio)


# ============================================================
# 輔助函數
# ============================================================

def get_or_create_game() -> Game:
    """
    從 session 獲取或創建遊戲實例
    
    Returns:
        Game: 遊戲實例
    """
    if 'game_state' not in session:
        game = Game()
        session['game_state'] = game.get_state()
        return game
    
    # 從 session 載入遊戲狀態
    game = Game()
    game.load_state(session['game_state'])
    return game


def save_game(game: Game):
    """
    將遊戲狀態保存到 session
    
    Args:
        game: 遊戲實例
    """
    session['game_state'] = game.get_state()


# ============================================================
# 路由定義
# ============================================================

# 登入頁面
@app.route('/login', methods=['GET', 'POST'])
def login():
    """
    登入頁面處理
    - GET: 顯示登入表單（隨機顯示 5 個圖示）
    - POST: 驗證登入資訊並創建 session
    """
    # 如果已登入，重定向到首頁
    if 'user' in session:
        return redirect(url_for('home'))

    error = None
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        icon = request.form.get('icon')
        shown_icons = session.get('login_icons', [])
        
        # 驗證輸入
        if not username:
            error = '請輸入使用者名稱'
        elif not icon:
            error = '請選擇一個圖示'
        elif icon not in shown_icons:
            error = '所選圖示無效，請重新選擇'
        else:
            # 登入成功
            session.pop('login_icons', None)
            session['user'] = username
            session['icon'] = icon
            return redirect(url_for('home'))
    
    # 生成隨機圖示選項（每次刷新不同）
    ICON_POOL = ['😺','🐶','🐼','🚀','🎃','🐧','🐵','🐸','🦊','🐢','🐟','🐯','🦁','🐷','🦄']
    icons = random.sample(ICON_POOL, 5)
    session['login_icons'] = icons
    
    return render_template('login.html', error=error, icons=icons)


# 首頁（需要登入）
@app.route('/')
def home():
    """
    首頁處理
    - 顯示主題選擇（聖誕或新年主題）
    - 需要登入才能訪問
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 隨機選擇主題（如果 URL 沒有指定）
    theme = request.args.get('theme', '').lower()
    if not theme:
        theme = random.choice(['christmas', 'newyear'])
    
    return render_template('index.html', user=session['user'], theme=theme)


# 遊戲頁面（需要登入）
@app.route('/game', methods=['GET', 'POST'])
def game():
    """
    遊戲頁面處理
    - GET: 顯示遊戲界面
    - POST: 處理遊戲操作（模式設置、開始遊戲、移動棋子）
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 獲取或創建遊戲實例
    game_instance = get_or_create_game()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        # 設置遊戲模式
        if action == 'set_mode':
            mode = request.form.get('mode', 'computer')
            difficulty = request.form.get('difficulty', 'normal')
            game_instance.set_mode(mode, difficulty)
            save_game(game_instance)
            return redirect(url_for('game'))
        
        # 開始遊戲
        elif action == 'start_game':
            game_instance.start()
            save_game(game_instance)
            return redirect(url_for('game'))
        
        # 玩家移動（僅限電腦模式）
        elif 'cell' in request.form and game_instance.mode == 'computer':
            try:
                position = int(request.form['cell'])
                
                # 玩家移動
                if game_instance.make_move(position):
                    save_game(game_instance)
                    
                    # AI 回應（如果遊戲還未結束）
                    if not game_instance.winner and game_instance.turn == 'O':
                        ai = AIPlayer(game_instance.difficulty)
                        ai_move = ai.get_move(game_instance.board)
                        if ai_move is not None:
                            game_instance.make_move(ai_move)
                            save_game(game_instance)
            
            except (ValueError, TypeError):
                pass
            
            return redirect(url_for('game'))
    
    # 準備模板數據
    state = game_instance.get_state()
    return render_template(
        'game.html',
        board=state['board'],
        turn=state['turn'],
        winner=state['winner'],
        mode=state['mode'],
        difficulty=state['difficulty'],
        pvp_waiting=session.get('pvp_waiting', False),
        started=state['started']
    )


# 重置遊戲
@app.route('/reset')
def reset():
    """重置遊戲狀態並重定向到遊戲頁面"""
    session.pop('game_state', None)
    return redirect(url_for('game'))


# 登出
@app.route('/logout')
def logout():
    """清除 session 並重定向到登入頁面"""
    session.clear()
    return redirect(url_for('login'))


# ============================================================
# 應用啟動
# ============================================================

if __name__ == '__main__':
    # 啟動應用
    # host='0.0.0.0' 允許外部訪問
    # debug=True 僅用於開發環境
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)

