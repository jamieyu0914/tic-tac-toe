"""
test_webapp.py - WebApp 路由與初始化單元測試
"""
import unittest
from flask import session
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from WebApp import WebApp
from Config import Config

class TestWebApp(unittest.TestCase):
    def setUp(self):
        self.webapp = WebApp()
        self.app = self.webapp.App
        self.client = self.app.test_client()
        self.app.config['TESTING'] = True

    def test_webapp_initialization(self):
        """測試 WebApp 初始化"""
        self.assertIsNotNone(self.webapp.App)
        self.assertIsNotNone(self.webapp.SocketIO)
        # 檢查secret_key是否設定（不需要精確值）
        self.assertIsNotNone(self.webapp.App.secret_key)
        self.assertNotEqual(self.webapp.App.secret_key, '')

    def test_login_get(self):
        # GET 請求登入頁
        resp = self.client.get('/login')
        self.assertEqual(resp.status_code, 200)
        self.assertIn(b'icons', resp.data)

    def test_login_post_success(self):
        # POST 正確登入
        resp = self.client.post('/login', data={'username': 'testuser', 'icon': '😺'}, follow_redirects=True)
        # 檢查是否成功登入並重定向到遊戲頁面
        self.assertEqual(resp.status_code, 200)

    def test_login_post_fail(self):
        # POST 缺少資料
        resp = self.client.post('/login', data={'username': '', 'icon': ''})
        self.assertIn('請輸入使用者名稱'.encode('utf-8'), resp.data)

    def test_login_post_no_icon(self):
        """測試只有用戶名沒有圖標的登入"""
        resp = self.client.post('/login', data={'username': 'testuser', 'icon': ''})
        # 檢查是否包含錯誤消息（使用更寬鬆的檢查）
        self.assertIn('選擇'.encode('utf-8'), resp.data)

    def test_login_post_no_username(self):
        """測試只有圖標沒有用戶名的登入"""
        resp = self.client.post('/login', data={'username': '', 'icon': '😺'})
        self.assertIn('請輸入使用者名稱'.encode('utf-8'), resp.data)

    def test_home_redirect(self):
        # 未登入時訪問首頁應重定向
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/login', resp.headers['Location'])

    def test_home_with_session(self):
        """測試已登入用戶訪問首頁"""
        with self.client.session_transaction() as sess:
            sess['user'] = 'testuser'
            sess['icon'] = '😺'
        
        resp = self.client.get('/')
        self.assertEqual(resp.status_code, 200)
        # 檢查是否包含遊戲相關內容
        self.assertIn(b'Tic-Tac-Toe', resp.data)

    def test_home_post_with_session(self):
        """測試已登入用戶的POST請求"""
        with self.client.session_transaction() as sess:
            sess['user'] = 'testuser'
            sess['icon'] = '😺'
        
        resp = self.client.post('/', data={'username': 'newuser', 'icon': '🐱'}, follow_redirects=True)
        self.assertEqual(resp.status_code, 200)

    def test_home_with_login(self):
        # 登入後可正常訪問 /
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = 'testuser'
            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)
            # 檢查頁面有 testuser 名稱
            self.assertIn(b'testuser', resp.data)
            # 檢查首頁有遊戲區塊
            self.assertIn(b'game-area', resp.data)

    def test_logout(self):
        with self.app.test_client() as c:
            with c.session_transaction() as sess:
                sess['user'] = 'testuser'
            resp = c.get('/logout', follow_redirects=True)
            # 檢查是否重定向到登入頁面
            self.assertIn('登入 - Tic-Tac-Toe'.encode('utf-8'), resp.data)

    def test_logout_clears_session(self):
        # /logout 會清除 session 並重導到 /login
        with self.client as c:
            with c.session_transaction() as sess:
                sess['user'] = 'testuser'
            resp = c.get('/logout')
            self.assertEqual(resp.status_code, 302)
            self.assertIn('/login', resp.headers['Location'])
            with c.session_transaction() as sess:
                self.assertNotIn('user', sess)

    def test_reset_route(self):
        """測試重置路由"""
        resp = self.client.get('/reset', follow_redirects=True)
        self.assertEqual(resp.status_code, 200)
        # 應該重定向到登入頁面
        self.assertIn('登入 - Tic-Tac-Toe'.encode('utf-8'), resp.data)

    def test_reset_redirects(self):
        # /reset 會重導到 /
        resp = self.client.get('/reset')
        self.assertEqual(resp.status_code, 302)
        self.assertIn('/', resp.headers['Location'])

    def test_run_method(self):
        """測試 run 方法"""
        # 檢查 run 方法是否存在
        self.assertTrue(hasattr(self.webapp, 'run'))
        self.assertTrue(callable(getattr(self.webapp, 'run')))

    def test_run_invokes_socketio_run(self):
        # 測試 run() 會呼叫 SocketIO.run 並傳入正確參數
        self.webapp = WebApp()
        called = {}
        def fake_run(app, host, port, debug):
            called['app'] = app
            called['host'] = host
            called['port'] = port
            called['debug'] = debug
        self.webapp.SocketIO.run = fake_run
        self.webapp.run()
        self.assertIs(called['app'], self.webapp.App)
        self.assertEqual(called['host'], Config.HOST)
        self.assertEqual(called['port'], Config.FLASK_RUN_PORT)
        self.assertEqual(called['debug'], Config.DEBUG)

    def test_socketio_initialization(self):
        """測試 SocketIO 初始化"""
        self.assertIsNotNone(self.webapp.SocketIO)
        # 檢查 SocketIO 是否正確配置
        self.assertEqual(self.webapp.SocketIO.async_mode, 'threading')

    def test_routes_registration(self):
        """測試路由是否正確註冊"""
        # 檢查所有路由是否存在
        with self.app.test_request_context():
            rules = [rule.rule for rule in self.app.url_map.iter_rules()]
            self.assertIn('/', rules)
            self.assertIn('/login', rules)
            self.assertIn('/logout', rules)
            self.assertIn('/reset', rules)

    def test_different_icons(self):
        """測試不同圖標的登入"""
        icons = ['😀', '🐶', '🎮', '⭐', '🔥']
        
        for icon in icons:
            with self.subTest(icon=icon):
                resp = self.client.post('/login', data={'username': f'user_{icon}', 'icon': icon}, follow_redirects=True)
                self.assertEqual(resp.status_code, 200)

    def test_session_persistence(self):
        """測試會話持久性"""
        with self.client as c:
            # 登入
            resp = c.post('/login', data={'username': 'testuser', 'icon': '😺'}, follow_redirects=True)
            self.assertEqual(resp.status_code, 200)
            
            # 檢查後續請求是否保持登入狀態
            resp = c.get('/')
            self.assertEqual(resp.status_code, 200)
            self.assertIn(b'testuser', resp.data)

    def test_edge_cases(self):
        """測試邊界情況"""
        # 非常長的用戶名
        long_username = 'a' * 1000
        resp = self.client.post('/login', data={'username': long_username, 'icon': '😺'})
        # 應該能處理長用戶名而不崩潰
        self.assertIn(resp.status_code, [200, 302])
        
        # 特殊字符用戶名
        special_username = '<script>alert("test")</script>'
        resp = self.client.post('/login', data={'username': special_username, 'icon': '😺'})
        self.assertIn(resp.status_code, [200, 302])

    def test_multiple_sessions(self):
        """測試多個會話"""
        # 創建兩個不同的客戶端
        client1 = self.app.test_client()
        client2 = self.app.test_client()
        
        # 分別登入
        with client1.session_transaction() as sess1:
            sess1['user'] = 'user1'
            sess1['icon'] = '😀'
            
        with client2.session_transaction() as sess2:
            sess2['user'] = 'user2'  
            sess2['icon'] = '😎'
        
        # 檢查兩個會話是否獨立
        resp1 = client1.get('/')
        resp2 = client2.get('/')
        
        self.assertEqual(resp1.status_code, 200)
        self.assertEqual(resp2.status_code, 200)
        self.assertIn(b'user1', resp1.data)
        self.assertIn(b'user2', resp2.data)


