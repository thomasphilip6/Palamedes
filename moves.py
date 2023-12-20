import numpy as np
from numpy import asarray
import cv2
from PIL import Image
#from diffCheck import checkRessemblance, buildROI, checkEveryCell
from diffCheck import*
from calibration import calibration, findCell, spotCell
from skimage.metrics import structural_similarity
from ChessEngine import startGame, restartGame, getWinMove, updateEngineBoard
import requests



from sentence_transformers import SentenceTransformer, util

import glob
import os
import time   
import serial

import pickle

url = "http://172.20.10.2:8080/shot.jpg"

#we'll comunicate with moves.py during a running game
comPort = 'COM11' 
ser = serial.Serial(comPort,baudrate = 2000000, timeout = 1)



#Arduino command lines
#when we get ridof a piece we're gonna toss it here
dropmove =  "J116550J215550J301000" + '\r' #it is not the right position yet test it first
gripperClose= "G1"+'\r'
gripperOpen= "G0"+'\r'
everyoneHome= "J102000J209000J300500" +'\r'
correction= "C"+'\r'
global correctPositions
correctPositions= 0

#we hav the values until row E
realWorld = [["05800", "11800", "08100"], ["05200", "13350", "08100"], ["04800", "14550", "08150"], ["04450", "15500", "08250"], ["04250", "16450", "08300"], ["04100", "17350", "08300"], ["04100", "18300", "08500"], ["04400", "19350", "08550"],
["06250", "11950", "08150"], ["05750", "13350", "08150"], ["05400", "14450", "08250"], ["05150", "15600", "08150"], ["05000", "16500", "08200"], ["05000", "17400", "08250"], ["05250", "18450", "08400"], ["06050", "19600", "08500"],
["06800", "11750", "08050"], ["06300", "13200", "08100"], ["05950", "14500", "08150"], ["05850", "15300", "08200"], ["05650", "16350", "08300"], ["05850", "17300", "08350"], ["06200", "18300", "08500"], ["07100", "19300", "08600"],
["07350", "11450", "08150"], ["06850", "13000", "08100"], ["06500", "14250", "08250"], ["06400", "15250", "08250"], ["06350", "16100", "08250"], ["06550", "17100", "08400"], ["07050", "17950", "08650"], ["08000", "18950", "08450"],
["07900", "11150", "08200"], ["07450", "12650", "08250"], ["07150", "13900", "08200"], ["07100", "14850", "08250"], ["07100", "15850", "08450"], ["07350", "16650", "08550"], ["07800", "17450", "08650"], ["08550", "18250", "08600"],
["08550", "10600", "08300"], ["08000", "12350", "08250"], ["07750", "13500", "08350"], ["07750", "14550", "08250"], ["07800", "15350", "08400"], ["08000", "16100", "08500"], ["08500", "16900", "08450"], ["09050", "17550", "08700"],
["09300", "09700", "08250"], ["08700", "11650", "08200"], ["08450", "12850", "08200"], ["08400", "13950", "08300"], ["08450", "14750", "08350"], ["08650", "15550", "08400"], ["09050", "16200", "08550"], ["09600", "16850", "08700"],
["10300", "08300", "08200"], ["09500", "10700", "08150"], ["09150", "12100", "08200"], ["09050", "13350", "08250"], ["09100", "14100", "08250"], ["09300", "14850", "08450"], ["09650", "15550", "08500"], ["10050", "16000", "08550"]]

def cellToString(cell):
    order= "J1" + realWorld[cell][0]+ "J2" + realWorld[cell][1] + "J3" + realWorld[cell][2] + '\r'
    return order

def getPicture(url,name):
    img_resp=requests.get(url)
    img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
    img=cv2.imdecode(img_arr,-1)
    img=cv2.resize(img,(640,360))
    cv2.imwrite(name, img)
    img_arr_resized=np.array(Image.open(name).resize((640,360)))
    return img_arr_resized

