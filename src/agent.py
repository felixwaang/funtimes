#!/usr/bin/python3
# 9x9 Tic Tac Toe AI.
# Written by Felix Wang (z5112711) and Daniel Wu (z5114131)
# Last modified: 01/05/2019
# Parsing in the inputs, credits to Zac Partridge (z.partridge@unsw.edu.au)


##################################################################################################
# Briefly describe how your program works:                                                       #
# We employed an Alpha Beta Search using an evaluator (heuristic). The Alpha Beta Search         #
# calculates the heuristic only at the leaf nodes (i.e. when the depth of the child has          #
# exceeded the depth limit, or when a child evaluates as a won position). We attempt to increase #
# the depth limit as we make more moves as there are less children to evaluate. Our heuristic    #
# is evaluated by: (how many boards we can currently win in * how many ways we can win) -        #
# (how many boards they can win in * how many ways they can win). Ultimately, the Heuristic      #
# creates a snap shot of what the board can look like after the depth limit has been reached,    #
# and we attempt to make the moves to achieve the most favourable board for us. We use the       #
# Alpha Beta search to choose the best move based on the heuristic at every level (maximiser     #
# for us, minimiser for them).                                                                   #
#                                                                                                #
# Algorithms and data structures employed:                                                       #
# - Alpha beta search                                                                            #
# - Heuristic is a modified version of the week 5 tute one                                       #
# - Maintain possible board moves as a dictionary for efficiency                                 #
# - Boards are by a 2D arrays, board[i][j] where i is which 3x3 board, j is which tile inside    #
#                                                                                                #
# Design decisions made:                                                                         #
# - Originally we used copy.deepcopy() to create each board state one by one, however deepcopy   #
# requires some time and slowed our program down. Hence, instead, we would make a move on the    #
# current board and after evaluation, undo the moves from the current board.                     #
# - Heuristic used to be a double for loop to go over every board. Instead we opted for a        #
# single for loop with a bunch of if statements to make it slightly quicker.                     #
# - Depth Limit is increased as we go deeper into the game as less children nodes need to be     #
# expanded, this helps reduce unnecessary computation in the beginning to allow our program      #
# to run faster and as we go towards the end, better evaluation of positions.                    #
# - We modified the week 5 tute heuristic as we needed to understand how good our position is    #
# taking in a count of all 9 boards rather than a sub 3x3 board. Evaluating just a 3x3 board     #
# would cause our AI to evaluate a move as good if it helped us make 2 in a row, but lose on     #
# the very next turn.                                                                            #
# - Used Alpha beta over MCTS as MCTS isn't able to simulate enough games to identify the        #
# best possible move as we have a short time limit.                                              #
# - Used Python as it's the easiest language to code this project in, however, we understand     #
# the drawbacks of python being incredibly slow.                                                 #
##################################################################################################       

import socket
import sys
import numpy as np

# A board cell can hold:
#   0 - Empty
#   1 - I played here
#   2 - They played here

# The boards are of size 10 because index 0 isn't used
boards = np.zeros((10, 10), dtype="int8")
s = [".","X","O"]
# Current board to play in
curr = 0
# Number of moves played, used to increase depth_limit
num_moves_made = 0
# Depth Limit, how many levels of child boards to create
depth_limit = 5

# Print a row of the board
# This is just ported from game.c
def print_board_row(board, a, b, c, i, j, k):
    print(" "+s[board[a][i]]+" "+s[board[a][j]]+" "+s[board[a][k]]+" | " \
             +s[board[b][i]]+" "+s[board[b][j]]+" "+s[board[b][k]]+" | " \
             +s[board[c][i]]+" "+s[board[c][j]]+" "+s[board[c][k]])

# Print the entire board
# This is just ported from game.c
def print_board(board):
    print_board_row(board, 1,2,3,1,2,3)
    print_board_row(board, 1,2,3,4,5,6)
    print_board_row(board, 1,2,3,7,8,9)
    print(" ------+-------+------")
    print_board_row(board, 4,5,6,1,2,3)
    print_board_row(board, 4,5,6,4,5,6)
    print_board_row(board, 4,5,6,7,8,9)
    print(" ------+-------+------")
    print_board_row(board, 7,8,9,1,2,3)
    print_board_row(board, 7,8,9,4,5,6)
    print_board_row(board, 7,8,9,7,8,9)
    print()

#########################################################################
########################### Alpha Beta Search ###########################
#########################################################################

