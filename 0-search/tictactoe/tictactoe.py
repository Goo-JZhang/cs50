"""
Tic Tac Toe Player
"""
import ipdb

import math

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]

def player(board):
    """
    Returns player who has the next turn on a board.
    """
    count = 0
    for row in board:
        for ele in row:
            if ele=="X":
                count += 1
            elif ele=="O":
                count -=1
    if count:
        return "O"
    else:
        return "X"

def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    ret = []
    for i in range(9):
        if board[i//3][i%3]==None:
            ret.append((i//3,i%3))
    return ret
    #raise NotImplementedError


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    ret = initial_state()
    for i in range(9):
        if (i//3,i%3)==action:
            if board[i//3][i%3] is not None:
                raise Exception("Invalid action")
            ret[i//3][i%3] = player(board)
        else:
            ret[i//3][i%3] = board[i//3][i%3]
    return ret
    #raise NotImplementedError

def line(x):
    if x[0] in ("X","O"):
        for ele in x:
            if ele!=x[0]:
                return None
        return x[0]
    else:
        return None

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    x_win = False
    o_win = False
    #rows
    for row in board:
        tmp = line(row)
        if tmp=="X":
            x_win = True
        elif tmp=="O":
            o_win = True
    for col in range(3):
        tmp = line([board[0][col],board[1][col],board[2][col]])
        if tmp=="X":
            x_win = True
        elif tmp=="O":
            o_win = True
    tmp = line([board[0][0],board[1][1],board[2][2]])
    if tmp=="X":
        x_win = True
    elif tmp=="O":
        o_win = True
    tmp = line([board[0][2],board[1][1],board[2][0]])
    if tmp=="X":
        x_win = True
    elif tmp=="O":
        o_win = True
    if x_win and o_win:
        raise ValueError("Invalid board input")
    elif x_win:
        return "X"
    elif o_win:
        return "O"
    else:
        return None
    #raise NotImplementedError


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) is not None:
        return True
    elif len(actions(board))==0:
        return True
    else:
        return False
    #raise NotImplementedError


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    tmp = winner(board)
    if tmp=="X":
        return 1
    elif tmp=="O":
        return -1
    else:
        return 0
    #raise NotImplementedError

def get_min(board,side = 1):
    """
    side=1 presents player is 'X' while side=-1 presents player is 'O'
    """
    if terminal(board):
        return side*utility(board)
    acts = actions(board)
    ret = 2
    for act in acts:
        gm = get_max(result(board,act),side)
        if gm<ret:
            ret = gm
        if ret==-1:
            return ret
    return ret
            

def get_max(board,side = 1):
    """
    side=1 presents player is 'X' while side=-1 presents player is 'O'
    """
    if terminal(board):
        return side*utility(board)
    acts = actions(board)
    ret = -2
    for act in acts:
        gm = get_min(result(board,act),side)
        if gm>ret:
            ret = gm
        if ret == 1:
            return ret
    return ret

def get_optimal_score(board,side):
    if terminal(board):
        return utility(board)
    acts = actions(board)
    ret = -2
    for act in acts:
        gm = side*get_optimal_score(result(board,act),-side)
        if gm>ret:
            ret = gm
        if ret==1:
            return side*ret
    return side*ret

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    side = 1
    if player(board)=="O":
        side = -1
    #print(side)
    acts = actions(board)
    max_min_score = -2
    ret_act = None
    #print(f"Player{player(board)} choices:")
    for act in acts:
        gm = side*get_optimal_score(result(board,act),side=-side)
        if gm>max_min_score:
            max_min_score = gm
            ret_act = act
        if max_min_score==1:
            print("Absolute winning strategy")
            return ret_act
    return ret_act
    #raise NotImplementedError

minimax([["O","X","O"],[None,"X",None],["X",None,None]])