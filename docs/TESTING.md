# 測試指南

本文檔說明如何執行 tic-tac-toe 專案的各項測試。

## 單元測試

**執行單元測試**:

```bash
# 執行所有測試
python -m unittest

# 執行特定測試檔案
python -m unittest tests/test_game.py

# 顯示詳細輸出
python -m unittest -v
```

## 覆蓋率測試

**執行覆蓋率測試**:

```bash
# 執行 coverage 測試
coverage run -m unittest

# 列出 coverage 報告
coverage report -m
```

**覆蓋率測試與報告結果**:

```
....................................................................................................................................................
----------------------------------------------------------------------
Ran 148 tests in 0.231s

OK
```

```
Name             Stmts   Miss  Cover   Missing
----------------------------------------------
ChatEvents.py       14      0   100%
Config.py            8      0   100%
Game.py             50      0   100%
GameEvents.py      122      0   100%
RoomManager.py     161      0   100%
WebApp.py           55      0   100%
----------------------------------------------
TOTAL              410      0   100%
```


## 測試覆蓋範圍

### 已測試功能

#### Game.py
- ✅ 遊戲初始化（3x3 棋盤，X 先手）
- ✅ 棋盤重置
- ✅ 遊戲開始/結束狀態
- ✅ 座標移動驗證（row, col 格式）
- ✅ 所有勝利條件：
  - 橫向連線（3種）
  - 縱向連線（3種）
  - 對角線連線（2種）
- ✅ 平局判定
- ✅ 回合切換（X ↔ O）
- ✅ 邊界條件處理

#### RoomManager.py
- ✅ 房間創建/加入/離開/刪除
- ✅ 玩家與房間映射
- ✅ 房間狀態查詢（等待/進行中/活躍遊戲數）
- ✅ 房間重置、回合結束、比賽結束條件
- ✅ 玩家座位與符號隨機分配
- ✅ 例外與邊界條件（不存在房間、滿員、重複加入等）

#### GameEvents.py
- ✅ Socket.IO 事件註冊與處理
- ✅ PVP 配對與房間分配
- ✅ 行動事件（make_move, reset_game, start_new_match）
- ✅ 勝利線判斷與 round_end 廣播
- ✅ 斷線處理
- ✅ 所有錯誤分支與異常情境

#### WebApp.py
- ✅ Flask 路由註冊
- ✅ 首頁、登入、遊戲頁面渲染
- ✅ Session 管理
- ✅ 靜態檔案與模板載入
- ✅ 應用啟動流程（run, StartWebApp）
- ✅ 例外與重導處理（未登入、登出、reset）

#### Config.py
- ✅ 設定參數載入與覆蓋
- ✅ 預設值與例外處理

#### ChatEvents.py
- ✅ 聊天訊息事件處理
- ✅ 系統訊息廣播


### 測試檔案所在位置

```
tests/
├── test_game.py           # Game.py 遊戲邏輯測試
├── test_room_manager.py   # RoomManager.py 與房間/玩家管理
├── test_game_events.py    # GameEvents.py SocketIO 事件與整合
├── test_webapp.py         # WebApp.py 路由與 session 測試
├── test_config.py         # Config.py 設定檔測試
├── test_chat_events.py    # ChatEvents.py 聊天事件測試
```

### 目前使用 `# pragma: no cover` 標記忽略覆蓋率的區塊

專案中部分無法自動測試或不屬於邏輯核心的程式碼，會加上 `# pragma: no cover` 來讓 coverage 工具忽略這些區塊。

```python
# 井字遊戲邏輯測試區塊
if __name__ == '__main__':  # pragma: no cover
    """測試井字遊戲邏輯"""

# Flask 應用啟動區塊
if __name__ == '__main__':  # pragma: no cover
    StartWebApp()
```

上述區塊通常不影響邏輯正確性，且難以自動測試，因此建議加註 pragma: no cover。


## 手動測試

### 完整遊戲流程測試

1. **啟動應用**:

   ```bash
   cd app
   python WebApp.py
   ```

2. **測試登入**:

   - 訪問 http://localhost:5000/login
   - 輸入用戶名
   - 選擇圖示
   - 驗證登入成功

3. **測試 PVP 遊戲**:

   - 開啟兩個瀏覽器視窗
   - 分別登入不同用戶
   - 驗證自動配對
   - 測試完整的 5 戰 3 勝流程
   - 驗證座位和符號隨機分配
   - 確認先手輪替機制

4. **測試聊天室**:

   - 在聊天室發送訊息
   - 驗證雙方都能看到訊息
   - 確認時間戳記正確

5. **測試斷線重連**:
   - 關閉一個玩家的瀏覽器
   - 驗證另一個玩家收到離開通知
   - 確認自動重新配對

## 持續整合

如要設置 CI/CD，可使用以下配置：

**GitHub Actions 範例** (`.github/workflows/test.yml`):

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v2

      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: "3.9"

      - name: Install dependencies
        run: |
          pip install -r requirements.txt

      - name: Run coverage tests
        run: |
          cd app/tests
          coverage run -m unittest
          coverage report -m
```