def displayImage(image):
    img=cv2.imdecode(image, -1)
    cv2.imshow("Android_cam", img)


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
    #print(cells)

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
1/8 = rock
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
    global correctPositions
    newCell=p2
    isNowEmpty=p1
    newCellMove=cellToString(p2)
    print(newCellMove)
    isNowEmptyMove=cellToString(p1)
    print(isNowEmptyMove)
    pieceMoved=board[p1]
    if board[p2][0]==op_Color:
        wasEaten=board[p2]
        #eatHim()#we would need a way to specify to the robot that he needs to first eat the 
        #we need to send the info to eat a piece:
        ser.write(gripperOpen.encode())
        ser.write(newCellMove.encode())
        ser.write(gripperClose.encode())
        ser.write(everyoneHome.encode())
        ser.write(gripperOpen.encode())
        time.sleep(10)
        correctPositions = correctPositions + 1
    else:
        wasEaten=0 
    board[newCell]=pieceMoved
    board[isNowEmpty]=[0][0]  
    #We do the move from our spot to the empty cell 
    ser.write(gripperOpen.encode())
    ser.write(isNowEmptyMove.encode())
    ser.write(gripperClose.encode())
    ser.write(newCellMove.encode())
    ser.write(gripperOpen.encode())
    ser.write(everyoneHome.encode())
    correctPositions = correctPositions + 1
    print(isNowEmptyMove)
    print(newCellMove)

    if (correctPositions >= 2):
        ser.write(correction.encode())
        correctPositions=0

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
    #load images
    global boardWitness
    global emptyBoard
    boardWitness=getPicture(url,'empty.jpg')
    emptyBoard='empty.jpg'
    global coordinates
    global cells
    coordinates, cells = calibration(emptyBoard)
    #boardWitness=np.array(Image.open('data\empty.jpg').resize((400,400)))
    #previousPicture=getPicture(url,'previousPicture.jpg')
    #image1=np.array(Image.open('data\position1.jpg').resize((400,400)))
    #faire la calibration une seule fois :
    

def check_castling(p1,p2,p3,p4):
    pic_to_check= [p1,p2,p3,p4]
    kingside=["H8","E8","G8","F8"]
    qweenside=["A8","C8","E8","D8"]
    side="0"
    arrayToCheck=[]

    for pic in pic_to_check:
        if pic == kingside[O]:
            side="k"
            arrayToCheck=kingside
    if side =="0":#
        for pic in pic_to_check:
            if pic == qweenside[O]:
                side="q"
                arrayToCheck=qweenside


    if side=="0":
        print("unexpected error, no king or qween side found")
    
    count=0
    for pic in pic_to_check:
        for square in arrayToCheck:
            if pic== square:
                count+=1

    if  count==4:
        print("we found a castling move")
        update_castling(side)

        if side=="q":
            board[0][0]=0#couleurs, tower empty 
            board[0][1]=0#pièce
            board[4][0]=0#couleurs, king empty
            board[4][1]=0#pièce

            board[3][0]=op_Color
            board[3][1]=1#number refering to the rock on the left, sorry for the magic number
            board[2][0]=op_Color
            board[2][1]=5#nb of the king

        else:
            board[7][0]=0#couleurs, tower empty 
            board[7][1]=0#pièce
            board[4][0]=0#couleurs, king empty
            board[4][1]=0#pièce

            board[5][0]=op_Color
            board[5][1]=1#number refering to the rock on the left, sorry for the magic number
            board[6][0]=op_Color
            board[6][1]=5#nb of the king

    else:
        print("unexpected error, we didn't get a match with the castling")



def mainMovesDiff():
    print("write p to take previous picture ")
    if input()=='p':
        previousPicture=getPicture(url,'previousPicture.jpg')
    print("write n to take new picture ")
    if input()=='n':
        newPicture=getPicture(url, 'newPicture.jpg')
    global move1
    move1=imageDifference(coordinates,cells,emptyBoard,boardWitness,previousPicture,newPicture)
    # from now on coordinates and cells are accessible with move1.cells and move1.coordinates
    move1.load()

    #to update the player move
    diffCells=move1.checkEveryCell()
    #cell1=diffCells[0]
    #cell2=diffCells[1]
    print("the 2 cells diff:")
    print(diffCells)
    if len(diffCells)==4:#4 difff should mean a castling move we'll check that out

        p1,p2,p3,p4=check_castling(diffCells)
        ####there is lot of stuff missing here
    elif len(diffCells)==2:#that should be a regular move, check it
        p1,p2 = translateCellToIndex(diffCells)
        #this whole part only consider the perfect result with two differences no more no less
        #so we'll make sure everything works properly before those line   
        startMove, endMove = readMove(p1, p2)#update moves
        startCell=cells[startMove]
        endCell=cells[endMove]
        print("startCell & endCells",startCell,endCell  )
        updateEngineBoard(startCell, endCell)#update engine
        #this line is wrong find the mistake
    else:
        print("Unexpected number of diff in mainMovesDiff")

    

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


#avec le GUI on appelle la fct suivante pour aller chercher les images
def tell_move_to_move(round):

    if round==0:#no switch case in python sorry
        start()#start the moves.py board 
        prep()#start the diff check and calibration
        startGame()#Start the chess engine and stockfish the API
        mainMovesDiff()
    elif (round % 2 == 0):
        #Human
        mainMovesDiff()
        printTheBoard()
        #take a picture
    else:
        #Robot
        mainMovesApi()
        #take a picture 

    ###il va falloir faire un truc comme ça####
    """
    #Player is white and he is playing round 1 so impair == white
    elif (round % 2 != 0):
        #Human
        mainMovesDiff()
        printTheBoard()
        #take a picture
    else:
        #Robot
        mainMovesApi()
        #take a picture 

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