# Initial Alpha beta step - Finds max values from child nodes
# Params: board -> state of the 9x9 board
# Returns: The next move to make
def alphabeta(board):
    # Global variables: curr -> current board number
    global curr
    # Depth -> level of depth for the child board 
    depth = 0
    # Move to return, 0 if no good moves, else, 
    nextMove = 0

    # Set up alpha (max value, initiate as -infinity)
    alpha = -float('inf')
    # Set up beta (min value, initiate as infinity)
    beta = float('inf')

    # All possible moves that can be made on this board
    children = possibleMoves(board, curr)
    depth += 1

    for child in children:
        board[curr][child] = 1
        eval = calc_min(board, child, alpha, beta, depth, curr)
        board[curr][child] = 0
        if eval > alpha:
            alpha = eval
            nextMove = child
    return nextMove # this returns the next move to make

# Minimizer. 
# Params: board -> curr board state, move -> new board to play on
#         alpha -> alpha value, beta -> beta value
#         depth -> level of child, curr_move -> previous board played
# Returns: The minimizer move.
def calc_min(board, move, alpha, beta, depth, curr_move):
    global depth_limit

    # Checks if we made a winning move last move
    if checkWin(board, curr_move, 1):
        return float('inf')

    # If depth of child passes the limit
    if depth >= depth_limit:
        return calc_h(board)

    children = possibleMoves(board, move)
    depth += 1

    for child in children:
        board[move][child] = 2
        eval = calc_max(board, child, alpha, beta, depth, move)
        beta = min(beta, eval)
        board[move][child] = 0
        if beta <= alpha:
            break
    return beta

# Maximizer.
# Params: board -> curr board state, move -> new board to play on
#         alpha -> alpha value, beta -> beta value
#         depth -> level of child, curr_move -> previous board played
# Returns: The maximizer move.
def calc_max(board, move, alpha, beta, depth, curr_move):
    global depth_limit

    # Check if they made a winning move last move
    if checkWin(board, curr_move, 2):
        return -float('inf')

    # If depth of child passes the limit
    if depth >= depth_limit:
        return calc_h(board)

    children = possibleMoves(board, move)
    depth += 1

    for child in children:
        board[move][child] = 1
        eval = calc_min(board, child, alpha, beta, depth, move)
        alpha = max(alpha, eval)
        board[move][child] = 0
        if beta <= alpha:
            break      
    return alpha

#########################################################################
########################### End of Alpha Beta ###########################
#########################################################################

# All the possible moves that can be made on the current 3x3 board
# Params: board -> current 9x9 board state, boardnum -> which 3x3 board to play
# Returns: Dictionary with all the possible moves that can be made
def possibleMoves(board,boardnum):
    moves = {}
    for i in range(1,10):
        if board[boardnum][i] == 0:
            moves[i] = i
    return moves
    
# Finds which move to play.
# If we are losing in every move, make a random move
# Else, play what was suggested by Alpha Beta Search    
def play():
    global boards
    print_board(boards)
    moveToMake = alphabeta(boards)
    if moveToMake == 0:
        for i in range(1,10):
            if boards[curr][i] == 0:
                place(curr, i, 1)
                return i
    else:
        place(curr, moveToMake, 1)
        return moveToMake
    
#######################################################################
############################## Heuristic ##############################
#######################################################################

