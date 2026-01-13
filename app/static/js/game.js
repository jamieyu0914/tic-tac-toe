/**
 * 井字棋遊戲前端邏輯
 * 處理 Socket.IO 通訊、遊戲狀態和 UI 更新
 */

// 全局變量
const socket = io();
let chatMessages, chatInput, chatSend, gameBoard, pvpStatus, startPvpBtn, resetBtn;
let mode;

// 遊戲狀態
let mySymbol = null;
let currentTurn = 'X';
let gameActive = false;
let mySide = null; // 'left' or 'right'
let leftPlayer = null;
let rightPlayer = null;
let scores = { left: 0, right: 0, draw: 0 };
let roundCount = 0;
let matchFinished = false;
let board = [null, null, null, null, null, null, null, null, null];

/**
 * 初始化遊戲
 * 在 DOM 載入後調用
 */
function initGame(gameMode) {
    // 獲取 DOM 元素
    chatMessages = document.getElementById('chat-messages');
    chatInput = document.getElementById('chat-input');
    chatSend = document.getElementById('chat-send');
    gameBoard = document.getElementById('game-board');
    startPvpBtn = document.getElementById('start-pvp-btn');
    resetBtn = document.getElementById('reset-btn');
    mode = gameMode;

    // 初始化棋盤為禁用狀態
    if (gameBoard) {
        const cells = gameBoard.querySelectorAll('.cell');
        cells.forEach(cell => {
            cell.disabled = true;
            cell.textContent = '';
        });
    }

    // 設置聊天室事件監聽
    setupChatEvents();
    
    // 設置遊戲事件監聽
    if (mode === 'pvp') {
        setupPvPEvents();
    }
}

/**
 * 設置聊天室相關事件
 */
function setupChatEvents() {
    if (chatInput) {
        chatInput.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                chatSend.click();
            }
        });
    }

    socket.on('chat message', function(msg) {
        appendMessage(msg);
    });
}

/**
 * 設置 PvP 模式事件監聽
 */
