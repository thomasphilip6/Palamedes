import numpy as np
from numpy import asarray
import cv2
from PIL import Image
#from diffCheck import checkRessemblance, buildROI, checkEveryCell
from diffCheck import *
from calibration import calibration, findCell, spotCell
from skimage.metrics import structural_similarity
from ChessEngine import startGame, restartGame, getWinMove, updateEngineBoard



from sentence_transformers import SentenceTransformer, util

import glob
import os
import time   

import pickle


def start():


    global my_Color
    global op_Color
    my_Color = 2 #We'll have to be careful with that 
    # 1=white and 2=black
    #and we'll do 0 = empty
    if my_Color == 1:
        op_Color = 2
    else:
        op_Color = 1

    global board
    board =np.zeros((64,2),dtype=int)
    #64 cells with 2 infos in each: color + type
    global letters 
    letters=["A","B","C","D","E","F","G","H"]   
    numbers=["1","2","3","4","5","6","7","8"]

    #the global board with the letters to easily translate names to index
    global cells
    cells=[]
    for letter in letters:
        for number in numbers:
            cells.append(letter + number)


    z=0
    for j in range(1,9):
        board [z][0] = op_Color
        board [z][1] = j
        z+=1
        board [z][0] = op_Color
        board [z][1] = j+8
        z+=5 #they are already 0 everywhere no need to fill them again
        board [z][0] = my_Color 
        board [z][1] = j+8
        z+=1
        board [z][0] = my_Color 
        board [z][1] = j
        z+=1
"""
little reminder
8/1 = rock
2/7 = knight
3/6 = bishop
4 = queen
5 = king 
9 to 16 = pawn 
"""
def printTheBoard():
    print("      ", end="")
    for z in range (1,9):
        print(z,"     ", end="")
    print("\r")
    cnt=0
    let=0
    for i in range (0,64):
        if cnt==0:
            print(letters[let], " ",end="")
            let+=1
        cnt+=1
        if i==1 or i==6:
            print("[",board[i][0], "",board[i][1], "]", end="")
        else:
            print("[",board[i][0], board[i][1], "]", end="")
        if cnt == 8:
            cnt=0
            print("\r")


def readMove(p1, p2):
    #I've got 3 infos : previous position, new position or empty 

    if board[p1][0]==0:
        #this cell was previously empty so this is now the position of the opponent
        newCell=p1
        isNowEmpty=p2
        pieceMoved=board[p2]
        wasEaten=0
    elif board[p1][0]==my_Color:
        #means that he just ate my piece
        newCell=p1
        isNowEmpty=p2
        pieceMoved=board[p2]
        wasEaten=board[p1]
    else:
        newCell=p2
        isNowEmpty=p1
        pieceMoved=board[p1]
        if board[p2][0]==0:
            wasEaten=0
        else:
            wasEaten=board[p2]

    #now we make the changes to the game
    board[newCell]=pieceMoved
    board[isNowEmpty]=[0][0] 
    return isNowEmpty,newCell
        
def writeMove(p1,p2):
    newCell=p2
    isNowEmpty=p1
    pieceMoved=board[p1]
    if board[p2][0]==op_Color:
        wasEaten=board[p2]
        #eatHim()#we would need a way to specify to the robot that he needs to first eat the 
    else:
        wasEaten=0
        
    board[newCell]=pieceMoved
    board[isNowEmpty]=[0][0]    

def translateCellToIndex(diffArray):
    p1 = cells.index(str(diffArray[0]))
    p2 = cells.index(str(diffArray[1]))
    return p1, p2


