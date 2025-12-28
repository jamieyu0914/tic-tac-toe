# 井字遊戲類別圖說明

## 類別架構總覽

```
┌─────────────────────────────────────────────────────────┐
│                    Tic-Tac-Toe 系統                      │
└─────────────────────────────────────────────────────────┘
                           │
          ┌────────────────┼────────────────┐
          ▼                ▼                ▼
    ┌──────────┐    ┌──────────┐    ┌──────────────┐
    │  Game.py │    │AIPlayer  │    │RoomManager.py│
    └──────────┘    └──────────┘    └──────────────┘
```

## 1. Game.py - 遊戲核心模組

### 類別與枚舉

```python
┌─────────────────┐
│   GameMode      │ (Enum)
├─────────────────┤
│ + COMPUTER      │
│ + PVP           │
└─────────────────┘

┌─────────────────┐
│   Difficulty    │ (Enum)
├─────────────────┤
│ + SIMPLE        │
│ + NORMAL        │
│ + HARD          │
└─────────────────┘

┌─────────────────┐
│   Player        │ (Enum)
├─────────────────┤
│ + X             │
│ + O             │
└─────────────────┘

┌─────────────────┐
│  GameResult     │ (Enum)
├─────────────────┤
│ + X_WIN         │
│ + O_WIN         │
│ + DRAW          │
│ + ONGOING       │
└─────────────────┘

┌──────────────────────────────┐
│         Game                 │
├──────────────────────────────┤
│ - board: List[Optional[str]] │ 
│ - turn: str                  │
│ - winner: Optional[str]      │
│ - mode: str                  │
│ - difficulty: str            │
│ - started: bool              │
├──────────────────────────────┤
│ + reset()                    │
│ + set_mode()                 │
│ + start()                    │
│ + make_move()                │
│ + get_available_moves()      │
│ + is_valid_move()            │
│ + get_state()                │
│ + load_state()               │
│ - _check_winner()            │
└──────────────────────────────┘
```

### 關鍵屬性說明
- `board`: 9 格棋盤，None 表示空位
- `turn`: 當前回合 ('X' 或 'O')
- `winner`: 勝者 ('X', 'O', 'Draw', 或 None)
- `mode`: 遊戲模式 ('computer' 或 'pvp')
- `difficulty`: AI 難度 ('simple', 'normal', 'hard')
- `started`: 遊戲是否已開始

### 關鍵方法說明
- `make_move()`: 執行移動，自動切換回合和檢查勝負
- `_check_winner()`: 內部方法，檢查勝負狀態
- `get_state()/load_state()`: 狀態序列化（用於 Session）

## 2. AIPlayer.py - AI 玩家模組

```python
┌──────────────────────────────┐
│        AIPlayer              │
├──────────────────────────────┤
│ - difficulty: str            │
│ - symbol: str                │
├──────────────────────────────┤
│ + get_move()                 │
│ - _get_available_moves()     │
│ - _simple_move()             │
│ - _normal_move()             │
│ - _hard_move()               │
│ - _find_winning_move()       │
│ - _minimax()                 │
│ - _check_winner()            │
└──────────────────────────────┘
```

### AI 策略說明

**Simple 模式：**
- 隨機選擇空位

**Normal 模式（策略優先級）：**
1. 如果可以贏 → 走贏棋的步
2. 如果對手可以贏 → 擋住對手
3. 中心位置（4）為空 → 走中心
4. 角落位置（0,2,6,8）為空 → 走角落
5. 其他 → 隨機

**Hard 模式：**
- 使用 Minimax 演算法
- 遞迴搜索所有可能走法
- 選擇最優解（完美走法）

### 關係
```
AIPlayer ──uses──> Game._check_winner()
AIPlayer ──called by──> app.py (電腦回合時)
```

## 3. RoomManager.py - 房間管理模組

```python
┌──────────────────────────────┐
│      PlayerInfo              │
├──────────────────────────────┤
│ - sid: str                   │
│ - username: str              │
│ - symbol: str                │
├──────────────────────────────┤
│ + to_dict()                  │
└──────────────────────────────┘
         ▲
         │ has 2
         │
┌──────────────────────────────┐
│       GameRoom               │
├──────────────────────────────┤
│ - room_id: str               │
│ - game: Game                 │◄──── contains
│ - players: List[PlayerInfo]  │
│ - waiting: bool              │
├──────────────────────────────┤
│ + add_player()               │
│ + remove_player()            │
│ + get_player_by_sid()        │
│ + make_move()                │
│ + reset()                    │
│ + get_state()                │
└──────────────────────────────┘
         ▲
         │ manages *
         │
┌──────────────────────────────┐
│      RoomManager             │
├──────────────────────────────┤
│ - rooms: Dict[str, GameRoom] │
│ - player_to_room: Dict       │
├──────────────────────────────┤
│ + create_room()              │
│ + join_room()                │
│ + leave_room()               │
│ + get_available_room()       │
│ + get_room()                 │
│ + get_room_by_sid()          │
│ + make_move()                │
│ + reset_room()               │
└──────────────────────────────┘
```