function setupPvPEvents() {
    // 房間已滿事件
    socket.on('room_full', function(data) {
        updateGameStatus(data.message, 'error');
        startPvpBtn.disabled = false;
        startPvpBtn.textContent = '開始配對';
        appendMessage('[系統提示] ' + data.message);
    });

    // 等待對手事件
    socket.on('waiting_for_opponent', function(data) {
        updateGameStatus('等待對手加入...', '');
    });

    // 遊戲開始事件
    socket.on('game_start', function(data) {
        // 隱藏配對區
        document.querySelector('.pvp-search').style.display = 'none';
        
        leftPlayer = data.left_player;
        rightPlayer = data.right_player;
        mySide = data.my_side;
        mySymbol = data.your_symbol;
        currentTurn = data.turn;
        scores = data.scores;
        roundCount = data.round_count;
        gameActive = true;
        board = [null, null, null, null, null, null, null, null, null];
        
        // 顯示戰績板和棋盤
        const scoreBoard = document.getElementById('score-board');
        if (scoreBoard) scoreBoard.classList.add('active');
        
        if (gameBoard) {
            gameBoard.classList.add('active');
        }
        if (resetBtn) {
            resetBtn.classList.add('visible');
            resetBtn.textContent = '下一回合';
        }
        
        clearBoard();
        updateTurnDisplay();
        updateScoreDisplay();
    });

    // 移動完成事件
    socket.on('move_made', function(data) {
        const position = data.row * 3 + data.col;
        board[position] = data.symbol;
        updateCell(data.row, data.col, data.symbol);
        currentTurn = data.turn;
        updateTurnDisplay();
    });

    // 回合結束事件
    socket.on('round_end', function(data) {
        gameActive = false;
        scores = data.scores;
        roundCount = data.round_count;
        matchFinished = data.match_finished;
        
        // 繪製連線
        if (data.winning_lines && data.winning_lines.length > 0) {
            drawWinningLines(data.winning_lines);
        }
        
        // 更新遊戲狀態（只顯示一次）
        if (data.winner === 'Draw') {
            updateGameStatus('平手！', 'draw');
        } else {
            // 判斷誰贏了
            let iWon = false;
            if ((mySide === 'left' && data.winner === leftPlayer.symbol) ||
                (mySide === 'right' && data.winner === rightPlayer.symbol)) {
                iWon = true;
            }
            
            if (iWon) {
                updateGameStatus('你贏了！🎉', 'win');
            } else {
                updateGameStatus('你輸了！', 'lose');
            }
        }
        
        // 禁用所有格子
        if (gameBoard) {
            const cells = gameBoard.querySelectorAll('.cell');
            cells.forEach(cell => cell.disabled = true);
        }
        
        updateScoreDisplay();
        
        // 更新按鈕文字和顯示結果
        if (resetBtn) {
            if (matchFinished) {
                resetBtn.textContent = '下一輪';
                resetBtn.disabled = false;
                
                // 顯示最終結果
                let finalMessage = '';
                let winnerName = '';
                if (scores.left >= 3) {
                    winnerName = leftPlayer.username;
                    finalMessage = `🎉 ${leftPlayer.username} (${leftPlayer.symbol}) 獲勝！比分 ${scores.left}:${scores.right}`;
                } else if (scores.right >= 3) {
                    winnerName = rightPlayer.username;
                    finalMessage = `🎉 ${rightPlayer.username} (${rightPlayer.symbol}) 獲勝！比分 ${scores.right}:${scores.left}`;
                } else if (scores.left === 2 && scores.right === 2) {
                    finalMessage = '🤝 平手！雙方戰成 2:2';
                }
                
                if (finalMessage) {
                    updateGameStatus(finalMessage, 'win');
                }
                
                // 在聊天室顯示系統提示
                if (winnerName) {
                    appendMessage(`[系統提示] 🏆 ${winnerName} 主宰了比賽！`);
                } else if (scores.left === 2 && scores.right === 2) {
                    appendMessage('[系統提示] 比賽結束！雙方戰成平手！');
                }
            } else {
                resetBtn.textContent = '下一回合';
                resetBtn.disabled = false;
            }
        }
    });

    // 遊戲重置事件
    socket.on('game_reset', function(data) {
        currentTurn = data.turn;
        scores = data.scores;
        roundCount = data.round_count;
        matchFinished = data.match_finished;
        
        // 如果比賽已經結束，顯示最終結果
        if (matchFinished) {
            gameActive = false;
            
            // 更新分數顯示
            updateScoreDisplay();
            
            // 顯示最終結果
            let finalMessage = '';
            if (scores.left >= 3) {
                finalMessage = `比賽結束！${leftPlayer.username} (${leftPlayer.symbol}) 以 ${scores.left}:${scores.right} 獲勝！`;
            } else if (scores.right >= 3) {
                finalMessage = `比賽結束！${rightPlayer.username} (${rightPlayer.symbol}) 以 ${scores.right}:${scores.left} 獲勝！`;
            } else if (scores.left === 2 && scores.right === 2) {
                finalMessage = '比賽結束！雙方戰成 2:2 平手！';
            }
            
            if (finalMessage) {
                updateGameStatus(finalMessage, 'win');
            }
            
            // 更新按鈕
            if (resetBtn) {
                resetBtn.textContent = '下一輪';
                resetBtn.disabled = false;
            }
            
            return; // 不執行重置棋盤的操作
        }
        
        // 正常開始新回合
        gameActive = true;
        board = [null, null, null, null, null, null, null, null, null];
        
        clearBoard();
        clearWinningLines();
        updateScoreDisplay();
        updateTurnDisplay();
    });

    // 新比賽開始事件
    socket.on('new_match_started', function(data) {
        // 更新玩家資訊（可能重新分配了座位和符號）
        leftPlayer = data.left_player;
        rightPlayer = data.right_player;
        
        // 重置所有狀態
        currentTurn = data.turn;
        scores = data.scores;
        roundCount = data.round_count;
        matchFinished = data.match_finished;
        gameActive = true;
        board = [null, null, null, null, null, null, null, null, null];
        
        // 更新UI
        clearBoard();
        clearWinningLines();
        updateScoreDisplay();
        updateTurnDisplay();
        updateGameStatus('新的一輪開始！', 'turn');
        
        // 更新按鈕
        if (resetBtn) {
            resetBtn.textContent = '下一回合';
            resetBtn.disabled = true;
        }
    });

    // 對手離開事件
    socket.on('opponent_left', function() {
        updateGameStatus('對手已離開', 'error');
        gameActive = false;
        matchFinished = true;
        
        // 讓配對按鈕恢復可用
        if (startPvpBtn) {
            startPvpBtn.disabled = false;
            startPvpBtn.textContent = '開始配對';
        }
        
        // 禁用棋盤
        if (gameBoard) {
            const cells = gameBoard.querySelectorAll('.cell');
            cells.forEach(cell => {
                cell.disabled = true;
            });
        }
        
        // 更新重置按鈕
        if (resetBtn) {
            resetBtn.textContent = '對手離開 - 重新配對';
        }
        
        appendMessage('[系統提示] 您的對手已離開，遊戲結束。');
        
        // 清空遊戲狀態
        const gameStatus = document.getElementById('game-status');
        if (gameStatus) {
            gameStatus.className = 'game-status';
            gameStatus.textContent = '';
        }
    });

    // 處理棋盤點擊事件（使用座標方式）
    if (gameBoard) {
        gameBoard.addEventListener('click', function(e) {
            if (e.target.classList.contains('cell')) {
                const cellIndex = parseInt(e.target.dataset.cell);
                const row = Math.floor(cellIndex / 3);
                const col = cellIndex % 3;
                
                if (gameActive && currentTurn === mySymbol && !e.target.disabled && board[cellIndex] === null) {
                    socket.emit('make_move', { row: row, col: col });
                }
            }
        });
    }
}

