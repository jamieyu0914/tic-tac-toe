"""
test_chat_events.py - ChatEvents 單元測試 (SocketIO 事件模擬)
"""

import unittest
from unittest.mock import MagicMock, patch
from flask import Flask, session
from flask_socketio import SocketIO
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from ChatEvents import register_chat_events

class TestChatEvents(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.secret_key = 'test'
        self.socketio = SocketIO(self.app, async_mode='threading')
        register_chat_events(self.socketio)
        self.client = self.socketio.test_client(self.app)

    def test_chat_message_broadcast(self):
        # 模擬 session
        with self.app.test_request_context('/'):
            session['user'] = '測試玩家'
            # 發送 chat message 事件
            self.client.emit('chat message', {'message': '哈囉', 'time': '12:00:00'})
            received = self.client.get_received()
            found = any(e['name'] == 'chat message' and e['args'][0]['message'] == '哈囉' for e in received)
            self.assertTrue(found)

    def test_chat_message_default_username(self):
        # 不設 session，測試預設名稱
        with self.app.test_request_context('/'):
            self.client.emit('chat message', {'message': 'hi'})
            received = self.client.get_received()
            found = any(e['name'] == 'chat message' and e['args'][0]['username'] in ['隱藏玩家', None] for e in received)
            self.assertTrue(found)

    def test_chat_message_string_input(self):
        """測試字符串輸入的聊天消息"""
        with self.app.test_request_context('/'):
            session['user'] = '測試玩家'
            # 發送字符串格式的 chat message
            self.client.emit('chat message', 'Hello World')
            received = self.client.get_received()
            found = any(e['name'] == 'chat message' and e['args'][0]['message'] == 'Hello World' for e in received)
            self.assertTrue(found)

    def test_chat_message_with_username_in_msg(self):
        """測試消息中包含用戶名的情況"""
        with self.app.test_request_context('/'):
            # session 中沒有 user，但消息中有 username
            self.client.emit('chat message', {'message': 'test message', 'username': '消息中的用戶'})
            received = self.client.get_received()
            found = any(e['name'] == 'chat message' and e['args'][0]['username'] == '消息中的用戶' for e in received)
            self.assertTrue(found)

    def test_chat_message_no_time_provided(self):
        """測試未提供時間的聊天消息"""
        with self.app.test_request_context('/'):
            session['user'] = '測試玩家'
            self.client.emit('chat message', {'message': 'no time message'})
            received = self.client.get_received()
            
            # 檢查是否有 time 字段且格式正確
            found = False
            for event in received:
                if event['name'] == 'chat message' and event['args'][0]['message'] == 'no time message':
                    time_str = event['args'][0]['time']
                    # 簡單檢查時間格式 HH:MM:SS
                    if len(time_str.split(':')) == 3:
                        found = True
                        break
            self.assertTrue(found)

    def test_chat_message_empty_message(self):
        """測試空消息"""
        with self.app.test_request_context('/'):
            session['user'] = '測試玩家'
            self.client.emit('chat message', {'message': ''})
            received = self.client.get_received()
            found = any(e['name'] == 'chat message' and e['args'][0]['message'] == '' for e in received)
            self.assertTrue(found)

    def test_chat_message_fallback_username(self):
        """測試所有用戶名來源都不存在的情況"""
        with self.app.test_request_context('/'):
            # 清理 session，確保沒有 user
            if 'user' in session:
                del session['user']
            # 發送不包含 username 的消息
            self.client.emit('chat message', {'message': 'test'})
            received = self.client.get_received()
            found = any(e['name'] == 'chat message' and e['args'][0]['username'] == '隱藏玩家' for e in received)
            self.assertTrue(found)

    def test_multiple_chat_messages(self):
        """測試多個聊天消息"""
        with self.app.test_request_context('/'):
            session['user'] = '測試玩家'
            
            messages = ['第一條消息', '第二條消息', '第三條消息']
            for i, msg in enumerate(messages):
                self.client.emit('chat message', {'message': msg, 'time': f'12:0{i}:00'})
            
            received = self.client.get_received()
            
            # 檢查是否收到所有消息
            for msg in messages:
                found = any(e['name'] == 'chat message' and e['args'][0]['message'] == msg for e in received)
                self.assertTrue(found)

if __name__ == '__main__':
    unittest.main()
