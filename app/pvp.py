from tic_tac_toe import check_winner

def init_game_state(session):
    """Ensure game-related session keys exist with sensible defaults."""
    if 'board' not in session:
        session['board'] = [None] * 9
        session['turn'] = 'X'
        session['winner'] = None
        # default mode: pvp
        session.setdefault('mode', 'pvp')
        session.setdefault('pvp_waiting', False)
        session.setdefault('pvp_room_id', None)
        # whether the game has been started after selecting mode
        session.setdefault('started', False)

def set_mode(session, form):
    """Handle mode selection form submission.

    Expects a dict-like `form` with keys 'mode' and maybe 'difficulty'.
    Updates session in-place.
    """
    sel_mode = form.get('mode')
    session['mode'] = sel_mode
    # pvp selected: will use Socket.IO for matchmaking
    session['pvp_waiting'] = True
    session['pvp_room_id'] = None
    # reset game when changing mode and require pressing Start
    session['board'] = [None] * 9
    session['turn'] = 'X'
    session['winner'] = None
    session['started'] = False

def join_pvp(session):
    """Placeholder when a second player joins a PVP game.
    
    Note: Actual PvP matchmaking now happens via Socket.IO.
    This is kept for compatibility but may not be used.
    """
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