/**
 * 聊天室功能
 */
function appendMessage(msg) {
    if (chatMessages) {
        const div = document.createElement('div');
        div.textContent = msg;
        chatMessages.appendChild(div);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

function sendMessage() {
    const msg = chatInput.value.trim();
    if (msg) {
        socket.emit('chat message', msg);
        chatInput.value = '';
    }
}

/**
 * 遊戲控制功能
 */
function startPvp() {
    socket.emit('join_pvp');
    startPvpBtn.disabled = true;
    startPvpBtn.textContent = '配對中...';
    if (pvpStatus) pvpStatus.textContent = '正在尋找對手...';
}

function resetGame() {
    if (matchFinished) {
        // 比賽結束，開始新的一輪
        socket.emit('start_new_match');
    } else {
        // 下一回合
        socket.emit('reset_game');
    }
}

/**
 * 棋盤更新功能
 */
function clearBoard() {
    if (!gameBoard) return;
    const cells = gameBoard.querySelectorAll('.cell');
    cells.forEach((cell) => {
        cell.textContent = '';
        cell.disabled = false;
    });
}

function updateCell(row, col, symbol) {
    if (!gameBoard) return;
    const cellIndex = row * 3 + col;
    const cells = gameBoard.querySelectorAll('.cell');
    if (cells[cellIndex]) {
        cells[cellIndex].textContent = symbol || '';
        cells[cellIndex].disabled = symbol !== null;
    }
}

function updateBoard(boardData) {
    if (!gameBoard) return;
    const cells = gameBoard.querySelectorAll('.cell');
    cells.forEach((cell, index) => {
        cell.textContent = boardData[index] || '';
        cell.disabled = boardData[index] !== null;
    });
}

/**
 * UI 顯示更新功能
 */
function updateGameStatus(message, type = '') {
    const gameStatus = document.getElementById('game-status');
    if (gameStatus) {
        gameStatus.textContent = message;
        gameStatus.className = 'game-status active ' + type;
    }
}

function updateTurnDisplay() {
    if (gameActive) {
        if (currentTurn === mySymbol) {
            updateGameStatus('YOUR TURN!!', 'turn');
        } else {
            updateGameStatus('對手回合...', 'waiting');
        }
    }
}

function updateScoreDisplay() {
    // 更新左玩家
    const leftSymbolEl = document.getElementById('left-symbol');
    const leftNameEl = document.getElementById('left-name');
    const leftScoreEl = document.getElementById('left-score');
    
    if (leftPlayer && leftSymbolEl && leftNameEl && leftScoreEl) {
        leftSymbolEl.textContent = leftPlayer.symbol;
        leftNameEl.textContent = leftPlayer.username;
        leftScoreEl.textContent = scores.left;
    }
    
    // 更新右玩家
    const rightSymbolEl = document.getElementById('right-symbol');
    const rightNameEl = document.getElementById('right-name');
    const rightScoreEl = document.getElementById('right-score');
    
    if (rightPlayer && rightSymbolEl && rightNameEl && rightScoreEl) {
        rightSymbolEl.textContent = rightPlayer.symbol;
        rightNameEl.textContent = rightPlayer.username;
        rightScoreEl.textContent = scores.right;
    }
    
    // 更新回合和平手
    const roundInfoEl = document.getElementById('round-info');
    const drawScoreEl = document.getElementById('draw-score');
    
    if (roundInfoEl) {
        roundInfoEl.textContent = `回合 ${roundCount + 1}/5`;
    }
    
    if (drawScoreEl) {
        drawScoreEl.textContent = scores.draw;
    }
}

function updatePlayersDisplay() {
    // 此函數已被 updateScoreDisplay 取代，保留空函數以兼容
}

/**
 * 連線繪製功能
 */
function drawWinningLines(winningLines) {
    // 清除之前的連線
    clearWinningLines();
    
    if (!gameBoard) return;
    
    // 為每條連線繪製線條
    winningLines.forEach((line, index) => {
        const canvas = document.createElement('canvas');
        canvas.className = 'winning-line';
        canvas.style.position = 'absolute';
        canvas.style.top = '0';
        canvas.style.left = '0';
        canvas.style.width = '100%';
        canvas.style.height = '100%';
        canvas.style.pointerEvents = 'none';
        canvas.style.zIndex = '10';
        
        gameBoard.style.position = 'relative';
        gameBoard.appendChild(canvas);
        
        const rect = gameBoard.getBoundingClientRect();
        canvas.width = rect.width;
        canvas.height = rect.height;
        
        const ctx = canvas.getContext('2d');
        const cellWidth = rect.width / 3;
        const cellHeight = rect.height / 3;
        
        // 起點和終點
        const startRow = line[0][0];
        const startCol = line[0][1];
        const endRow = line[2][0];
        const endCol = line[2][1];
        
        const startX = (startCol + 0.5) * cellWidth;
        const startY = (startRow + 0.5) * cellHeight;
        const endX = (endCol + 0.5) * cellWidth;
        const endY = (endRow + 0.5) * cellHeight;
        
        // 繪製線條
        ctx.strokeStyle = '#FF5722';
        ctx.lineWidth = 5;
        ctx.lineCap = 'round';
        ctx.beginPath();
        ctx.moveTo(startX, startY);
        ctx.lineTo(endX, endY);
        ctx.stroke();
    });
}

function clearWinningLines() {
    if (!gameBoard) return;
    const lines = gameBoard.querySelectorAll('.winning-line');
    lines.forEach(line => line.remove());
}
