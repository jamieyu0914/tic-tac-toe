"""
app.py - Flask 應用主程式
負責路由管理和 HTTP 請求處理
"""

from flask import Flask, render_template, request, redirect, url_for, session
import random
from flask_socketio import SocketIO
from flask_cors import CORS

from chat_events import register_chat_events
from game_events import register_game_events
from Game import Game
from AIPlayer import AIPlayer

# 創建 Flask 應用實例
app = Flask(__name__)
CORS(app)
app.secret_key = 'SINBON'

# 創建 Socket.IO 實例
# - async_mode='threading': 使用多線程異步模式
# - cors_allowed_origins="*": 允許所有來源跨域連接（生產環境應改為具體域名） '*' -> 允許所有來源跨域連接
socketio = SocketIO(app, async_mode='threading', cors_allowed_origins="*")

# 註冊事件處理
register_chat_events(socketio)  # 聊天室事件
register_game_events(socketio)  # 遊戲邏輯事件


# ============================================================
# 輔助函數
# ============================================================

# For 單機/電腦模式遊戲狀態使用
def get_or_create_game() -> Game: 
    """
    從 session 獲取或創建遊戲實例
    
    Returns:
        Game: 遊戲實例
    """
    # 若 session 中無遊戲狀態，創建新遊戲；有則載入現有狀態
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
    ICON_POOL = ['😺','🐶','🐼','🚀','🎃','🐧','🐵','🐸','🦊','🐢','🐟','🐯','🦁','🐷','🦄']
    
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        icon = request.form.get('icon')
        shown_icons = session.get('login_icons', [])
        
        # 驗證輸入
        if not username:
            error = '請輸入使用者名稱'
        elif len(username) > 10:
            error = '使用者名稱不可超過 10 個字元'
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
        
        # 驗證失敗，使用已保存的圖示
        icons = shown_icons
    else:
        # GET 請求：生成新的隨機圖示
        icons = random.sample(ICON_POOL, 5)
        session['login_icons'] = icons
    
    return render_template('login.html', error=error, icons=icons)


# 首頁 / 遊戲主頁（需要登入）
@app.route('/', methods=['GET', 'POST'])
def home():
    """
    首頁處理
    - GET: 顯示遊戲界面
    - POST: 處理遊戲操作（模式設置、開始遊戲）
    """
    if 'user' not in session:
        return redirect(url_for('login'))
    
    # 獲取或創建遊戲實例
    game_instance = get_or_create_game()
    
    if request.method == 'POST':
        action = request.form.get('action') #從 <form method="post"> 取name值
        
        # 設置遊戲模式
        if action == 'set_mode':
            mode = request.form.get('mode', 'pvp')
            game_instance.set_mode(mode)
            save_game(game_instance)
        
        # 開始遊戲
        elif action == 'start_game':
            game_instance.start()
            save_game(game_instance)
            
            return redirect(url_for('home'))
    
    # 準備模板數據
    state = game_instance.get_state()
    
    # 難度中文名稱
    difficulty_names = {
        'simple': '簡單',
        'normal': '普通',
        'hard': '困難'
    }
    
    return render_template(
        'game.html',
        board=state['board'], # 棋盤狀態
        turn=state['turn'], # 輪到誰?
        winner=state['winner'], # 贏家 
        mode=state['mode'], # pvp
        username=session.get('user', '玩家'),
        started=state['started']
    )

# 重置遊戲
@app.route('/reset')
def reset():
    """重置遊戲狀態但保留模式設定，並重定向到遊戲頁面"""
    if 'game_state' in session:
        # 保留當前模式和難度設定
        current_state = session['game_state']
        mode = current_state.get('mode', 'pvp')
        
        # 創建新遊戲但保留設定
        game = Game()
        game.set_mode(mode)
        game.start()
        save_game(game)
    else:
        session.pop('game_state', None)
    
    return redirect(url_for('home'))


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

