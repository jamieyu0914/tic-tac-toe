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
    │  Game.py │    │  app.py  │    │RoomManager.py│
    │          │    │ (WebApp) │    │              │
    └──────────┘    └──────────┘    └──────────────┘
```

## 1. Game.py - 遊戲核心模組

### 類別與枚舉

```python
┌─────────────────┐
│   Player        │ (Enum)
├─────────────────┤
│ + X             │
│ + O             │
└─────────────────┘

┌─────────────────┐
│  GameResult     │ (Enum)
├─────────────────┤
│ + DRAW          │
│ + ONGOING       │
└─────────────────┘

┌──────────────────────────────┐
│         Game                 │
├──────────────────────────────┤
│ - board: List[Optional[str]] │ 
│ - turn: str                  │
│ - winner: Optional[str]      │
│ - started: bool              │
├──────────────────────────────┤
│ + reset()                    │
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
- `board`: 9 格棋盤（一維陣列），None 表示空位
- `turn`: 當前回合 ('X' 或 'O')
- `winner`: 勝者 ('X', 'O', 'Draw', 或 None)
- `started`: 遊戲是否已開始

### 關鍵方法說明
- `make_move()`: 執行移動，自動切換回合和檢查勝負
- `_check_winner()`: 內部方法，檢查勝負狀態
- `get_state()/load_state()`: 狀態序列化（用於 Session）

## 2. RoomManager.py - 房間管理模組

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
│ - scores: dict               │ (5戰3勝戰績)
│ - round_count: int           │
│ - match_finished: bool       │
│ - current_first_player: str  │
│ - left_player: PlayerInfo    │
│ - right_player: PlayerInfo   │
├──────────────────────────────┤
│ + add_player()               │
│ + remove_player()            │
│ + get_player_by_sid()        │
│ + _assign_seats_and_symbols()│ (隨機分配)
│ + make_move()                │
│ + reset()                    │
│ + check_round_end()          │
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

## 3. app.py - Flask 應用層（類別化）

```python
┌──────────────────────────────┐
│         WebApp               │
├──────────────────────────────┤
│ - app: Flask                 │
│ - socketio: SocketIO         │
│ - lock: Lock                 │
├──────────────────────────────┤
│ + __init__()                 │
│ - _register_routes()         │
│ + get_or_create_game()       │
│ + save_game()                │
│ + login()                    │ → /login
│ + home()                     │ → /
│ + reset()                    │ → /reset
│ + logout()                   │ → /logout
│ + run()                      │
└──────────────────────────────┘
         │
         │ manages
         ▼
┌──────────────────────────────┐
│      Session 管理            │
├──────────────────────────────┤
│ + get_or_create_game()       │──> 創建 Game 實例
│ + save_game()                │──> 保存到 Session
└──────────────────────────────┘
```

### 流程
1. 路由接收 HTTP 請求
2. 從 Session 載入或創建 Game 實例
3. 根據請求處理遊戲邏輯
4. 將遊戲狀態保存回 Session
5. 返回 HTML 模板

## 4. Socket.IO 事件層

### chat_events.py - 聊天事件
```python
┌──────────────────────────────┐
│   Chat Events                │
├──────────────────────────────┤
│ • chat message               │ (即時聊天訊息)
└──────────────────────────────┘
```

### game_events.py - 遊戲事件
```python
┌──────────────────────────────┐
│   Game Events                │
├──────────────────────────────┤
│ • join_pvp                   │ (配對加入)
│ • make_move                  │ (下棋)
│ • reset_game                 │ (下一回合)
│ • start_new_match            │ (開新對局)
│ • disconnect                 │ (斷線處理)
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
6. **隨機分配座位（左/右）和符號（X/O）**
7. 左側玩家先手，開始第 1 回合
8. 廣播 `game_start` 給兩位玩家

### 移動同步流程
1. 玩家觸發 `make_move` 事件（傳送座標 {row, col}）
2. `RoomManager.make_move()` 驗證並執行移動
3. 廣播 `move_made` 給房間內所有玩家（只傳該格資訊）
4. 若遊戲結束 → 廣播 `round_end`（包含獲勝線條）
5. 更新戰績，檢查是否達到 3 勝

## 完整系統互動圖

```
┌──────────────┐
│   Browser    │
│   (Client)   │
└──────┬───────┘
       │
       │ HTTP / WebSocket
       ▼
┌────────────────────────────────────────────────────┐
│          Flask + Socket.IO (WebApp)                │
│  ┌────────────┐  ┌──────────────┐  ┌────────────┐│
│  │  app.py    │  │chat_events.py│  │game_events │││
│  │  (WebApp)  │  │   (Chat)     │  │   (PVP)    │││
│  │  Routes    │  │              │  │            │││
│  └─────┬──────┘  └──────────────┘  └──────┬─────┘│
│        │                                   │       │
│        │ Session管理              PVP房間管理│      │
│        ▼                                   ▼       │
│  ┌──────────┐                    ┌──────────────┐│
│  │   Game   │◄───────────────────│ RoomManager  ││
│  │          │                    │ • 配對系統   ││
│  │  (核心)  │                    │ • 5戰3勝     ││
│  └──────────┘                    │ • 隨機分配   ││
│                                  │  └─GameRoom  ││
│                                  │    └─Game    ││
│                                  └──────────────┘│
└────────────────────────────────────────────────────┘

特點：
• 前後端採用座標協定 (row, col) 溝通
• 只傳送必要資料（單格更新，非整個棋盤）
• 自動配對系統，隨機分配座位和符號
• 5戰3勝制，先手輪替機制
```