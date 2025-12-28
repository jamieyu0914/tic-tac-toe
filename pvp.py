from tic_tac_toe import check_winner
from modes import computer_move

def init_game_state(session):
    """Ensure game-related session keys exist with sensible defaults."""
    if 'board' not in session:
        session['board'] = [None] * 9
        session['turn'] = 'X'
        session['winner'] = None
        # default mode: computer normal
        session.setdefault('mode', 'computer')
        session.setdefault('difficulty', 'normal')
        session.setdefault('pvp_waiting', False)
        # whether the game has been started after selecting mode
        session.setdefault('started', False)

def set_mode(session, form):
    """Handle mode selection form submission.

    Expects a dict-like `form` with keys 'mode' and maybe 'difficulty'.
    Updates session in-place.
    """
    sel_mode = form.get('mode')
    session['mode'] = sel_mode
    if sel_mode == 'computer':
        session['difficulty'] = form.get('difficulty', 'normal')
        session['pvp_waiting'] = False
    else:
        # pvp selected: set waiting state
        session['pvp_waiting'] = True
    # reset game when changing mode and require pressing Start
    session['board'] = [None] * 9
    session['turn'] = 'X'
    session['winner'] = None
    session['started'] = False

def join_pvp(session):
    """Placeholder when a second player joins a PVP game."""
    session['pvp_waiting'] = False
    # when someone joins, start the game
    session['board'] = [None] * 9
    session['turn'] = 'X'
    session['winner'] = None
    session['started'] = True

def start_game(session):
    """Start the game after mode selection (reset board and mark started)."""
    session['board'] = [None] * 9
    session['turn'] = 'X'
    session['winner'] = None
    session['started'] = True

def handle_cell_click(session, form):
    """Process a cell click from the player.

    Expects 'cell' in form. Updates session (board, turn, winner) and
    performs a computer move when in computer mode.
    """
    # guard: ignore cell clicks if game hasn't been started
    if not session.get('started', False):
        return

    # quick guards
    if session.get('winner'):
        return
    if session.get('mode') == 'pvp' and session.get('pvp_waiting', True):
        return

    if 'cell' not in form:
        return

    try:
        idx = int(form['cell'])
    except (ValueError, TypeError):
        return

    board = session.get('board', [None] * 9)
    turn = session.get('turn', 'X')

    # validate index range
    if not (0 <= idx < len(board)):
        return

    if board[idx] is None:
        board[idx] = turn
        winner = check_winner(board)
        session['winner'] = winner
        session['board'] = board
        # toggle turn
        session['turn'] = 'O' if turn == 'X' else 'X'

        # if computer mode and it's computer's turn, make computer move
        if session.get('mode') == 'computer' and session.get('turn') == 'O' and not session.get('winner'):
            comp_idx = computer_move(board, session.get('difficulty', 'normal'))
            if comp_idx is not None and 0 <= comp_idx < len(board) and board[comp_idx] is None:
                board[comp_idx] = 'O'
                session['board'] = board
                winner = check_winner(board)
                session['winner'] = winner
                # set turn back to X if it was O
                session['turn'] = 'X' if session['turn'] == 'O' else session['turn']
