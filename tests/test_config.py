"""
test_config.py - Config 設定單元測試
"""
import unittest
import os
import sys
from unittest import mock
from importlib import reload
import Config as config_module

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

class TestConfig(unittest.TestCase):
    def test_default_values(self):
        with mock.patch('dotenv.load_dotenv'), \
             mock.patch('os.getenv', side_effect=lambda key, default=None: default):

            reload(config_module)
            self.assertEqual(config_module.Config.SECRET_KEY, 'SINBON')
            self.assertEqual(config_module.Config.HOST, '0.0.0.0')
            self.assertEqual(config_module.Config.FLASK_RUN_PORT, 5000)
            self.assertTrue(config_module.Config.DEBUG)

    def test_env_values(self):
        env_values = {
            'SECRET_KEY': 'TESTKEY',
            'HOST': '127.0.0.1',
            'FLASK_RUN_PORT': '8888',
            'DEBUG': 'False',
        }
        
        def mock_getenv(key, default=None):
            return env_values.get(key, default)
        
        with mock.patch('dotenv.load_dotenv'), \
            mock.patch('os.getenv', side_effect=mock_getenv):

            reload(config_module)
            self.assertEqual(config_module.Config.SECRET_KEY, 'TESTKEY')
            self.assertEqual(config_module.Config.HOST, '127.0.0.1')
            self.assertEqual(config_module.Config.FLASK_RUN_PORT, int('8888'))
            self.assertEqual(config_module.Config.DEBUG, False)

if __name__ == '__main__':
    unittest.main()
