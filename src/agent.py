#!/usr/bin/python3
# Sample starter bot by Zac Partridge
# Contact me at z.partridge@unsw.edu.au
# 06/04/19
# Feel free to use this and modify it however you wish
import copy
import socket
import sys
import numpy as np
import random

###### For Daniel:
# i think the minimax function is correct or somewhat working
# our heuristic is rlly bad.... TODO: Better heuristic 
# I think maybe our isTerminal is incorrect....
# maybe isterminal can take in a board, and check if its done...?
# Defs need to fix heuristic first to know if isterminal is bad


# a board cell can hold:
#   0 - Empty
#   1 - I played here
#   2 - They played here

# the boards are of size 10 because index 0 isn't used
boards = np.zeros((10, 10), dtype="int8")
s = [".","X","O"]
curr = 0 # this is the current board to play in

depth_limit = 5 # Max depth iterate too


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
# Note that moveTile is the next board the move needs to be played on
# curr_move is where the move was played on current board

def alphabeta(board):
    global curr
    global depth_limit
    depth = 0
    # Set up alpha and beta

    alpha = -float('inf')
    beta = float('inf')

    children = genChildren(board, curr, 1)
    depth += 1
    nextMove = 0
    for moveTile, child in children.items():
        eval = calc_min(child, moveTile, alpha, beta, depth, curr)
        print ("Move Tile is:", moveTile)
        print ("Evaluation is:", eval)
        if eval > alpha:
            alpha = eval
            nextMove = moveTile

    print ("whats my next move?", nextMove, " in board ", curr)
    return nextMove # this returns the next move to make

def calc_min(board, move, alpha, beta, depth, curr_move):
    global depth_limit

    if checkWin(board, curr_move, 1):
        return float('inf')

    if depth >= depth_limit:
        #return getHeuristic(board, curr_move, move, 1)
        return calc_h(board, move, 1)

    children = genChildren(board, move, 2)
    depth += 1
    for moveTile, child in children.items():
        eval = calc_max(child, moveTile, alpha, beta, depth, move)
        beta = min(beta, eval)
        if beta <= alpha:
            break
        
    return beta

def calc_max(board, move, alpha, beta, depth, curr_move):
    global depth_limit

    if checkWin(board, curr_move, 2):
        return -float('inf')

    if depth >= depth_limit:
        #return getHeuristic(board, curr_move, move, 2)
        return calc_h(board, move, 2)

    children = genChildren(board, move, 1)
    depth += 1
    for moveTile, child in children.items():
        eval = calc_min(child, moveTile, alpha, beta, depth, move)
        alpha = max(alpha, eval)
        if beta <= alpha:
            break      
    return alpha

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

def play2():
    global boards
    print_board(boards)
    possible = []

    for i in range(1,10):
        if boards[curr][i] == 0:
            nextMove = copy.deepcopy(boards)
            nextMove[curr][i] = 1
            if checkWin(nextMove, curr, 1):
                print ("winning move yeet")
                return i
            else:
                children = genChildren(nextMove, i, 2)
                for j in children.values():
                    if checkWin(j, i, 2):
                        continue
                    else:
                        possible.append(i)

    moveToMake = alphabeta(boards)
    if moveToMake not in possible and possible:
        print ("all the possible", possible)
        place(curr, possible[0], 1)
        return possible[0]
    else:
        place(curr, moveToMake, 1)
        return moveToMake

### End of Alpha Beta Stuff ###

def chooseMove():
    global boards
    possible = []

    for i in range(1,10):
        if boards[curr][i] == 0:
            yes = getHeuristic(boards,curr,i)
            print(yes, " is heuristic")
            nextMove = boards.copy()
            nextMove[curr][i] = 1 
            if checkWin(nextMove,curr,1):
                print("winning move yeet")
                win = []
                win.append(i)
                return win
            else:
                # Check other person doesn't win next move
                children = genChildren(nextMove, i, 2)
                for j in children:
                    if checkWin(j,i, 2):
                        continue
                    else:
                        possible.append(i)
    return possible
