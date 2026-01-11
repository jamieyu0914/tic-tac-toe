# Tic-Tac-Toe 井字遊戲
⭕❌⭕❌ 經典井字遊戲，使用 Flask 實作，支援單機與多人對戰。

## 專案簡介
本專案以 Flask 結合 Socket.IO 實作井字棋遊戲，提供網頁介面，支援單人（對電腦 AI）與雙人（PVP）模式，並內建聊天室功能，用於練習與學習相關技術。

## 功能說明
- 支援單人模式（AI 難度可選：簡單、普通、困難）
- 支援雙人即時對戰（PVP）
- 遊戲狀態即時同步
- 內建聊天室
- 多主題切換（聖誕、新年等）

## 技術架構
- 前端：HTML + Flask 模板 + Socket.IO（JavaScript 即時互動）
- 後端：Flask + Flask-SocketIO + Flask-CORS
- AI：Minimax 演算法

## 建立虛擬環境
1. 建立：`python3 -m venv venv` 或 `python -m venv venv`
2. 啟用：`source venv/bin/activate`

## 安裝模組
1. 執行：`pip install flask`
2. 執行：`pip install flask_socketio`
3. 執行：`pip install flask_cors`

## 啟動應用程式
1. 在終端機啟用 venv 後，移動至 `cd app/`
2. 執行：`python app.py`
3. 或用 Flask 指令：`flask --app app run` 或 `flask run`

## 查看路由
1. 執行：`flask --app app routes`

## 檢查程式是否運行中
1. 執行：`sudo lsof -i :5000`

## 關閉程式
1. 執行：`sudo kill {PID}`

## Todo（待完成項目）
1. 決定起手玩家（可選擇 X 或 O 先手）
2. 新增電腦聊天室（讓單人模式也能與 AI 聊天）
3. 個別聊天室（每個房間獨立聊天頻道）
4. 增加遊戲結束後統計（勝率、對戰紀錄）
5. 前端介面美化（主題切換、響應式設計）
6. 增加遊戲提示（如勝負判斷動畫、提示訊息）
