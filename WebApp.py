"""
app.py - Flask 應用主程式（類別化版本）
負責路由管理和 HTTP 請求處理
"""

from flask import Flask, render_template, request, redirect, url_for, session
from flask_socketio import SocketIO
from flask_cors import CORS
import random

from Environment import Config
from ChatEvents import register_chat_events
from GameEvents import register_game_events
from Game import Game


class WebApp:
    """
    Web 應用類別
    管理 Flask 應用、Socket.IO 和所有路由
    """
    
    def __init__(self):
        """初始化 Web 應用"""
        # 創建 Flask 應用
        self.App = Flask(__name__)
        CORS(self.App)
        self.App.secret_key = Config.SECRET_KEY
        
        # 創建 Socket.IO 實例
        self.SocketIO = SocketIO(
            self.App, 
            async_mode='threading', 
            cors_allowed_origins="*"
        )
        
        # 註冊路由
        self.App.route('/login', methods=['GET', 'POST'])(self.login)
        self.App.route('/', methods=['GET', 'POST'])(self.home)
        self.App.route('/reset')(self.reset)
        self.App.route('/logout')(self.logout)
        
        # 註冊 Socket.IO 事件
        register_chat_events(self.SocketIO)
        register_game_events(self.SocketIO)
    
    # ============================================================
    # 輔助函數
    # ============================================================
    
    def get_or_create_game(self) -> Game:
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
    
    def save_game(self, game: Game):
        """
        將遊戲狀態保存到 session
        
        Args:
            game: 遊戲實例
        """
        session['game_state'] = game.get_state()
    
    # ============================================================
    # 路由處理函數
    # ============================================================
    
    def login(self):
        """
        登入頁面處理
        - GET: 顯示登入表單（隨機顯示 5 個圖示）
        - POST: 驗證登入資訊並創建 session
        """
        # 如果已登入，重定向到首頁
        if 'user' in session:
            return redirect(url_for('home'))
        
        error = None
        ICON_POOL = [
            '😺', '🐶', '🐼', '🚀', '🎃', 
            '🐧', '🐵', '🐸', '🦊', '🐢', 
            '🐟', '🐯', '🦁', '🐷', '🦄'
        ]
        
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
    
    def home(self):
        """
        首頁處理
        - GET: 顯示遊戲界面
        - POST: 處理遊戲操作（開始遊戲）
        """
        if 'user' not in session:
            return redirect(url_for('login'))
        
        # 獲取或創建遊戲實例
        game_instance = self.get_or_create_game()
        
        if request.method == 'POST':
            action = request.form.get('action')
            
            # 開始遊戲
            if action == 'start_game':
                game_instance.start()
                self.save_game(game_instance)
                return redirect(url_for('home'))
        
        # 準備模板數據
        state = game_instance.get_state()
        
        return render_template(
            'index.html',
            board=state['board'],
            turn=state['turn'],
            winner=state['winner'],
            username=session.get('user', '玩家'),
            started=state['started'],
        )
    
    def reset(self):
        """重置遊戲狀態並重定向到遊戲頁面"""
        # 清除遊戲狀態
        session.pop('game_state', None)
        return redirect(url_for('home'))
    
    def logout(self):
        """清除 session 並重定向到登入頁面"""
        session.clear()
        return redirect(url_for('login'))
    
    # ============================================================
    # 應用運行
    # ============================================================
    
    def run(self):
        """啟動 Web 應用"""
        self.SocketIO.run(
            self.App, 
            host=Config.HOST, 
            port=Config.FLASK_RUN_PORT, 
            debug=Config.DEBUG
        )


def StartWebApp():
    """啟動 Web 應用（主線程模式）"""
    webapp = WebApp()
    webapp.run()


if __name__ == '__main__':
    StartWebApp()

# ============================================================
# 供 flask run 指令執行
# 運行在指定的 SERVER_PORT
# ============================================================
# app = WebApp().App
# app.config['SERVER_PORT'] = Config.FLASK_RUN_PORT