def countMoves(board,boardnum,player):
    scores = [0,0]
    for i in range(1,10):
        if board[boardnum][i] == player:
            scores[0] += 1
        elif board[boardnum][i] == 0:
            continue
        else:
            scores[1] += 1
    return 2*scores[0]/scores[1] if scores[1] else 0
### NEW HEURISTIC?? Tries to add up everytime ###
def calc_h(board, currboard, player):
    us = 0 # we are player 1
    us_array = []
    them = 0 # they are player 2
    them_array = []
    for i in range(1,10):
        # the rows
        weight = countMoves(board,i,player)
        if board[i][1] == board[i][2] == 1 and board[i][3] == 0:
            us += 1 * weight
        if board[i][1] == board[i][3] == 1 and board[i][2] == 0:
            us += 1 * weight
        if board[i][2] == board[i][3] == 1 and board[i][1] == 0:
            us += 1 * weight
        if board[i][4] == board[i][5] == 1 and board[i][6] == 0:
            us += 1 * weight
        if board[i][4] == board[i][6] == 1 and board[i][5] == 0:
            us += 1 * weight
        if board[i][5] == board[i][6] == 1 and board[i][4] == 0:
            us += 1 * weight
        if board[i][7] == board[i][8] == 1 and board[i][9] == 0:
            us += 1 * weight
        if board[i][7] == board[i][9] == 1 and board[i][8] == 0:
            us += 1 * weight
        if board[i][8] == board[i][9] == 1 and board[i][7] == 0:
            us += 1 * weight

        # the cols
        if board[i][1] == board[i][4] == 1 and board[i][7] == 0:
            us += 1 * weight
        if board[i][1] == board[i][7] == 1 and board[i][4] == 0:
            us += 1 * weight
        if board[i][4] == board[i][7] == 1 and board[i][1] == 0:
            us += 1 * weight
        if board[i][2] == board[i][5] == 1 and board[i][8] == 0:
            us += 1 * weight
        if board[i][2] == board[i][8] == 1 and board[i][5] == 0:
            us += 1 * weight
        if board[i][5] == board[i][8] == 1 and board[i][2] == 0:
            us += 1 * weight
        if board[i][3] == board[i][6] == 1 and board[i][9] == 0:
            us += 1 * weight
        if board[i][3] == board[i][9] == 1 and board[i][6] == 0:
            us += 1 * weight
        if board[i][6] == board[i][9] == 1 and board[i][3] == 0:
            us += 1 * weight

        # diagonals
        if board[i][1] == board[i][5] == 1 and board[i][9] == 0:
            us += 1 * weight
        if board[i][1] == board[i][9] == 1 and board[i][5] == 0:
            us += 1 * weight
        if board[i][5] == board[i][9] == 1 and board[i][1] == 0:
            us += 1 * weight
        if board[i][3] == board[i][5] == 1 and board[i][7] == 0:
            us += 1 * weight
        if board[i][3] == board[i][7] == 1 and board[i][5] == 0:
            us += 1 * weight
        if board[i][5] == board[i][7] == 1 and board[i][3] == 0:
            us += 1 * weight



        # the rows for them
        if board[i][1] == board[i][2] == 2 and board[i][3] == 0:
            them += 1
        if board[i][1] == board[i][3] == 2 and board[i][2] == 0:
            them += 1
        if board[i][2] == board[i][3] == 2 and board[i][1] == 0:
            them += 1
        if board[i][4] == board[i][5] == 2 and board[i][6] == 0:
            them += 1
        if board[i][4] == board[i][6] == 2 and board[i][5] == 0:
            them += 1
        if board[i][5] == board[i][6] == 2 and board[i][4] == 0:
            them += 1
        if board[i][7] == board[i][8] == 2 and board[i][9] == 0:
            them += 1
        if board[i][7] == board[i][9] == 2 and board[i][8] == 0:
            them += 1
        if board[i][8] == board[i][9] == 2 and board[i][7] == 0:
            them += 1

        # the cols
        if board[i][1] == board[i][4] == 2 and board[i][7] == 0:
            them += 1
        if board[i][1] == board[i][7] == 2 and board[i][4] == 0:
            them += 1
        if board[i][4] == board[i][7] == 2 and board[i][1] == 0:
            them += 1
        if board[i][2] == board[i][5] == 2 and board[i][8] == 0:
            them += 1
        if board[i][2] == board[i][8] == 2 and board[i][5] == 0:
            them += 1
        if board[i][5] == board[i][8] == 2 and board[i][2] == 0:
            them += 1
        if board[i][3] == board[i][6] == 2 and board[i][9] == 0:
            them += 1
        if board[i][3] == board[i][9] == 2 and board[i][6] == 0:
            them += 1
        if board[i][6] == board[i][9] == 2 and board[i][3] == 0:
            them += 1

        # diagonals
        if board[i][1] == board[i][5] == 2 and board[i][9] == 0:
            them += 1
        if board[i][1] == board[i][9] == 2 and board[i][5] == 0:
            them += 1
        if board[i][5] == board[i][9] == 2 and board[i][1] == 0:
            them += 1
        if board[i][3] == board[i][5] == 2 and board[i][7] == 0:
            them += 1
        if board[i][3] == board[i][7] == 2 and board[i][5] == 0:
            them += 1
        if board[i][5] == board[i][7] == 2 and board[i][3] == 0:
            them += 1
    
    
    if player == 1:
        return us + 1 - them
    else:
        return them - us - 1