"""
#we'll need that later on
global firstTime
firstTime = True

def getDiffCheck():

    differences=[]
    if firstTime:
        #fill with the appropriate image name
        board='empty.jpeg'
        #load images
        boardWitness=np.array(Image.open('empty.jpeg').resize((400,400)))
        image0=np.array(Image.open('position0.jpg').resize((400,400)))
        image1=np.array(Image.open('position1.jpg').resize((400,400)))
        #faire la calibration une seule fois :
        coordinates, cells = calibration(board)
        move1=imageDifference(coordinates,cells,board,boardWitness,image0,image1)
        # from now on coordinates and cells are accessible with move1.cells and move1.coordinates
        move1.load()
        differences = move1.checkEveryCell()
        firstTime=False

    else:
        #create object here
        differences = object.checkEveryCell()

    return differences
"""
def prep():
    #fill with the appropriate image name
    emptyBoard='data\empty.jpg'
    #load images
    boardWitness=np.array(Image.open('data\empty.jpg').resize((400,400)))
    image0=np.array(Image.open('data\position0.jpg').resize((400,400)))
    image1=np.array(Image.open('data\position1.jpg').resize((400,400)))
    #faire la calibration une seule fois :
    coordinates, cells = calibration(emptyBoard)
    global move1
    move1=imageDifference(coordinates,cells,emptyBoard,boardWitness,image0,image1)
    # from now on coordinates and cells are accessible with move1.cells and move1.coordinates
    move1.load()


def mainMovesDiff():
    #to update the player move
    diffCells=move1.checkEveryCell()
    #cell1=diffCells[0]
    #cell2=diffCells[1]
    print("the 2 cells diff:")
    print(diffCells)
    p1,p2 = translateCellToIndex(diffCells)
    #this whole part only consider the perfect result with two differences no more no less
    #so we'll make sure everything works properly before those line   
    startMove, endMove = readMove(p1, p2)#update moves
    startCell=cells[startMove]
    endCell=cells[endMove]
    print("startCell & endCells",startCell,endCell  )
    updateEngineBoard(startCell, endCell)#update engine
    #this line is wrong find the mistake

def mainMovesApi():#movesAPI would need to be an array with the 2 mocements cells
    #startPos,endPos = translateCellToIndex()
    #with this configuration I would need in [0] the start and in [1] the end of my movements
    startPos,endPos = getWinMove()#getmove from engine and update engine
    
    st = cells.index(startPos)
    end = cells.index(endPos)
    writeMove(st, end)#update moves
    printTheBoard()

def getBoard():
    return board

def tell_move_to_move(round):

    if round==0:#no switch case in python sorry
        start()#start the moves.py board 
        prep()#start the diff check and calibration
        startGame()#Start the chess engine and stockfish the API

    elif round==1: 
        #the player first because he plays white so diff check first
        mainMovesDiff()
        printTheBoard()
    elif round==2: 
        #newMoves=["A2","A4"]
        mainMovesApi()
    else:
        print("we're out of the round")
    """
    elif round==3: 
        newMoves=["C7","C4"]
        mainMovesDiff(newMoves)
    elif round ==4:
        newMoves=["E2","D3"]
        mainMovesApi(newMoves)
    """ 
    










#start() #start the board

### Proff of concept ### 
"""
#fill with the appropriate image name
board='data\empty.jpeg'
#load images
boardWitness=np.array(Image.open('data\empty.jpeg').resize((400,400)))
image0=np.array(Image.open('data\position0.jpg').resize((400,400)))
image1=np.array(Image.open('data\position1.jpg').resize((400,400)))
#faire la calibration une seule fois :
coordinates, cells = calibration(board)
move1=imageDifference(coordinates,cells,board,boardWitness,image0,image1)
# from now on coordinates and cells are accessible with move1.cells and move1.coordinates
move1.load()
"""


#printTheBoard() #if needed to see if we started well


###########
#begining of the main code
"""

diffArray = checkEveryCell(image0,image1)
p1,p2 = translateCellToIndex(diffArray)
#this whole part only consider the perfect result with two differences no more no less
#so we'll make sure everything works properly before those line   

#now I would need to import the 2 squares that had movents on the picture differentiation
#function to find the movemnt and who moved
readMove(p1,p2)
print("That's after 1 move:")
printTheBoard()

#now we need to update or board regarding what the API want's to play 
startPos =0
endPos = 5
writeMove(startPos, endPos)
print("After I mad my deadly move...")
printTheBoard()
"""

#start() to run with the interface
