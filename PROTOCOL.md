# 井字棋遊戲 - 前後端通訊協定 (Protocol)

本文檔定義了前端（JavaScript/Socket.IO）與後端（Flask/Socket.IO）之間的所有通訊協定。

---

## 目錄
- [Socket.IO 連線](#socketio-連線)
- [聊天室事件](#聊天室事件)
- [PVP 遊戲事件](#pvp-遊戲事件)
- [資料結構定義](#資料結構定義)
- [錯誤處理](#錯誤處理)

---

## Socket.IO 連線

### 連線建立
- **事件**: `connect`
- **方向**: Client → Server
- **說明**: 當客戶端建立 WebSocket 連線時自動觸發
- **回應**: 無

### 斷線
- **事件**: `disconnect`
- **方向**: Client → Server
- **說明**: 當客戶端斷開連線時自動觸發
- **處理**: 
  - 移除玩家從所在房間
  - 通知對手玩家離開

---

## 聊天室事件

### 1. 發送聊天訊息

**事件**: `chat message`

**方向**: Client → Server

**請求格式**:
```javascript
socket.emit('chat message', message);
```

**參數**:
- `message` (string): 聊天訊息內容

**範例**:
```javascript
socket.emit('chat message', '大家好！');
```

---

### 2. 接收聊天訊息

**事件**: `chat message`

**方向**: Server → Client (broadcast)

**回應格式**:
```javascript
socket.on('chat message', function(msg) {
    // msg 格式: "[HH:MM:SS] 用戶名: 訊息內容"
});
```

**參數**:
- `msg` (string): 格式化的聊天訊息，包含時間戳記和用戶名

**範例**:
```
"[14:30:25] 玩家1: 大家好！"
"[系統提示] 強勁的棋手 玩家2 已抵達戰場!"
```

---

## PVP 遊戲事件

### 1. 加入 PVP 配對

**事件**: `join_pvp`

**方向**: Client → Server

**請求格式**:
```javascript
socket.emit('join_pvp');
```

**說明**: 
- 自動尋找可用房間或創建新房間
- 如果有房間等待中，則加入該房間並開始遊戲
- 如果無可用房間，則創建新房間並等待對手

**可能的回應事件**:
- `waiting_for_opponent` - 等待對手加入
- `game_start` - 遊戲開始
- `room_full` - 房間已滿
- `game_in_progress` - 已有遊戲進行中

---

### 2. 等待對手

**事件**: `waiting_for_opponent`

**方向**: Server → Client

**回應格式**:
```javascript
socket.on('waiting_for_opponent', function(data) {
    // data.room_id: 房間ID
});
```

**資料結構**:
```javascript
{
    "room_id": "room_abcd1234_5678"
}
```

---

### 3. 遊戲開始

**事件**: `game_start`

**方向**: Server → Client

**回應格式**:
```javascript
socket.on('game_start', function(data) {
    // 遊戲開始，接收初始化資料
});
```

**資料結構**:
```javascript
{
    "room_id": "room_abcd1234_5678",
    "your_symbol": "X",              // 玩家的符號 ('X' 或 'O')
    "turn": "X",                     // 當前回合的符號
    "left_player": {                 // 左側玩家資訊
        "sid": "socket_id_1",
        "username": "玩家1",
        "symbol": "X"
    },
    "right_player": {                // 右側玩家資訊
        "sid": "socket_id_2",
        "username": "玩家2",
        "symbol": "O"
    },
    "my_side": "left",               // 玩家所在位置 ('left' 或 'right')
    "scores": {                      // 戰績
        "left": 0,
        "right": 0,
        "draw": 0
    },
    "round_count": 0                 // 當前回合數 (0-4, 代表第1-5回合)
}
```

---

### 4. 執行移動

**事件**: `make_move`

**方向**: Client → Server

**請求格式**:
```javascript
socket.emit('make_move', {
    row: 0,    // 行座標 (0-2)
    col: 1     // 列座標 (0-2)
});
```

**參數**:
- `row` (number): 行座標，範圍 0-2
  - 0: 第一行
  - 1: 第二行
  - 2: 第三行
- `col` (number): 列座標，範圍 0-2
  - 0: 第一列
  - 1: 第二列
  - 2: 第三列

**座標對應棋盤位置**:
```
     col 0   col 1   col 2
row 0   0  |   1  |   2
       ----+------+----
row 1   3  |   4  |   5
       ----+------+----
row 2   6  |   7  |   8
```

**範例**:
```javascript
// 點擊中間格子 (位置 4)
socket.emit('make_move', { row: 1, col: 1 });

// 點擊左上角 (位置 0)
socket.emit('make_move', { row: 0, col: 0 });
```

---

### 5. 移動完成

**事件**: `move_made`

**方向**: Server → Client (room broadcast)

**回應格式**:
```javascript
socket.on('move_made', function(data) {
    // 更新棋盤
});
```

**資料結構**:
```javascript
{
    "row": 1,         // 行座標
    "col": 1,         // 列座標
    "symbol": "X",    // 下在此格的符號
    "turn": "O"       // 下一回合的符號
}
```

---

### 6. 回合結束

**事件**: `round_end`

**方向**: Server → Client (room broadcast)

**回應格式**:
```javascript
socket.on('round_end', function(data) {
    // 顯示回合結果
});
```

**資料結構**:
```javascript
{
    "winner": "X",               // 獲勝符號 ('X', 'O', 'Draw')
    "scores": {                  // 更新後的戰績
        "left": 1,
        "right": 0,
        "draw": 0
    },
    "round_count": 1,            // 當前回合數
    "match_finished": false,     // 比賽是否結束
    "winning_lines": [           // 獲勝連線的座標
        [[0, 0], [0, 1], [0, 2]]  // 第一行
    ]
}
```

**獲勝連線格式說明**:
- `winning_lines` 是一個陣列，包含所有獲勝的連線
- 每條連線包含 3 個座標點 `[row, col]`
- 可能有多條連線（極少數情況）

**連線範例**:
```javascript
// 第一行
[[0, 0], [0, 1], [0, 2]]

// 第一列
[[0, 0], [1, 0], [2, 0]]

// 主對角線
[[0, 0], [1, 1], [2, 2]]

// 副對角線
[[0, 2], [1, 1], [2, 0]]
```

---

### 7. 遊戲重置（下一回合）

**事件**: `reset_game`

**方向**: Client → Server

**請求格式**:
```javascript
socket.emit('reset_game');
```

**說明**: 開始新的一個回合（在5戰3勝的賽制中）

---

### 8. 重置完成

**事件**: `game_reset`

**方向**: Server → Client (room broadcast)

**回應格式**:
```javascript
socket.on('game_reset', function(data) {
    // 重置棋盤，開始新回合
});
```

**資料結構**:
```javascript
{
    "turn": "O",                 // 新回合的先手符號
    "scores": {                  // 當前戰績
        "left": 1,
        "right": 0,
        "draw": 0
    },
    "round_count": 1,            // 當前回合數
    "match_finished": false,     // 比賽是否結束
    "current_first_player": "right"  // 當前先手玩家 ('left' 或 'right')
}
```

---

### 9. 開始新比賽

**事件**: `start_new_match`

**方向**: Client → Server

**請求格式**:
```javascript
socket.emit('start_new_match');
```

**說明**: 
- 當 5 戰 3 勝的比賽結束後，開始新的一輪比賽
- 重置所有分數和回合數
- 重新隨機分配座位和符號

---

### 10. 新比賽開始

**事件**: `new_match_started`

**方向**: Server → Client (room broadcast)

**回應格式**:
```javascript
socket.on('new_match_started', function(data) {
    // 重新初始化，開始新比賽
});
```

**資料結構**:
```javascript
{
    "turn": "X",                 // 新比賽的先手符號
    "scores": {                  // 重置後的戰績
        "left": 0,
        "right": 0,
        "draw": 0
    },
    "round_count": 0,            // 重置回合數
    "match_finished": false,     // 比賽狀態
    "left_player": {             // 重新分配的左側玩家
        "sid": "socket_id_1",
        "username": "玩家1",
        "symbol": "O"            // 符號可能改變
    },
    "right_player": {            // 重新分配的右側玩家
        "sid": "socket_id_2",
        "username": "玩家2",
        "symbol": "X"            // 符號可能改變
    },
    "current_first_player": "left"
}
```

---

### 11. 對手離開

**事件**: `opponent_left`

**方向**: Server → Client (room broadcast)

**回應格式**:
```javascript
socket.on('opponent_left', function() {
    // 對手已離開，重新配對
});
```

**說明**: 
- 當對手斷線或離開房間時觸發
- 客戶端應重置遊戲狀態
- 自動重新發起 `join_pvp` 配對

---

### 12. 房間已滿

**事件**: `room_full`

**方向**: Server → Client

**回應格式**:
```javascript
socket.on('room_full', function(data) {
    // 顯示錯誤訊息
});
```

**資料結構**:
```javascript
{
    "message": "房間已滿，請稍後再試"
}
```

---

### 13. 遊戲進行中

**事件**: `game_in_progress`

**方向**: Server → Client

**回應格式**:
```javascript
socket.on('game_in_progress', function(data) {
    // 顯示遊戲進行中訊息
});
```

**資料結構**:
```javascript
{
    "message": "目前已有遊戲進行中，請稍後再試"
}
```

**說明**: 
- 當有玩家正在遊戲中，且沒有等待中的房間時觸發
- 防止同時進行多場遊戲

---

## 資料結構定義

### PlayerInfo (玩家資訊)
```javascript
{
    "sid": "socket_id",      // Socket.IO 連線 ID
    "username": "玩家名稱",   // 用戶名稱
    "symbol": "X"            // 玩家符號 ('X' 或 'O')
}
```

### Scores (戰績)
```javascript
{
    "left": 0,    // 左側玩家得分
    "right": 0,   // 右側玩家得分
    "draw": 0     // 平手局數
}
```

### Board (棋盤狀態)
```javascript
// 陣列格式，長度為 9，索引 0-8 對應棋盤位置
[null, "X", null, "O", "X", null, null, null, "O"]

// 位置對應:
// 0 | 1 | 2
// ---------
// 3 | 4 | 5
// ---------
// 6 | 7 | 8
```

### Coordinate (座標)
```javascript
{
    "row": 0,    // 行 (0-2)
    "col": 1     // 列 (0-2)
}
```

---

## 錯誤處理

### 一般錯誤處理原則
1. **無效移動**: Server 會拒絕無效的移動請求，不會發送 `move_made` 事件
2. **權限驗證**: Server 會檢查是否輪到該玩家，以及格子是否已被佔用
3. **斷線重連**: 玩家斷線後，房間會被清除，對手會收到 `opponent_left` 事件

### 移動驗證規則
Server 會驗證以下條件，不符合則拒絕移動：
- 座標範圍必須在 0-2 之間
- 遊戲必須處於進行中狀態
- 必須輪到該玩家
- 目標格子必須為空

### Session 驗證
- 所有遊戲事件都需要有效的 Session (登入狀態)
- Session 包含: `user` (用戶名), `icon` (圖示)

---

## 事件流程圖

### PVP 遊戲完整流程

```
Client A                Server               Client B
   |                      |                      |
   |--join_pvp---------->|                      |
   |<-waiting_for_opponent|                      |
   |                      |<------join_pvp-------|
   |<-------game_start----|----game_start------->|
   |                      |                      |
   |--make_move---------->|                      |
   |<-------move_made-----|----move_made-------->|
   |                      |<-----make_move-------|
   |<-------move_made-----|----move_made-------->|
   |                      |                      |
   |<-------round_end-----|----round_end-------->|
   |--reset_game--------->|                      |
   |<-------game_reset----|----game_reset------->|
   |                      |                      |
   |       (遊戲繼續...)   |                      |
   |                      |                      |
   |<-------round_end-----|----round_end-------->|
   | (match_finished=true)|                      |
   |--start_new_match---->|                      |
   |<--new_match_started--|--new_match_started-->|
   |                      |                      |
```

---

## 版本記錄

- **v1.0** (2026-01-15): 初始版本，定義所有 PVP 模式的通訊協定

---

## 注意事項

1. **所有事件都使用 Socket.IO** 進行即時通訊
2. **座標系統**: 統一使用 `(row, col)` 格式，範圍 0-2
3. **符號**: 使用字串 `"X"` 和 `"O"`，不是字元
4. **房間廣播**: 大部分遊戲事件會廣播給房間內的所有玩家
5. **時間戳記**: 聊天訊息由 Server 端添加時間戳記，格式為 `HH:MM:SS`
6. **Session 依賴**: 所有遊戲功能都需要先登入（建立 Session）
