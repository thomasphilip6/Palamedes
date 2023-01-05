import numpy as np
from numpy import asarray
import cv2
from PIL import Image
from diffCheck import checkRessemblance, buildROI, checkEveryCell
from calibration import calibration, findCell, spotCell
from skimage.metrics import structural_similarity

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
        board [z][0] = my_Color
        board [z][1] = j
        z+=1
        board [z][0] = my_Color
        board [z][1] = j+8
        z+=5 #they are already 0 everywhere no need to fill them again
        board [z][0] = op_Color 
        board [z][1] = j+8
        z+=1
        board [z][0] = op_Color 
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
        
def writeMove(p1,p2):
    newCell=p2
    isNowEmpty=p1
    pieceMoved=board[p1]
    if board[p2][0]==op_Color:
        wasEaten=board[p2]
        """eatHim()"""#we would need a way to specify to the robot that he needs to first eat the little guy
    else:
        wasEaten=0
        
    board[newCell]=pieceMoved
    board[isNowEmpty]=[0][0]    

def translateCellToIndex(diffArray):
    p1 = cells.index(str(diffArray[0]))
    p2 = cells.index(str(diffArray[1]))
    return p1, p2


def mainMovesDiff(diffArray):
    p1,p2 = translateCellToIndex(diffArray)
    #this whole part only consider the perfect result with two differences no more no less
    #so we'll make sure everything works properly before those line   
    readMove(p1, p2)

def mainMovesApi(movesApi):#movesAPI would need to be an array with the 2 mocements cells
    startPos,endPos = translateCellToIndex(movesApi)
    #with this configuration I would need in [0] the start and in [1] the end of my movements
    writeMove(startPos, endPos)

def getBoard():
    return board

def tell_move_to_move(round):
    print("the system sucks!!!")
    
    
    if round==0:
        start()
    elif round==1: #no switch case in python sorry
        newMoves=["A7","A6"]
        mainMovesDiff(newMoves)
    elif round==2: #no switch case in python sorry
        newMoves=["A2","A4"]
        mainMovesApi(newMoves)
    elif round==1: #no switch case in python sorry
        newMoves=["C7","C4"]
        mainMovesDiff(newMoves)
    elif round ==3:
        newMoves=["E2","D3"]
        mainMovesApi(newMoves)
    else:
        print("me not happy the round count not working")
    



""" little fct to check if the programm is working
def checkEveryCell(img1,img2):
    
    diffArray = ["A2","A4"]
    return diffArray

"""



###########
#begining of the main code

#def the pictures you want to compare
image0 = cv2.imread("data\position0.jpg")
image1 = cv2.imread("data\position1.jpg")


start()
printTheBoard()
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
