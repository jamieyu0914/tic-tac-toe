# Client 與 Server 通訊協議

## 說明

定義前端（JavaScript/Socket.IO）與後端（Flask/Socket.IO）的通訊格式，方便前後端協作開發。

---

## 聊天室功能

### 送出聊天訊息

Client 傳送訊息給 Server：

```json
{
  "username": "玩家1",
  "message": "你好！",
  "time": "12:34:56"
}
```

Server 收到後會廣播給所有人，格式如下：

```json
{
  "username": "玩家1",
  "message": "你好！",
  "time": "12:34:56"
}
```

---

## 遊戲配對

### 玩家加入配對

玩家按下「開始配對」後，前端送出：

```json
{
  "action": "join_pvp"
}
```

Server 處理邏輯：

- 有等待中的房間 → 加入房間，開始遊戲
- 無等待中的房間 → 創建新房間，等待對手
- 房間已滿 → 回傳錯誤訊息

### 等待對手

Server 回傳這個表示正在等對手：

```json
{
  "room_id": "room_abcd1234_5678",
  "status": "waiting"
}
```

### 開始遊戲

兩個人都進來後，Server 會送這個：

```json
{
  "room_id": "room_abcd1234_5678",
  "your_symbol": "X", // 你是 X 還是 O
  "turn": "X", // 現在輪到誰
  "left_player": {
    // 左邊玩家
    "username": "玩家1",
    "symbol": "X"
  },
  "right_player": {
    // 右邊玩家
    "username": "玩家2",
    "symbol": "O"
  },
  "my_side": "left", // 你在左邊還是右邊
  "scores": {
    // 目前戰績
    "left": 0,
    "right": 0,
    "draw": 0
  },
  "round_count": 0 // 第幾局（0代表第1局）
}
```

註：座位跟符號都是隨機分配的，這樣比較公平。

---

## 下棋動作

### 玩家下棋

前端送這個告訴 Server 要下在哪：

```json
{
  "row": 1, // 第幾行 (0, 1, 2)
  "col": 1 // 第幾列 (0, 1, 2)
}
```

棋盤座標系統：

```
     0列  1列  2列
0行   0 |  1 |  2
     ---+----+---
1行   3 |  4 |  5
     ---+----+---
2行   6 |  7 |  8
```

範例：

- 正中間：`{row: 1, col: 1}`
- 左上角：`{row: 0, col: 0}`

### Server 通知下棋結果

Server 確認可以下之後，會廣播給兩個玩家：

````json
{
    "row": 1,
    "col": 1,
    "symbol": "X",     // 這格現在是 X
    "turn": "O"        // 接下來換 O
}
```只需更新該格狀態，不需傳送完整棋盤資料

前端收到後更新棋盤就好，不用傳整個棋盤回來，這樣比較省流量。

---

## 一回合結束通知
當出現勝負或平手時，Server 廣播
### 有人贏了或平手
當連成一線或下滿了，Server 會送：
```json
{
    "winner": "X",              // X贏、O贏、或Draw平手
    "scores": {                 // 更新戰績
        "left": 1,
        "right": 0,
        "draw": 0
    },
    "round_count": 1,           // 打了幾局
    "match_finished": false,    // 5戰3勝結束了沒
    "winning_lines": [          // 連線的位置（可以畫紅線）
        [[0, 0], [0, 1], [0, 2]]
    ]
}
````

`winning_lines` 是陣列，每條線有 3 個點的座標。例如：

- 第一行：`[[0, 0], [0, 1], [0, 2]]`
- 第一列：`[[0, 0], [1, 0], [2, 0]]`
- 斜線：`[[0, 0], [1, 1], [2, 2]]`

---

## 下一局

### 開始新的一局

按下「下一局」後送出：

Server 會回傳：

````json
{
    "turn": "O",                      // 這局誰先下
    "scores": {"left": 1, "right": 0, "draw": 0},
    "round_count": 1,
    "match_finished": false,
    "current_first_player": "right"   // 這局誰先手
}
```替，第1局左側先手，第2局右側先手，依此類推

註：先手會輪流，第一局左邊先，第二局右邊先，這樣才公平。

### 重新開始5戰3勝
如果5戰3勝打完了，想重新來過：

Server 會重置所有東西，分數歸零，重新分配座位和符號：
```json
{
    "turn": "X",
    "scores": {"left": 0, "right": 0, "draw": 0},
    "round_count": 0,
    "match_finished": false,
    "left_player": {
        "username": "玩家1",
        "symbol": "O"         // 符號可能跟之前不一樣
    },
    "right_player": {
        "username": "玩家2",
        "symbol": "X"
    },
    "current_first_player": "left"
}
````

---

## 錯誤狀況

### 房間已滿

配對時如果房間滿了：

```json
{
  "message": "房間已滿，請稍後再試"
}
```

### 有人在玩

如果已經有其他人在玩，沒有空房間：

```json
{
  "message": "目前已有遊戲進行中，請稍後再試"
}
```

---

## 重要規則

### Server 會檢查的事

- 座標要在 0~2 之間
- 要輪到你才能下
- 那格要是空的
- 遊條件時 Server 會拒絕請求，不發送

不符合的話 Server 會直接擋掉，不會有任何回應。

### 使用注意事項

1. 要先登入才能玩（需要 session）
2. 座標都是從 0 開始算
3. 用 socket.io 傳送，不是 HTTP
4. 時間格式是 HH:MM:SS（24 小時制）

---

## 完整流程範例

