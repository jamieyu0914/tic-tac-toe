# 代碼重構說明 - HTML/CSS/JavaScript 分離

## 重構日期
2026年1月13日

## 重構目的
將原本混雜在 HTML 中的 JavaScript 代碼分離到獨立文件，提高代碼的可維護性和可讀性。

## 文件結構

### 之前（混亂）
```
index.html (400+ 行)
├── HTML 結構
├── 內嵌 JavaScript (300+ 行)
└── 引用外部 CSS
```

### 之後（清晰）
```
index.html (71 行) ✓ 簡潔
├── HTML 結構
├── 引用外部 CSS
└── 引用外部 JavaScript

static/js/game.js (新建) ✓ 獨立的遊戲邏輯
├── Socket.IO 通訊
├── 遊戲狀態管理
├── UI 更新函數
└── Canvas 繪圖功能
```

## 修改內容

### 1. 創建獨立的 JavaScript 文件

**文件位置**: `app/static/js/game.js`

**內容結構**:
```javascript
// 全局變量聲明
const socket = io();
let gameState = {...};

// 初始化函數
function initGame(gameMode) {...}

// 聊天室功能
function setupChatEvents() {...}
function appendMessage(msg) {...}
function sendMessage() {...}

// 遊戲事件處理
function setupPvPEvents() {...}

// 遊戲控制
function startPvp() {...}
function resetGame() {...}

// 棋盤更新
function clearBoard() {...}
function updateCell(row, col, symbol) {...}
function updateBoard(boardData) {...}

// UI 更新
function updateTurnDisplay() {...}
function updateScoreDisplay() {...}
function updatePlayersDisplay() {...}

// 連線繪製
function drawWinningLines(winningLines) {...}
function clearWinningLines() {...}
```

### 2. 簡化 HTML 文件

**修改前** (index.html 約 420 行):
```html
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<script>
    // 300+ 行的 JavaScript 代碼
    const socket = io();
    // ... 大量代碼 ...
</script>
```

**修改後** (index.html 僅 71 行):
```html
<!-- Socket.IO -->
<script src="https://cdn.socket.io/4.7.5/socket.io.min.js"></script>
<!-- 遊戲邏輯 -->
<script src="{{ url_for('static', filename='js/game.js') }}"></script>
<!-- 初始化遊戲 -->
<script>
    document.addEventListener('DOMContentLoaded', function() {
        initGame("{{ mode }}");
    });
</script>
```

## 優點

### 1. **可讀性提升** 📖
- HTML 文件從 420 行減少到 71 行（減少 83%）
- HTML 只負責結構，邏輯完全分離
- 代碼更容易閱讀和理解

### 2. **可維護性提升** 🔧
- JavaScript 代碼獨立，易於修改和調試
- 函數分類清晰，便於定位問題
- 添加新功能更容易

### 3. **可重用性提升** ♻️
- JavaScript 代碼可以在其他頁面重用
- 函數模塊化，可以單獨測試

### 4. **緩存優化** ⚡
- 瀏覽器可以緩存 game.js 文件
- 修改 HTML 不會導致 JavaScript 重新下載
- 提升頁面加載速度

### 5. **開發體驗提升** 👨‍💻
- IDE 可以提供更好的 JavaScript 語法高亮
- 支持 JavaScript 的自動補全和錯誤檢查
- 可以使用 JavaScript 的調試工具

## 代碼組織

### game.js 的函數分類

#### 初始化類
- `initGame(gameMode)` - 初始化遊戲

#### 聊天功能類
- `setupChatEvents()` - 設置聊天事件
- `appendMessage(msg)` - 添加訊息
- `sendMessage()` - 發送訊息

#### 事件處理類
- `setupPvPEvents()` - 設置 PvP 事件監聽

#### 遊戲控制類
- `startPvp()` - 開始 PvP 配對
- `resetGame()` - 重置遊戲

#### 棋盤操作類
- `clearBoard()` - 清空棋盤
- `updateCell(row, col, symbol)` - 更新單個格子
- `updateBoard(boardData)` - 更新整個棋盤

#### UI 更新類
- `updateTurnDisplay()` - 更新回合顯示
- `updateScoreDisplay()` - 更新分數顯示
- `updatePlayersDisplay()` - 更新玩家資訊顯示

#### 繪圖功能類
- `drawWinningLines(winningLines)` - 繪製獲勝連線
- `clearWinningLines()` - 清除連線

## 注意事項

### 1. Flask 模板變量傳遞
在 HTML 中只保留一個小的 script 標籤來傳遞 Flask 模板變量：
```javascript
initGame("{{ mode }}");  // 將 Python 變量傳遞給 JavaScript
```

### 2. 初始化時機
使用 `DOMContentLoaded` 事件確保 DOM 完全載入後再初始化：
```javascript
document.addEventListener('DOMContentLoaded', function() {
    initGame("{{ mode }}");
});
```

### 3. 全局函數
按鈕的 `onclick` 屬性仍然可以正常工作，因為函數在 game.js 中是全局定義的：
```html
<button onclick="startPvp()">開始配對</button>
<button onclick="resetGame()">重置</button>
<button onclick="sendMessage()">送出</button>
```

## 測試建議

1. **功能測試**: 確保所有遊戲功能正常運作
2. **事件測試**: 驗證所有按鈕點擊事件正常
3. **Socket.IO 測試**: 確認 WebSocket 通訊正常
4. **Canvas 測試**: 驗證連線繪製功能正常
5. **瀏覽器兼容性**: 在不同瀏覽器測試

## 未來改進建議

1. **模塊化**: 可以進一步將 game.js 拆分為多個模塊
   - `chat.js` - 聊天室功能
   - `board.js` - 棋盤操作
   - `socket-handler.js` - Socket.IO 事件處理
   - `ui-updater.js` - UI 更新功能

2. **使用構建工具**: 考慮使用 Webpack 或 Vite 打包
   - 支持 ES6 模塊
   - 代碼壓縮
   - 自動注入依賴

3. **TypeScript**: 考慮遷移到 TypeScript
   - 類型安全
   - 更好的 IDE 支持
   - 減少運行時錯誤

4. **框架化**: 如果項目繼續擴大，可以考慮使用前端框架
   - Vue.js / React / Angular
   - 組件化開發
   - 狀態管理

## 總結

通過這次重構，我們成功地：
- ✅ 將 HTML 文件大小減少了 83%
- ✅ 實現了 HTML、CSS、JavaScript 的完全分離
- ✅ 提高了代碼的可讀性和可維護性
- ✅ 改善了開發體驗
- ✅ 為未來的擴展打下良好基礎

代碼現在更加清晰、專業，符合前端開發的最佳實踐！
