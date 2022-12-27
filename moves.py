import numpy as np


def start(board):
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
8/1 = tower
2/7 = horse
3/6 = bishop
4 = queen
5 = king 
9 to 16 = pawn 
"""
def printTheBoard(board,letters):
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


def readMove(board, p1, p2):
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
        
def writeMove(board,p1,p2):
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

        

###########
#begining of the main code

my_Color = 1 #We'll have to be careful with that
# 1=white and 2=black
if my_Color == 1:
    op_Color = 2
else:
    op_Color = 1



#and we'll do 0 = empty 
board =np.zeros((64,2),dtype=int)
letters=["A","B","C","D","E","F","G","H"]
start(board)
printTheBoard(board,letters)

#now I would need to import the 2 squares that had movents on the picture differentiation
p1=7
p2=4

#function to find the movemnt and who moved
readMove(board,p1,p2)
print("That's after 1 move:")
printTheBoard(board, letters)

#now we need to learn how to write move from the API and robot on the system when input the piece that is moving
startPos =8
endPos = 4
writeMove(board,startPos, endPos)
print("After imad my deadly move...")
printTheBoard(board, letters)