```
玩家A                  Server                玩家B
  |                      |                      |
  |--join_pvp---------->|                      |
  |<-等待對手------------|                      |
  |                      |<------join_pvp-------|
  |<-------遊戲開始-------|----遊戲開始--------->|
  |                      |                      |
  |--下棋(1,1)---------->|                      |
  |<-------更新棋盤-------|----更新棋盤--------->|
  |                      |<-----下棋(0,0)-------|
  |<-------更新棋盤-------|----更新棋盤--------->|
  |                      |                      |
  |      (繼續對戰...)     |                      |
  |                      |                      |
  |<-------一局結束-------|----一局結束--------->|
  |--下一局------------->|                      |
  |<-------重置棋盤-------|----重置棋盤--------->|
  |                      |                      |
```

---補充說明

### 座標系統選擇

採用 `(row, col)` 格式而非 0~8 編號，便於前端處理和座標對應。

### 隨機分配機制

每次開始新比賽時，座位和符號會重新隨機分配，避免先手優勢固定。

### 先手輪替

每局先手會輪流切換（左 → 右 → 左 → 右...），確保公平性

### 為什麼先手會輪流？

第一局左邊先下，第二局右邊先下...這樣輪流，避免先手優勢影響太大。

---

最後更新：2026-01-15

## 事件對照 (Events)

為了消除前後端在事件名稱上的歧義，下面列出後端實作中實際使用的 Socket.IO 事件名稱、方向與範例 payload，前端可依此來實作或修正現有程式。

Client → Server

- `chat message`: 傳送聊天訊息。payload 可為物件或純文字，建議使用物件：

```json
{
  "username": "玩家1",
  "message": "你好！",
  "time": "12:34:56"
}
```

- `join_pvp`: 加入 PVP 配對。可以傳空 payload，也可使用通用 `action` 包裝（參考下方）。
- `make_move`: 下棋（payload 範例）：

```json
{
  "row": 1,
  "col": 1
}
```

- `reset_game`: 要求開始下一局（單回合重置）。
- `start_new_match`: 要求重置整個 5 戰 3 勝 比賽（分數歸零、重新分配座位/符號）。
- `action` (通用 wrapper): 後端同時支援一個通用的 `action` 事件，格式為：

```json
{ "action": "make_move", "data": { "row": 1, "col": 1 } }
```

Server → Client

- `chat message`: 廣播給所有使用者，payload 如上。
- `waiting_for_opponent`: 當創建房間並等待對手時發回，payload：

```json
{ "room_id": "room_abcd1234_5678", "status": "waiting" }
```

- `game_start`: 當兩位玩家都加入房間後，server 會將遊戲開始資訊發送給每位玩家（注意：此訊息會針對每個玩家的 socket id 個別發送，以便包含 `your_symbol` 與 `my_side`）：

```json
{
  "room_id": "room_abcd1234_5678",
  "your_symbol": "X",
  "turn": "X",
  "left_player": { "username": "玩家1", "symbol": "X", "sid": "..." },
  "right_player": { "username": "玩家2", "symbol": "O", "sid": "..." },
  "my_side": "left",
  "scores": { "left": 0, "right": 0, "draw": 0 },
  "round_count": 0
}
```

- `move_made`: 當一方下子成功後，server 會向該房間廣播單格更新：

```json
{ "row": 1, "col": 1, "symbol": "X", "turn": "O" }
```

- `round_end`: 當一回合結束（勝/和）時，server 廣播：

```json
{
  "winner": "X",
  "scores": { "left": 1, "right": 0, "draw": 0 },
  "round_count": 1,
  "match_finished": false,
  "winning_lines": [
    [
      [0, 0],
      [0, 1],
      [0, 2]
    ]
  ]
}
```

- `game_reset`: 下一局開始（回傳 turn、scores、round_count、match_finished、current_first_player）：

```json
{
  "turn": "O",
  "scores": { "left": 1, "right": 0, "draw": 0 },
  "round_count": 1,
  "match_finished": false,
  "current_first_player": "right"
}
```

- `new_match_started`: 當整個比賽 (5 戰 3 勝) 被重置時，server 發送新比賽資訊，payload 包含 left/right player 資訊：

```json
{
  "turn": "X",
  "scores": { "left": 0, "right": 0, "draw": 0 },
  "round_count": 0,
  "match_finished": false,
  "left_player": { "username": "玩家1", "symbol": "O" },
  "right_player": { "username": "玩家2", "symbol": "X" },
  "current_first_player": "left"
}
```

- 錯誤/狀態事件：`room_full`、`game_in_progress`（payload `{ "message": "..." }`），以及 `opponent_left`（無 payload 或可視需求附帶資訊）。

## 備註與建議

- 後端在收到不合法的請求（例如座標不在範圍、不是該玩家回合、或該格已被佔用）時，多數情況會 silent drop（直接忽略並 return），這是設計上的選擇：前端不得假設會收到錯誤回應，應在合理時間內實作超時或 retry 與 UI 提示。若你希望改為回傳錯誤 event（例如 `invalid_move`），可以在前端/後端雙方約定並由後端實作。

- `game_start` 會包含玩家專屬欄位（`your_symbol` 與 `my_side`），因此 server 目前是針對每位玩家的 socket id 個別發送，而非單純 room-wide broadcast；請在前端監聽相同的事件名稱以接收個別訊息。

- `action` wrapper: 後端同時支援直接事件（如 `make_move`）與通用 `action` 事件（`{action: 'make_move', data: {...}}`），兩種方式皆可使用，但請務必統一專案中前端的做法。

- 在文件前半的範例 JSON 與本節的事件名稱已對齊，建議以本節為最終參考。若你希望我把文件中所有範例的註解（例如 // 註解形式）改為純 JSON 或移除註解，或想新增更多範例（包含錯誤回應、action wrapper 範例），我可以再做一個小更新。
