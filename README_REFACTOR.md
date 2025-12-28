# 井字遊戲重構說明

## 重構目標

將 tic-tac-toe 專案重構為類別導向設計，使其風格與 project-TaiwanMJ 一致，便於後續繪製類別圖。

## 新增檔案

### 1. Game.py - 遊戲核心類別
**職責：**
- 管理遊戲狀態（棋盤、輪次、勝負）
- 勝負判定邏輯
- 遊戲流程控制

**主要類別：**
- `GameMode` - 遊戲模式枚舉（電腦對戰/玩家對戰）
- `Difficulty` - AI 難度枚舉（簡單/普通/困難）
- `Player` - 玩家符號枚舉（X/O）
- `GameResult` - 遊戲結果枚舉
- `Game` - 遊戲核心類別

**主要方法：**
- `reset()` - 重置遊戲
- `set_mode()` - 設置遊戲模式
- `start()` - 開始遊戲
- `make_move()` - 執行移動
- `get_state()` / `load_state()` - 狀態管理

### 2. AIPlayer.py - AI 玩家類別
**職責：**
- 實現不同難度的 AI 對手
- 提供遊戲決策邏輯

**主要類別：**
- `AIPlayer` - AI 玩家

**AI 策略：**
- **Simple 模式：** 隨機走法
- **Normal 模式：** 策略走法（贏 > 擋 > 中心 > 角落 > 隨機）
- **Hard 模式：** Minimax 演算法（完美走法）

**主要方法：**
- `get_move()` - 獲取 AI 的下一步
- `_simple_move()` - 簡單模式邏輯
- `_normal_move()` - 普通模式邏輯
- `_hard_move()` - 困難模式邏輯
- `_minimax()` - Minimax 演算法實現

### 3. RoomManager.py - 房間管理類別
**職責：**
- 管理 PVP 模式的遊戲房間
- 處理玩家配對和房間生命週期

**主要類別：**
- `PlayerInfo` - 玩家資訊類別
- `GameRoom` - 遊戲房間類別
- `RoomManager` - 房間管理器類別

**主要方法：**
- `create_room()` - 創建新房間
- `join_room()` - 加入房間
- `leave_room()` - 離開房間
- `get_available_room()` - 獲取可用房間
- `make_move()` - 執行移動
- `reset_room()` - 重置房間

## 重構檔案

### 1. app.py - Flask 應用主程式
**變更：**
- 移除對 `pvp.py` 的依賴
- 使用新的 `Game` 和 `AIPlayer` 類別
- 簡化路由邏輯
- 添加完整的中文註解

**主要函數：**
- `get_or_create_game()` - 從 session 獲取或創建遊戲實例
- `save_game()` - 保存遊戲狀態到 session
- 各路由處理函數（`login`, `home`, `game`, `reset`, `logout`）

### 2. chatroom.py - Socket.IO 事件處理
**變更：**
- 移除對 `game_rooms.py` 的依賴
- 使用新的 `RoomManager` 類別
- 添加完整的中文註解

**事件處理：**
- `chat message` - 聊天消息
- `join_pvp` - 加入 PVP 配對
- `make_move` - 玩家移動
- `reset_game` - 重置遊戲
- `disconnect` - 玩家斷線

## 可移除的舊檔案

以下檔案已被新類別取代，可以保留作為參考或刪除：
- `tic_tac_toe.py` - 功能已整合到 `Game.py`
- `modes.py` - 功能已整合到 `AIPlayer.py`
- `pvp.py` - 功能已整合到 `app.py`
- `game_rooms.py` - 功能已整合到 `RoomManager.py`

## 類別架構對比

### 重構前
```
功能式程式設計風格
├── tic_tac_toe.py（勝負判定函數）
├── modes.py（AI 邏輯函數）
├── pvp.py（PVP 邏輯函數）
└── game_rooms.py（房間管理字典）
```

### 重構後（類似 TaiwanMJ）
```
物件導向設計風格
├── Game.py（遊戲核心類別）
│   ├── GameMode（枚舉）
│   ├── Difficulty（枚舉）
│   ├── Player（枚舉）
│   └── Game（類別）
├── AIPlayer.py（AI 玩家類別）
│   └── AIPlayer（類別）
└── RoomManager.py（房間管理類別）
    ├── PlayerInfo（類別）
    ├── GameRoom（類別）
    └── RoomManager（類別）
```

## TaiwanMJ 風格特點

1. **類別導向設計**
   - 每個功能模組使用類別封裝
   - 清晰的職責分離

2. **枚舉使用**
   - 使用 `Enum` 定義常量
   - 提高程式碼可讀性

3. **完整註解**
   - 模組級別的 docstring
   - 類別和方法的說明文件
   - 中文註解說明邏輯

4. **狀態管理**
   - 明確的狀態管理方法
   - `get_state()` / `load_state()` 模式

## 測試建議

1. **電腦對戰模式**
   ```
   - 測試三種 AI 難度
   - 測試遊戲重置功能
   - 測試勝負判定
   ```

2. **PVP 對戰模式**
   ```
   - 測試房間創建和加入
   - 測試玩家移動同步
   - 測試玩家斷線處理
   ```

3. **登入登出**
   ```
   - 測試使用者認證
   - 測試 Session 管理
   ```

## 類別圖建議

建議繪製以下類別關係：
- Game 類別（核心）
- AIPlayer 類別（與 Game 的關聯）
- RoomManager、GameRoom、PlayerInfo（房間管理體系）
- Flask 路由與類別的互動

## 相容性

✅ 保持原有功能完全相容
✅ 前端 HTML/CSS/JS 無需修改
✅ URL 路由保持不變
✅ Session 機制正常運作