### 類別關係說明

- **RoomManager** 管理多個 **GameRoom**
- 每個 **GameRoom** 包含：
  - 一個 **Game** 實例（遊戲邏輯）
  - 兩個 **PlayerInfo** 實例（玩家資訊）
- **RoomManager** 維護兩個映射：
  - `rooms`: room_id → GameRoom
  - `player_to_room`: socket_id → room_id

## 4. app.py - Flask 應用層

```python
┌──────────────────────────────┐
│      Flask Routes            │
├──────────────────────────────┤
│ /login (GET, POST)           │
│ / (GET)                      │
│ /game (GET, POST)            │
│ /reset (GET)                 │
│ /logout (GET)                │
└──────────────────────────────┘
         │
         │ uses
         ▼
┌──────────────────────────────┐
│   Helper Functions           │
├──────────────────────────────┤
│ + get_or_create_game()       │──> 創建 Game 實例
│ + save_game()                │──> 保存到 Session
└──────────────────────────────┘
```

### 流程
1. 路由接收 HTTP 請求
2. 從 Session 載入或創建 Game 實例
3. 根據請求處理遊戲邏輯
4. 電腦模式：調用 AIPlayer 計算移動
5. 將遊戲狀態保存回 Session
6. 返回 HTML 模板

## 5. chatroom.py - Socket.IO 事件層

```python
┌──────────────────────────────┐
│   Socket.IO Events           │
├──────────────────────────────┤
│ • chat message               │
│ • join_pvp                   │
│ • make_move                  │
│ • reset_game                 │
│ • disconnect                 │
└──────────────────────────────┘
         │
         │ uses
         ▼
┌──────────────────────────────┐
│   room_manager (全域實例)     │
│   RoomManager                │
└──────────────────────────────┘
```

### PVP 配對流程
1. 玩家 A 觸發 `join_pvp` 事件
2. `RoomManager.get_available_room()` 查找等待中的房間
3. 若無等待房間 → 創建新房間，等待對手
4. 玩家 B 觸發 `join_pvp` 事件
5. 加入玩家 A 的房間
6. 廣播 `game_start` 給兩位玩家

### 移動同步流程
1. 玩家觸發 `make_move` 事件
2. `RoomManager.make_move()` 驗證並執行移動
3. 廣播 `game_update` 給房間內所有玩家

## 完整系統互動圖

```
┌──────────────┐
│   Browser    │
│   (Client)   │
└──────┬───────┘
       │
       │ HTTP / WebSocket
       ▼
┌──────────────────────────────────────────┐
│          Flask + Socket.IO               │
│  ┌────────────┐      ┌────────────┐     │
│  │  app.py    │      │chatroom.py │     │
│  │  (Routes)  │      │  (Events)  │     │
│  └─────┬──────┘      └──────┬─────┘     │
│        │                    │            │
│        │ 電腦模式           │ PVP模式    │
│        ▼                    ▼            │
│  ┌──────────┐        ┌──────────────┐   │
│  │   Game   │◄───────│ RoomManager  │   │
│  └────┬─────┘        │  └─GameRoom  │   │
│       │              │    └─Game    │   │
│       │              └──────────────┘   │
│       │                                  │
│       ▼                                  │
│  ┌──────────┐                           │
│  │ AIPlayer │                           │
│  └──────────┘                           │
└──────────────────────────────────────────┘
```

## 與 TaiwanMJ 的風格對比

### 相似點
1. **類別導向設計**
   - TaiwanMJ: `Player`, `Deck`, `Controller`, `Rule16`
   - Tic-Tac-Toe: `Game`, `AIPlayer`, `RoomManager`, `GameRoom`

2. **枚舉使用**
   - TaiwanMJ: `SUIT`, `WIND`, `MELD`, `Action`
   - Tic-Tac-Toe: `GameMode`, `Difficulty`, `Player`, `GameResult`

3. **狀態管理**
   - TaiwanMJ: 玩家狀態、牌組狀態
   - Tic-Tac-Toe: `get_state()`/`load_state()`

4. **完整註解**
   - 模組級 docstring
   - 類別和方法說明
   - 中文註解

### 差異點
1. **執行緒模型**
   - TaiwanMJ: `Player` 繼承 `Thread`，使用事件同步
   - Tic-Tac-Toe: 無需執行緒（遊戲較簡單）

2. **複雜度**
   - TaiwanMJ: 複雜規則（吃碰槓胡、台數計算）
   - Tic-Tac-Toe: 簡單規則（勝負判定）

3. **通訊方式**
   - TaiwanMJ: 使用 `pubsub` 模組
   - Tic-Tac-Toe: 使用 Flask-SocketIO