#get a heuristic for a board
#board is the board we are using
#current is the current board in board
#move is the selected move to make
def getHeuristic(board, prev_board, boardnum, player):    
    #if this is winning move
    scoreUs = 0
    scoreThem = 0
    if player == 1:
        for i in range(1,10):        
            scoreUs += rowColHeuristic(board,i,1)
            scoreThem += rowColHeuristic(board,i,2)

    else:
        for i in range(1,10):
            scoreUs += rowColHeuristic(board,i,2)
            scoreThem += rowColHeuristic(board,i,1)     

    print ("our board is ", scoreUs, " their ", scoreThem, " in boards ", prev_board, " and ", boardnum)
    
    
    
    
    
    return scoreUs - 1.2*scoreThem

def rowColHeuristic(board,boardnum,player):

    score = 0
    #if calculating heuristic for opponent, then we are the opponent from their perspective
    if player == 2:
        opp = 1
    else:
        opp = 2
        
    #if we win, move is good    
    if checkWin(board,boardnum,player):
        return float('inf')
    elif checkWin(board, boardnum, opp):
        return -float('inf')
    elif checkDraw(board,boardnum): #if move results in draw
        return 0
    
    
    #checking each row for x1 and x2 horizontally for each player
    adjacent=[0,0] #x2 array for both players 0 is player 1 is opponent
    single=[0,0] #x1 array for both players
    for j in range(1,3):
        for i in ([1,4,7]):  #for each row
            if board[boardnum][i] == j == board[boardnum][i+1] and board[boardnum][i+2] == 0: #check for X|X|0 
                adjacent[j-1] += 10
            elif board[boardnum][i] == j and board[boardnum][i+2] == 0 == board[boardnum][i+1]: #check for X|0|0
                single[j-1] +=1
            elif board[boardnum][i+1] == j == board[boardnum][i+2] and  board[boardnum][i] == 0:    #check for 0|X|X
                adjacent[j-1] += 10
            elif board[boardnum][i+1] == j and board[boardnum][i] == 0 == board[boardnum][i+2]:    #if the row is 0|X|0
                single[j-1] += 1
            elif board[boardnum][i+2] == j and board[boardnum][i] == 0 == board[boardnum][i+1]:  #if row is 0|0|X 
                single[j-1] += 1            
            elif board[boardnum][i] == j == board[boardnum][i+2] and board[boardnum][i+1] == 0: # if X|0|X
                adjacent[j-1] += 10
        #columns       
        for i in ([1,2,3]):  #for each column
            if board[boardnum][i] == j == board[boardnum][i+3] and board[boardnum][i+6] == 0: #check for X|X|0 (in columns)
                adjacent[j-1] += 10
            elif board[boardnum][i] == j and board[boardnum][i+3] == 0 == board[boardnum][i+6]: #check for X|0|0
                single[j-1] +=1
            elif board[boardnum][i+3] == j == board[boardnum][i+6] and board[boardnum][i] == 0:    #check for 0|X|X
                adjacent[j-1] +=10
            elif board[boardnum][i+3] == j and board[boardnum][i] == 0 == board[boardnum][i+6]:    #if is 0|X|0
                single[j-1] += 1
            elif board[boardnum][i+6] == j and board[boardnum][i] == 0 == board[boardnum][i+3]:  #if is 0|0|X     
                single[j-1] += 1  
            elif board[boardnum][i] == j == board[boardnum][i+6] and board[boardnum][i+3] == 0: # if X|0|X
                adjacent[j-1] += 10
    #diagonals
        if board[boardnum][1] == j == board[boardnum][5] and board[boardnum][9] == 0:
            adjacent[j-1] += 10
        elif board[boardnum][1] == j == board[boardnum][9] and board[boardnum][5] == 0:
            adjacent[j-1] += 10
        elif board[boardnum][1] == j and board[boardnum][5] == 0 == board[boardnum][9]:
            single[j-1] += 1
        elif board[boardnum][1] == 0 and board[boardnum][5] == j == board[boardnum][9]:
            adjacent[j-1] += 10
        elif board[boardnum][1] == 0 == board[boardnum][9] and board[boardnum][5] == j:
            single[j-1] += 1
        elif board[boardnum][1] == 0 == board[boardnum][5] and board[boardnum][9] == j:
            single[j-1] += 1
        if board[boardnum][3] == j == board[boardnum][5] and board[boardnum][7] == 0:
            adjacent[j-1] += 10
        elif board[boardnum][3] == j == board[boardnum][7] and board[boardnum][5] == 0:
            adjacent[j-1] += 10
        elif board[boardnum][3] == j and board[boardnum][5] == 0 == board[boardnum][7]:
            single[j-1] += 1
        elif board[boardnum][3] == 0 and board[boardnum][5] == j == board[boardnum][7]:
            adjacent[j-1] += 10
        elif board[boardnum][3] == 0 == board[boardnum][7] and board[boardnum][5] == j:
            single[j-1] += 1
        elif board[boardnum][3] == 0 == board[boardnum][5] and board[boardnum][7] == j:
            single[j-1] += 1
                
    #score += 3*adjacent[0] + single[0] - (3*adjacent[1]+single[1])

    if player == 2:
        score += ((1.2*adjacent[1]) + single[1] - adjacent[0] + single[0])
    else:
        score += (adjacent[0] + single[0] - adjacent[1] + single[1])

    return score


        
def getHeuristic2(board, prev_board, boardnum):
    us = 0
    them = 0
    neutral = 0
    for i in range(1,10):
        if board[boardnum][i] == 0:
            neutral += 1
        elif board[boardnum][i] == 1:
            us += 1
        elif board[boardnum][i] == 2:
            them += 1
    return 2*us - 3*them + neutral


        
#check if board is a draw    
def checkDraw(board,boardnum):
    if not checkWin(board,boardnum,1) and not checkWin(board,boardnum,2):
        for i in range(1,10):
            if board[boardnum][i] == 0:
                return False         
    return True       
    
#check win in one of the boards for a certain player
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
   
#generate all children for a board
def genChildren(board, boardnum, player):
    # dictionary instead board -> move played
    children = {}
    for i in range(1,10):
        if board[boardnum][i] == 0:
            child = copy.deepcopy(board)
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