class TestWebAppMainExecution(unittest.TestCase):
    """測試 WebApp.py 的主執行部分和 run 方法"""
    
    def test_start_webapp_function_exists(self):
        """測試 StartWebApp 函數存在且可以呼叫"""
        from WebApp import StartWebApp
        # 只測試函數是否存在，不實際運行
        self.assertTrue(callable(StartWebApp))
    
    def test_webapp_run_method_exists(self):
        """測試 WebApp.run 方法存在"""
        webapp = WebApp()
        self.assertTrue(hasattr(webapp, 'run'))
        self.assertTrue(callable(webapp.run))
    
    def test_main_execution_scenario(self):
        """測試主執行場景，確保 __main__ 代碼塊可以被導入"""
        import subprocess
        import sys
        
        # 使用 --help 參數來測試 WebApp.py 是否能正常導入和執行
        # 這樣不會實際啟動 server
        result = subprocess.run(
            [sys.executable, '-c', 'import sys; sys.path.insert(0, "."); import WebApp; print("WebApp imported successfully")'],
            cwd=os.path.join(os.path.dirname(__file__), '..'),
            capture_output=True,
            text=True,
            timeout=10
        )
        
        # 檢查是否成功導入
        self.assertEqual(result.returncode, 0, f"WebApp import failed: {result.stderr}")
        self.assertIn("imported successfully", result.stdout)
    
    def test_startwebapp_calls_run(self):
        # 測試 StartWebApp 會建立 WebApp 並呼叫 run
        import WebApp as webapp_mod
        called = {'run': False}
        class DummyWebApp:
            def run(self):
                called['run'] = True
        orig_webapp = webapp_mod.WebApp
        webapp_mod.WebApp = DummyWebApp
        try:
            webapp_mod.StartWebApp()
            self.assertTrue(called['run'])
        finally:
            webapp_mod.WebApp = orig_webapp


if __name__ == '__main__':
    unittest.main()