# Returns the heuristic for alpha beta search.
# Params: board -> 9x9 board state
# Returns: Heuristic value (Our # wins * Our # board win - their # wins * their # board win)
def calc_h(board):
    # us -> number of ways we can win
    # us_array -> number of boards we can win in
    us = 0 
    us_array = []
    # them -> number of ways they can win
    # them_array -> number of boards they can win in
    them = 0
    them_array = []

    for i in range(1,10):
        # Us / The rows
        if board[i][1] == board[i][2] == 1 and board[i][3] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][1] == board[i][3] == 1 and board[i][2] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][2] == board[i][3] == 1 and board[i][1] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][4] == board[i][5] == 1 and board[i][6] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][4] == board[i][6] == 1 and board[i][5] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][5] == board[i][6] == 1 and board[i][4] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][7] == board[i][8] == 1 and board[i][9] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][7] == board[i][9] == 1 and board[i][8] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][8] == board[i][9] == 1 and board[i][7] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)

        # Us / The columns
        if board[i][1] == board[i][4] == 1 and board[i][7] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][1] == board[i][7] == 1 and board[i][4] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][4] == board[i][7] == 1 and board[i][1] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][2] == board[i][5] == 1 and board[i][8] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][2] == board[i][8] == 1 and board[i][5] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][5] == board[i][8] == 1 and board[i][2] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][3] == board[i][6] == 1 and board[i][9] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][3] == board[i][9] == 1 and board[i][6] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][6] == board[i][9] == 1 and board[i][3] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)

        # Us / The diagonals
        if board[i][1] == board[i][5] == 1 and board[i][9] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][1] == board[i][9] == 1 and board[i][5] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][5] == board[i][9] == 1 and board[i][1] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][3] == board[i][5] == 1 and board[i][7] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][3] == board[i][7] == 1 and board[i][5] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)
        if board[i][5] == board[i][7] == 1 and board[i][3] == 0:
            us += 1
            if i not in us_array:
                us_array.append(i)

        # Them / The rows
        if board[i][1] == board[i][2] == 2 and board[i][3] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][1] == board[i][3] == 2 and board[i][2] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][2] == board[i][3] == 2 and board[i][1] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][4] == board[i][5] == 2 and board[i][6] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][4] == board[i][6] == 2 and board[i][5] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][5] == board[i][6] == 2 and board[i][4] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][7] == board[i][8] == 2 and board[i][9] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][7] == board[i][9] == 2 and board[i][8] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][8] == board[i][9] == 2 and board[i][7] == 0:
            them += 1

        # Them / The columns
        if board[i][1] == board[i][4] == 2 and board[i][7] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][1] == board[i][7] == 2 and board[i][4] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][4] == board[i][7] == 2 and board[i][1] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][2] == board[i][5] == 2 and board[i][8] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][2] == board[i][8] == 2 and board[i][5] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][5] == board[i][8] == 2 and board[i][2] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][3] == board[i][6] == 2 and board[i][9] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][3] == board[i][9] == 2 and board[i][6] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][6] == board[i][9] == 2 and board[i][3] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)

        # Them / The diagonals
        if board[i][1] == board[i][5] == 2 and board[i][9] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][1] == board[i][9] == 2 and board[i][5] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][5] == board[i][9] == 2 and board[i][1] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][3] == board[i][5] == 2 and board[i][7] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][3] == board[i][7] == 2 and board[i][5] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)
        if board[i][5] == board[i][7] == 2 and board[i][3] == 0:
            them += 1
            if i not in them_array:
                them_array.append(i)

    return (us*len(us_array)+2) - them*len(them_array)

########################################################################
########################### End of Heuristic ###########################
########################################################################

# Check if a player wins in a 3x3 board
# Params: board -> board state, boardnum -> 3x3 board position, player -> which player
# Returns: bool if win or not
def checkWin(board,boardnum,player):
    
    if (board[boardnum][1]==board[boardnum][2]==board[boardnum][3]==player or
    board[boardnum][4]==board[boardnum][5]==board[boardnum][6]==player or
    board[boardnum][7]==board[boardnum][8]==board[boardnum][9]==player or
    board[boardnum][1]==board[boardnum][4]==board[boardnum][7]==player or
    board[boardnum][2]==board[boardnum][5]==board[boardnum][8]==player or
    board[boardnum][3]==board[boardnum][6]==board[boardnum][9]==player or
    board[boardnum][1]==board[boardnum][5]==board[boardnum][9]==player or
    board[boardnum][3]==board[boardnum][5]==board[boardnum][7]==player):
        return True
    return False
    
# Place a move in one of the 3x3 boards
def place(board, num, player):
    global num_moves_made
    global depth_limit
    global curr
    curr = num
    boards[board][num] = player
    num_moves_made += 1

    if num_moves_made > 21:
        depth_limit += 2
        num_moves_made = 0

# Read what the server sent us and
# Only parses the strings that are necessary
def parse(string):
    if "(" in string:
        command, args = string.split("(")
        args = args.split(")")[0]
        args = args.split(",")
    else:
        command, args = string, []

    if command == "second_move":
        place(int(args[0]), int(args[1]), 2)
        return play()
    elif command == "third_move":
        # place the move that was generated for us
        place(int(args[0]), int(args[1]), 1)
        # place their last move
        place(curr, int(args[2]), 2)
        return play()
    elif command == "next_move":
        place(curr, int(args[0]), 2)
        return play()
    elif command == "win":
        print("Yay!! We win!! :)")
        return -1
    elif command == "loss":
        print("We lost :(")
        return -1
    return 0

# Connect to socket
def main():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    port = int(sys.argv[2]) # Usage: ./agent.py -p (port)

    s.connect(('localhost', port))
    while True:
        text = s.recv(1024).decode()
        if not text:
            continue
        for line in text.split("\n"):
            response = parse(line)
            if response == -1:
                s.close()
                return
            elif response > 0:
                s.sendall((str(response) + "\n").encode())

if __name__ == "__main__":
    main()