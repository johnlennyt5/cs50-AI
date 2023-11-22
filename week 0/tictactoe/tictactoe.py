"""
Tic Tac Toe Player
"""

import math
import copy

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
    # Count the number of X and O on the board to determine the current player
    count_X = sum(row.count(X) for row in board)
    count_O = sum(row.count(O) for row in board)

    return O if count_X > count_O else X


def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    # Generate a set of all empty cells as possible actions
    return {(row, col) for row in range(3) for col in range(3) if board[row][col] == EMPTY}


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    # Ensure the action is valid, then create a copy of the board with the move applied
    if action not in actions(board):
        raise ValueError("Invalid action")

    row, col = action
    board_copy = copy.deepcopy(board)
    board_copy[row][col] = player(board)
    return board_copy

# Define functions to check for a winner in rows, columns, and diagonals
def check_line(line, player):
    return all(cell == player for cell in line)

def winner(board):
    """
    Returns the winner of the game, if there is one.
    """
    # Check rows and columns for a winner
    for row in board:
        if check_line(row, X):
            return X
        elif check_line(row, O):
            return O

    for col in range(3):
        if check_line([board[row][col] for row in range(3)], X):
            return X
        elif check_line([board[row][col] for row in range(3)], O):
            return O

    # Check diagonals for a winner
    if check_line([board[i][i] for i in range(3)], X) or check_line([board[i][2 - i] for i in range(3)], X):
        return X
    elif check_line([board[i][i] for i in range(3)], O) or check_line([board[i][2 - i] for i in range(3)], O):
        return O

    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    # The game is over if there is a winner or the board is full
    return winner(board) or all(all(cell != EMPTY for cell in row) for row in board)


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    # Determine the winner and return the corresponding utility value
    result = winner(board)
    if result == X:
        return 1
    elif result == O:
        return -1
    else:
        return 0
    
# Simplify the implementation of max_value and min_value functions

def max_value(board):
    # If the board is in a terminal state, return the utility value
    if terminal(board):
        return utility(board)
    
    # Find the maximum utility value by evaluating each possible action
    return max(min_value(result(board, action)) for action in actions(board))

def min_value(board):
    # If the board is in a terminal state, return the utility value
    if terminal(board):
        return utility(board)
    
    # Find the minimum utility value by evaluating each possible action
    return min(max_value(result(board, action)) for action in actions(board))

def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    # If the board is in a terminal state, return None as no action is possible
    if terminal(board):
        return None

    # Determine the current player
    current_player = player(board)

    # If the current player is X, find the action that maximizes the utility value
    if current_player == X:
        return max(actions(board), key=lambda action: min_value(result(board, action)))
    # If the current player is O, find the action that minimizes the utility value
    else:
        return min(actions(board), key=lambda action: max_value(result(board, action)))
