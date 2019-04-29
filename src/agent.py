#!/usr/bin/python3
# Sample starter bot by Zac Partridge
# Contact me at z.partridge@unsw.edu.au
# 06/04/19
# Feel free to use this and modify it however you wish

import socket
import sys
import numpy as np

# a board cell can hold:
#   0 - Empty
#   1 - I played here
#   2 - They played here

# the boards are of size 10 because index 0 isn't used
boards = np.zeros((10, 10), dtype="int8")
s = [".","X","O"]
curr = 0 # this is the current board to play in
depth_limit = 4 # Max depth iterate too
curr_depth = 0 # Curr depth

# print a row
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

### Alpha Beta stuff ###
def alphabeta(board):
    global curr_depth
    global curr
    # Set up alpha and beta
    alpha = -float('inf')
    beta = float('inf')

    children = genChildren(board, curr, 1)
    curr_depth += 1
    nextMove = 0
    for moveTile, child in children.items():
        eval = calc_min(child, moveTile, alpha, beta)
        print ("Move Tile is:", moveTile)
        print ("Evaluation is:", eval)
        if eval > alpha:
            alpha = eval
            nextMove = moveTile
    print ("whats my next move?", nextMove)
    return nextMove # this returns the next move to make

def calc_min(board, move, alpha, beta):
    global curr_depth

    if isTerminal():
        return getHeuristic()

    min_val = float('inf')
    children = genChildren(board, move, 2)
    curr_depth += 1
    for moveTile, child in children.items():
        eval = calc_max(child, moveTile, alpha, beta)
        min_val = min(min_val, eval)
        beta = min(beta, eval)
        if beta <= alpha:
            break

    return min_val

def calc_max(board, move, alpha, beta):
    global curr_depth

    if isTerminal():
        return getHeuristic()

    max_val = -float('inf')
    children = genChildren(board, move, 1)
    curr_depth += 1
    for moveTile, child in children.items():
        eval = calc_min(child, moveTile, alpha, beta)
        max_val = max(max_val, eval)
        alpha = max(alpha, eval)
        if beta <= alpha:
            break

    return max_val

def isTerminal():
    global max_depth
    global curr_depth
    if (curr_depth >= depth_limit):
        curr_depth = 0
        return True
    return False

def getHeuristic():
    return np.random.randint(1,9)

def play():
    print_board(boards)
    moveToMake = alphabeta(boards)
    if moveToMake == 0:
        for i in range (1,10):
            if boards[curr][i] == 0:
                place(curr, i, 1)
                return i

    place(curr, moveToMake, 1)
    return moveToMake

### End of Alpha Beta Stuff ###

def chooseMove():
    possible = []
    global boards
    for i in range(1,10):
        if boards[curr][i] == 0:
            nextMove = boards.copy()
            nextMove[curr][i] = 1 
            if checkWin(nextMove,1):
                print("winning move yeet")
                win = []
                win.append(i)
                return win
            else:
                # Check other person doesn't win next move
                children = genChildren(nextMove, i, 2)
                for j in children.values():
                    if checkWin(j, 2):
                        continue
                    else:
                        possible.append(i)
    print (possible,curr)
    return possible
   
def checkWin(current,player):

    if (current[curr][1]==current[curr][2]==current[curr][3]==player or
    current[curr][4]==current[curr][5]==current[curr][6]==player or
    current[curr][7]==current[curr][8]==current[curr][9]==player or
    current[curr][1]==current[curr][4]==current[curr][7]==player or
    current[curr][2]==current[curr][5]==current[curr][8]==player or
    current[curr][3]==current[curr][6]==current[curr][9]==player or
    current[curr][1]==current[curr][5]==current[curr][9]==player or
    current[curr][3]==current[curr][5]==current[curr][7]==player):
        return True
    return False
   
#generate all children for a board
def genChildren(board, boardnum, player):
    # dictionary instead board -> move played
    children = {}
    for i in range(1,10):
        if board[boardnum][i] == 0:
            child = board[:]
            child[boardnum][i] = player
            children[i] = child
    return children
   
# choose a move to play
def play2():
    print_board(boards)
    goodMoves = chooseMove()
    if (len(goodMoves)== 1):
        n = np.bincount(goodMoves).argmax()
    elif (len(goodMoves)!= 0):
        n = np.bincount(goodMoves).argmax()
    # just play a random move for now
    else: 
        n = np.random.randint(1,9)
        while boards[curr][n] != 0:
            n = np.random.randint(1,9)

    # print("playing", n)
    
    place(curr, n, 1)
    return n

# place a move in the global boards
def place(board, num, player):
    global curr
    curr = num
    boards[board][num] = player

# read what the server sent us and
# only parses the strings that are necessary
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

# connect to socket
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