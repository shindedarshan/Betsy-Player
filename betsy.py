#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Oct 19 00:46:59 2018

@author: Darshan
"""

#Data Structure
#board string
import numpy as np
import sys

Inputs = sys.argv

N = int(Inputs[1])
T = int(Inputs[4])
MaxDepth = 7
MaxPlayer = Inputs[2]
BoardString = Inputs[3]

opponent = {'x' : 'o', 'o' : 'x'}
#creates a 2d matrix from the gievn input strin gas a board
def createBoardFromString(board_str, n):
    board = np.array(list(board_str)).reshape(n+3, n)
    return board

#checks whether the given state is the goal state or not
def isGoal(board, player1):
    board = board['board']
    #Diagonals
    if np.count_nonzero(board.diagonal() == player1) == N:
        return True
    if np.count_nonzero(np.flip(board, axis = 1).diagonal() == player1) == N:
        return True
    for i in range(0,N):
        #check for row
        if np.count_nonzero(board[i,:] == player1) == N:
            return True
        #check for column
        if np.count_nonzero(board[0:-3,i] == player1) == N:
            return True

    return False

#successor
def successors(initial_board, player):
    successors = []
    board = initial_board['board']
    for i in range(N):
        empty_spots = np.count_nonzero(board[:,i] == '.')
        #drop
        if empty_spots != 0 and np.count_nonzero(board == player) < N*(N+3)/2:
            board_drop = np.array(board)
            board_drop[empty_spots-1,i] = player
            new_board = {'board': board_drop, 'currentDepth': initial_board['currentDepth'] + 1, \
                         'action': i+1}
            successors.append(new_board)
        #rotate
        if empty_spots != N+3:
            board_rotate = np.array(board)
            board_rotate[empty_spots:,i] = np.roll(board[empty_spots:,i],1)
            if not (board_rotate == board).all():
                new_board = {'board': board_rotate, 'currentDepth': initial_board['currentDepth'] + 1,\
                             'action':-i-1}
                successors.append(new_board)
    return np.array(successors)  
          
def checkInRows(board):
    board_state = board['board']
    favourables = sum(int(np.count_nonzero(board_state[i,:] == MaxPlayer) in range(int((N+1)/2), N)) for i in range(N))
    notfavourables = sum(int(np.count_nonzero(board_state[i,:] == opponent[MaxPlayer]) in range(int((N+1)/2), N)) for i in range(N))
    return favourables - notfavourables

def checkInColumns(board):
    board_state = board['board']
    favourables = sum(int(np.count_nonzero(board_state[:,i] == MaxPlayer) in range(int((N+4)/2), N)) for i in range(N))
    notfavourables = sum(int(np.count_nonzero(board_state[:,i] == opponent[MaxPlayer]) in range(int((N+4)/2), N)) for i in range(N))
    return favourables - notfavourables

def checkInDiagonals(board):
    board_state = board['board']
    favourables = np.count_nonzero(board_state.diagonal() == MaxPlayer) + \
                      np.count_nonzero(np.flip(board_state, axis = 1).diagonal() == MaxPlayer)
    notfavourables = np.count_nonzero(board_state.diagonal() == opponent[MaxPlayer]) + \
                      np.count_nonzero(np.flip(board_state, axis = 1).diagonal() == opponent[MaxPlayer])
    return favourables - notfavourables

def countConsecutiveColumnElements(current_board):
    maxCountSelf = 0
    maxCountOpp = 0
    for i in range(N):
        countSelf = 0
        countOpp = 0
        for e in list(current_board['board'][:,i])*2:
            #count for Max
            if e == MaxPlayer:
                countSelf += 1
                countOpp = 0
            #count for Min
            if e == opponent[MaxPlayer]:
                countSelf = 0
                countOpp += 1
            if countSelf > maxCountSelf:
                maxCountSelf = countSelf
            if countOpp > maxCountOpp:
                maxCountOpp = countOpp
    if maxCountOpp >= N:
        maxCountOpp = 3*maxCountOpp
    if maxCountSelf >= N:
        maxCountSelf = 2*maxCountSelf
    return maxCountSelf - maxCountOpp

def available_pos(curr_board):
    player = MaxPlayer
    count_player = 0
    count_opp = 0
    board = curr_board['board']
    for i in range (N):
        #Row
        if np.count_nonzero(board[i,:] == opponent[player]) == 0:
            count_player += 1
        #Row for opponent
        if np.count_nonzero(board[i,:] == player) == 0:
            count_opp += 1
        #Column
        if np.count_nonzero(board[0:-3,i] == opponent[player]) == 0:
            count_player += 1
        #Column for opponent
        if np.count_nonzero(board[0:-3,i] == player) == 0:
            count_opp += 1
    #Diagonals
    if np.count_nonzero(board.diagonal() == opponent[player]) == 0:
        count_player += 1
    if np.count_nonzero(np.flip(board, axis = 1).diagonal() == opponent[player]) == 0:
        count_player += 1
    #Diagonals for opponent
    if np.count_nonzero(board.diagonal() == player) == 0:
        count_opp += 1
    if np.count_nonzero(np.flip(board, axis = 1).diagonal() == player) == 0:
        count_opp += 1
    return count_player - count_opp
    #return available_row_col(board, player) + available_diag(board, player) #+ available_col(board, player) 

def distancetoCompleteRow(curr_board, player):
    board = curr_board['board']
    min_distance = sys.maxsize
    for i in range(N):
        index_sum = 0
        if '.' in board[i,:]:
            index_sum = sys.maxsize
            continue
        for j in range(N):
            empty_spots = np.count_nonzero(board[:,j] == ".")
            column = list(board[:,j])[i+1:] + list(board[:,j])[empty_spots:i+1]
            if player in column:
                index_sum += column[::-1].index(player)
        if index_sum < min_distance:
            min_distance = index_sum
    if min_distance == sys.maxsize:
        return 0
    return min_distance

def distancetoGoalColumn(curr_board, player):
    board = curr_board['board']
    min_distance = sys.maxsize
    
    for i in range(N):
        distance = sys.maxsize
        ctr = 0
        countPlayer = 0
        end_index = 0
        maxCountPlayer = 0
        for e in list(board[:,i])*2:
            ctr += 1
            if e == player:
                countPlayer += 1
            else:
                countPlayer = 0
            if countPlayer > maxCountPlayer:
                maxCountPlayer = countPlayer
                end_index = ctr
        if maxCountPlayer >= N:
            end_index %= N+3
            if end_index <= N:
                distance = N - end_index
            else:
                distance = N+3+N - end_index
        if distance < min_distance:
            min_distance = distance
    if min_distance == sys.maxsize:
        return 0
    return min_distance


#This is the evaluation function which returns the value of the leaf node.
#If it is a goal state then the value will be the maximum else it will be some heuristic
def leafValue(board, currentPlayer):
    isGoalForMax = isGoal(board, MaxPlayer)
    isGoalForMin = isGoal(board, opponent[MaxPlayer])
    if currentPlayer == MaxPlayer:
        if isGoalForMax:#check first for MAX player win 
            return 2 * (N*(N+3) / board['currentDepth'])
        if isGoalForMin:
            return -2 * (N*(N+3) / board['currentDepth'])
    else:
        if isGoalForMin:#check first for MIN player win 
            return -2 * (N*(N+3) / board['currentDepth'])
        if isGoalForMax:
            return 2 * (N*(N+3) / board['currentDepth'])
    
    row_opp = distancetoCompleteRow(board, opponent[MaxPlayer])
    row_Max = distancetoCompleteRow(board, MaxPlayer)
    favourableRows = 0 
    if row_opp == 0:
        favourableRows = row_Max
    elif row_Max == 0:
        favourableRows = -row_opp
    else:
        favourableRows = row_opp - row_Max
    
    col_opp = distancetoGoalColumn(board, opponent[MaxPlayer])
    col_Max = distancetoGoalColumn(board, MaxPlayer)
    favourableColumns = 0
    if col_opp == 0:
        favourableColumns = col_Max
    elif col_Max == 0:
        favourableColumns = -col_opp
    else:
        favourableColumns = col_opp - col_Max
                     
    h_value = available_pos(board) + \
               countConsecutiveColumnElements(board) + \
               favourableRows + favourableColumns
    h_value = h_value / (N*board['currentDepth'])

    return h_value

def isLeafNode(board):
    if isGoal(board, 'o') or isGoal(board, 'x'):
        return True
    if board['currentDepth'] == MaxDepth:
       return True
    return False

def MAXValue(board, alpha, beta, player):
    if isLeafNode(board):
        return leafValue(board, player)
    for succ in successors(board, opponent[player]):
        alpha = max(alpha, MINValue(succ, alpha, beta, opponent[player]))
        if alpha >= beta:
            return alpha
    return alpha
    
def MINValue(board, alpha, beta, player):
    if isLeafNode(board):
        return leafValue(board, player)
    for succ in successors(board, opponent[player]):
        beta = min(beta, MAXValue(succ, alpha, beta, opponent[player]))
        if alpha >= beta:
            return beta
    return beta

def AlphaBetaDecision(board):
    #return a move that leads to the board corresponding to the maximum of the 
    #minimum values of the min successors
    alpha = -sys.maxsize
    beta = sys.maxsize
    board['currentDepth'] = 0
    bestmove = []
    for succ in successors(board, MaxPlayer):
        current_value = MINValue(succ, alpha, beta, MaxPlayer)
        if current_value > alpha:
            alpha = current_value
            bestmove = succ
    return bestmove

initial_board = {'board' : createBoardFromString(BoardString, N),
                 'currentDepth' : 0, 'action' : 0}  

#Run IDS for finding the next best move
for i in range(50):
    MaxDepth = i+2
    nextmove = AlphaBetaDecision(initial_board)
    print(str(nextmove['action']) + " " + ''.join(list(nextmove['board'].flatten())))

def play(board, firstPlayer):
    global MaxPlayer
    while (True):
        MaxPlayer = firstPlayer
        board = AlphaBetaDecision(board)
        print("Player : " + MaxPlayer + " Move : " + str(board['action']))
        print(board['board'])
        if isGoal(board, MaxPlayer):
            break
        MaxPlayer = opponent[firstPlayer]
        board = AlphaBetaDecision(board)
        print("Player : " + MaxPlayer + " Move : " + str(board['action']))
        print(board['board'])
        if isGoal(board, MaxPlayer):
            break

def performAction(CurrentBoard, action, player):
    board = CurrentBoard['board']
    
    #drop action
    if action > 0:
        empty_spots = np.count_nonzero(board[:,action-1] == ".")
        board_drop = np.array(board)
        board_drop[empty_spots-1,action-1] = player
        new_board = {'board': board_drop, 'currentDepth': CurrentBoard['currentDepth'] + 1, \
                         'action' : action}
        return new_board
    
    #rotate action
    if action < 0:
        action = abs(action)-1
        empty_spots = np.count_nonzero(board[:,action] == ".")
        board_rotate = np.array(board)
        board_rotate[empty_spots:,action] = np.roll(board[empty_spots:,action],1)
        new_board = {'board': board_rotate, 'currentDepth': CurrentBoard['currentDepth'] + 1,\
                     'action' : -1*(action+1)}
        return new_board 

def playAgainstHuman(board, firstPlayer):
    global MaxPlayer
    while (True):
        MaxPlayer = firstPlayer
        board = AlphaBetaDecision(board)
        print("Player : " + MaxPlayer + " Move : " + str(board['action']))
        print(board['board'])
        if isGoal(board, MaxPlayer):
            break
        
        MaxPlayer = opponent[firstPlayer]
        action = int(input("Enter action: "))
        board = performAction(board,action, MaxPlayer)
        #board = AlphaBetaDecision(board)
        print("Player : " + MaxPlayer + " Move : " + str(board['action']))
        print(board['board'])
        if isGoal(board, MaxPlayer):
            break
        
