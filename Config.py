import os
from dotenv import load_dotenv

# 載入 .env 設定
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'SINBON') 
    HOST = os.getenv('HOST', '0.0.0.0') # 允許外部訪問
    FLASK_RUN_PORT = int(os.getenv('FLASK_RUN_PORT', 5000)) # 預設端口
    DEBUG = os.getenv('DEBUG', 'True').lower() in ('true', '1', 'yes') # 僅用於開發環境
