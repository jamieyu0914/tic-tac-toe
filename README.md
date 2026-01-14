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
1. 使用 `pip install -r requirements.txt` 一次安裝所有依賴

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

## Todo1（待完成項目）
1. 決定起手玩家（可選擇 X 或 O 先手）
2. 新增電腦聊天室（讓單人模式也能與 AI 聊天）
3. 個別聊天室（每個房間獨立聊天頻道）
4. 增加遊戲結束後統計（勝率、對戰紀錄）
5. 前端介面美化（主題切換、響應式設計）
6. 增加遊戲提示（如勝負判斷動畫、提示訊息）

## Todo2（待完成項目）
1. 回合制：5戰3勝（Option: 3,5,～12）
2. 統計戰績（左玩家：1 平手：2 右玩家：2）
3. 開場隨機配置玩家座位（左/右邊）和符號（O/X）
4. 開場左玩家先手，下一回合輪替
5. Protocol 以座標方式交換（井字棋盤座標）
6. UI 相同符號連線時，需要即時畫出連線線條
7. game.py 類別規畫，不夠完善
8. 沒有定義前、後端溝通的 protocol，日後難維護
9. game.py 沒有驗證自我功能的正確性，除錯困難
10. game 有 WIN_CONDITIONS，卻沒有提供哪幾條線連線（狀態）
11. 從 app 到 game 的流程太迂迴（包太多層相同介面），效率不佳
12. 每次都把 board 全部的資都往 view 丟（資料過度複雜）
13. 少考慮 2 條連線情況
14. app 沒有類別化
15. AIPlayer 與一般玩家沒有制定相同的介面與功能
16. 登入有 bug: 選定圖示，按登入報錯「無此圖示」