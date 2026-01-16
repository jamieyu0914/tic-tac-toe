# 測試指南

本文檔說明如何執行 tic-tac-toe 專案的各項測試。

## 單元測試

### Game.py 功能測試

測試 Game.py 的所有核心功能，包括：

- 初始化和重置
- 遊戲開始
- 移動驗證（座標方式）
- 勝負判定（所有可能的連線）
- 平局判定
- 狀態管理
- 邊界條件

**執行測試**:

```bash
# 執行所有測試
python -m unittest discover tests

# 執行特定測試檔案
python -m unittest tests.test_game

# 顯示詳細輸出
python -m unittest tests.test_game -v
```

**測試結果範例**:

```
Ran 25 tests in 0.005s
OK

======================================================================
測試摘要
======================================================================
總測試數: 25
成功: 25
失敗: 0
錯誤: 0
======================================================================
```

## 測試覆蓋範圍

### 已測試功能

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

### 測試檔案位置

```
tests/
└── test_game.py    # Game.py 的 25 個單元測試
```
python test_structure.py
```

**測試內容**:

- 檢查 WebApp 類別是否存在
- 驗證所有必要方法是否實現
- 確認模組級別函數存在

## 測試覆蓋率

### Game.py 測試覆蓋

| 功能模塊     | 測試數量 | 狀態  |
| ------------ | -------- | ----- |
| 初始化測試   | 2        | ✓     |
| 遊戲開始測試 | 1        | ✓     |
| 移動測試     | 5        | ✓     |
| 勝負判定測試 | 10       | ✓     |
| 邊界條件測試 | 7        | ✓     |
| **總計**     | **25**   | **✓** |

### 測試的勝利條件

測試涵蓋所有可能的獲勝方式：

- ✓ 橫向獲勝（3 種：第一、二、三行）
- ✓ 縱向獲勝（3 種：第一、二、三列）
- ✓ 對角線獲勝（2 種：主對角線、副對角線）
- ✓ 平局情況
- ✓ X 和 O 都能獲勝

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

## 持續整合建議

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

      - name: Run Game tests
        run: |
          cd app/tests
          python test_game.py

      - name: Verify structure
        run: |
          cd app
          python test_structure.py
```

## 測試最佳實踐

1. **每次修改後都執行測試** - 確保沒有破壞現有功能
2. **添加新功能時增加測試** - 維持測試覆蓋率
3. **修復 bug 時先寫測試** - 確保 bug 不會再次出現
4. **定期檢查測試是否過時** - 隨著需求變化更新測試

## 已知限制

目前的測試涵蓋 Game.py 的核心邏輯，但以下部分尚未完全測試：

- RoomManager.py 的房間管理邏輯
- Socket.IO 事件處理
- Session 管理
- 前端 JavaScript 邏輯

建議未來添加這些部分的測試以提高整體測試覆蓋率。
