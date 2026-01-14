import os
from dotenv import load_dotenv

# 載入 .env 設定
load_dotenv()

class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'SINBON') 
    HOST = os.getenv('HOST', '0.0.0.0') # 允許外部訪問
    PORT = int(os.getenv('PORT', 5000)) # 預設端口
    DEBUG = os.getenv('DEBUG', 'True') # 僅用於開發環境
