# 井字棋遊戲更新說明

## 更新日期
2026年1月13日

## 更新內容

### 1. 房間人數限制 ✅
- **功能**: 限制每個房間最多只能有2名玩家進入
- **實現**:
  - 在 `GameEvents.py` 的 `handle_join_pvp()` 中添加房間人數檢查
  - 當房間已滿時，向玩家發送 `room_full` 事件
  - 前端顯示 "房間已滿，請稍後再試" 的提示訊息
- **修改文件**: `game_events.py`, `index.html`

### 2. 5戰3勝制度 ✅
- **功能**: 玩家對戰改為5戰3勝制，特殊規則：2比2時第5戰平手則比賽結束為平局
- **實現**:
  - 在 `RoomManager.py` 的 `GameRoom` 類中添加:
    - `scores`: 記錄左右玩家和平手的分數
    - `round_count`: 當前回合數
    - `match_finished`: 比賽是否結束標記
  - `check_round_end()`: 在每回合結束時更新戰績
  - `reset()`: 重置方法中檢查5戰3勝條件和2比2平手情況
- **修改文件**: `RoomManager.py`, `GameEvents.py`, `index.html`

### 3. 隨機配置座位和符號 ✅
- **功能**: 開場時隨機配置玩家座位(左/右)和符號(O/X)
- **實現**:
  - 在 `RoomManager.py` 添加 `_assign_seats_and_symbols()` 方法
  - 使用 `random.sample()` 隨機分配座位和符號
  - 在第二名玩家加入時調用此方法
- **修改文件**: `RoomManager.py`, `GameEvents.py`

### 4. 輪替先手機制 ✅
- **功能**: 開場左玩家先手，下一回合輪替先手權
- **實現**:
  - 添加 `current_first_player` 屬性追蹤當前先手玩家
  - 第一回合固定左玩家先手
  - 在 `reset()` 方法中實現先手輪替邏輯
  - 根據先手玩家的符號設定 `game.turn`
- **修改文件**: `RoomManager.py`

### 5. 座標方式傳遞位置 ✅
- **功能**: Protocol改用座標方式(row, col)而非0-8的數字
- **實現**:
  - 修改 `make_move()` 方法接受 `row` 和 `col` 參數
  - 內部轉換: `position = row * 3 + col`
  - Socket.IO 事件使用 `{'row': 行座標, 'col': 列座標}` 格式
  - 前端計算座標: `row = Math.floor(cellIndex / 3)`, `col = cellIndex % 3`
- **修改文件**: `RoomManager.py`, `GameEvents.py`, `index.html`

### 6. 優化通訊協議 ✅
- **功能**: 每次溝通只傳送必要資訊，不再傳送大包資料
- **實現**:
  - `move_made` 事件: 只傳送 `{row, col, symbol, turn}`
  - `round_end` 事件: 只傳送 `{winner, scores, round_count, match_finished, winning_lines}`
  - `game_reset` 事件: 只傳送 `{turn, scores, round_count, match_finished, current_first_player}`
  - `game_start` 事件: 只傳送 `{room_id, your_symbol, turn, left_player, right_player, my_side, scores, round_count}`
  - 前端維護本地 `board` 狀態，只在需要時更新
- **修改文件**: `GameEvents.py`, `index.html`

### 7. 連線線條顯示 ✅
- **功能**: 相同符號連線時，即時畫出連線線條(支持最多兩條連線)
- **實現**:
  - 添加 `get_winning_lines()` 函數計算所有獲勝連線
  - 返回座標格式的連線: `[[[row, col], [row, col], [row, col]], ...]`
  - 前端 `drawWinningLines()` 使用 Canvas API 繪製紅色線條
  - 支持同時繪製多條連線（理論上可達2條）
  - `clearWinningLines()` 清除線條準備下一回合
- **修改文件**: `GameEvents.py`, `index.html`

### 8. 戰績統計顯示 ✅
- **功能**: 顯示統計戰績(左玩家、平手、右玩家的勝場數)
- **實現**:
  - 在 UI 中顯示：`左玩家 (符號) 名稱：X勝｜平手：Y｜右玩家 (符號) 名稱：Z勝`
  - 顯示當前回合數：`回合制：5戰3勝｜目前回合：X/5`
  - `updateScoreDisplay()` 和 `updatePlayersDisplay()` 實時更新戰績
  - 比賽結束時顯示最終結果
- **修改文件**: `RoomManager.py`, `index.html`

## 技術細節

### 數據結構變更

#### GameRoom 類新增屬性:
```python
self.scores = {'left': 0, 'right': 0, 'draw': 0}  # 戰績統計
self.round_count = 0  # 當前回合數
self.match_finished = False  # 比賽是否結束
self.current_first_player = 'left'  # 當前先手玩家
self.left_player = None  # 左側玩家
self.right_player = None  # 右側玩家
```

### Socket.IO 事件更新

#### 新增事件:
- `room_full`: 房間已滿通知
- `move_made`: 移動完成（輕量級）
- `round_end`: 回合結束（包含連線資訊）
- `game_reset`: 遊戲重置（下一回合）

#### 移除/替換事件:
- `game_update` → 拆分為 `move_made` 和 `round_end`

### 連線檢測算法

使用座標格式定義所有可能的連線:
```python
win_conditions = [
    [[0, 0], [0, 1], [0, 2]],  # 第一行
    [[1, 0], [1, 1], [1, 2]],  # 第二行
    [[2, 0], [2, 1], [2, 2]],  # 第三行
    [[0, 0], [1, 0], [2, 0]],  # 第一列
    [[0, 1], [1, 1], [2, 1]],  # 第二列
    [[0, 2], [1, 2], [2, 2]],  # 第三列
    [[0, 0], [1, 1], [2, 2]],  # 主對角線
    [[0, 2], [1, 1], [2, 0]]   # 副對角線
]
```

### Canvas 繪製線條

使用 HTML5 Canvas API 繪製獲勝連線:
```javascript
ctx.strokeStyle = '#FF5722';  // 紅色
ctx.lineWidth = 5;
ctx.lineCap = 'round';
ctx.beginPath();
ctx.moveTo(startX, startY);
ctx.lineTo(endX, endY);
ctx.stroke();
```

## 測試建議

1. **房間限制測試**: 嘗試讓第三個玩家加入已有2人的房間
2. **5戰3勝測試**: 進行完整的5局遊戲，測試各種勝負組合
3. **2比2平手測試**: 特意製造2比2的情況，第5局平手
4. **座標系統測試**: 點擊各個位置，驗證座標傳遞正確
5. **連線顯示測試**: 測試水平、垂直、對角線的連線顯示
6. **先手輪替測試**: 觀察每回合的先手是否正確輪替
7. **戰績顯示測試**: 確認戰績統計正確更新

## 注意事項

- 所有修改都保持向後兼容
- 前端保持本地狀態以減少網絡傳輸
- 使用座標系統讓代碼更直觀易懂
- Canvas 線條會在下一回合自動清除
- 比賽結束後需要重新配對才能開始新比賽

## 未來改進建議

1. 添加動畫效果使連線繪製更流暢
2. 添加音效提示
3. 保存歷史戰績到數據庫
4. 添加重播功能
5. 支持觀戰模式
