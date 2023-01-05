import tkinter as tk
from moves import getBoard, tell_move_to_move




### we import every pictures ###
def importImages():
    #first littleapproximation here I'm gonna define all of them as global, not the best move but should work for the moment


    #an empty png of 64x64 to fill the empty cells with something
    global empty
    empty=tk.PhotoImage(file ="data/empty64.png")
    empty=empty.subsample(1, 2)
    #subsample is to resize to be use in a button

    
    #black pieces
    global Bk
    Bk = tk.PhotoImage(file ="data/Bk.png")
    Bk=Bk.subsample(1, 2)
    global Bb
    Bb = tk.PhotoImage(file ="data/Bb.png")
    Bb=Bb.subsample(1, 2)
    global Bkn
    Bkn = tk.PhotoImage(file ="data/Bkn.png")
    Bkn=Bkn.subsample(1, 2)
    global Bp
    Bp = tk.PhotoImage(file ="data/Bp.png")
    Bp=Bp.subsample(1, 2)
    global Bq
    Bq = tk.PhotoImage(file ="data/Bq.png")
    Bq=Bq.subsample(1, 2)
    global Br
    Br = tk.PhotoImage(file ="data/Br.png")
    Br=Br.subsample(1, 2)

    #white pieces
    global Wb
    Wb = tk.PhotoImage(file ="data/Wb.png")
    Wb=Wb.subsample(1, 2)
    global Wk
    Wk = tk.PhotoImage(file ="data/Wk.png")
    Wk=Wk.subsample(1, 2)
    global Wkn
    Wkn=tk.PhotoImage(file ="data/Wkn.png")
    Wkn=Wkn.subsample(1, 2)
    global Wp
    Wp = tk.PhotoImage(file ="data/Wp.png")
    Wp=Wp.subsample(1, 2)
    global Wq
    Wq = tk.PhotoImage(file ="data/Wq.png")
    Wq=Wq.subsample(1, 2)
    global Wr
    Wr = tk.PhotoImage(file ="data/Wr.png")
    Wr=Wr.subsample(1, 2)

    

def createEmptyBoard(boardFrame):
    #define the board before the interface
    for i in range(0,8):
        #boardFrame.columnconfigure(i,weight=1)
        boardFrame.rowconfigure(i,weight=1)

    global boardCells
    boardCells={}
    #that's a dictionary to name every piece differently (automatically name cell0,cell1...cell63)

    for i in range(0,8):

        if i%2==0:
            for j in range(7,-1,-1):
                if ((7-j)+8*i)%2==0:
                    boardCells["cell{0}".format((7-j)+8*i)] =tk.Button(boardFrame, width = 80,height = 80,bg="#696969", image = empty)
                    #for some weird reason the height semm to have twice the unit of the width
                    boardCells["cell{0}".format((7-j)+8*i)].grid(row=j,column=i, sticky=tk.W+tk.E)
                else:
                    boardCells["cell{0}".format((7-j)+8*i)] =tk.Button(boardFrame,  width = 80,height = 80,bg="white", image = empty)
                    boardCells["cell{0}".format((7-j)+8*i)].grid(row=j,column=i, sticky=tk.W+tk.E)
        else:
            for j in range(7,-1,-1):
                if ((7-j)+8*i)%2!=0:
                    boardCells["cell{0}".format((7-j)+8*i)] =tk.Button(boardFrame,  width = 80,height = 80,bg="#696969", image = empty)
                    boardCells["cell{0}".format((7-j)+8*i)].grid(row=j,column=i, sticky=tk.W+tk.E)
                else:
                    boardCells["cell{0}".format((7-j)+8*i)] =tk.Button(boardFrame, width = 80,height = 80,bg="white", image = empty)
                    boardCells["cell{0}".format((7-j)+8*i)].grid(row=j,column=i, sticky=tk.W+tk.E)
        # text=((7-j)+8*i), font=('Arial',18),fg="white", line to add to print the index of a cell


def translateToPic(board):
    #this code turns the array of cells define 
    #with numbers to the variables of the needed PNG images
    newPicBoard=[]
    for i in range(0,64):

        if board[i][0]==0:
            #esay it's an empty spot 
            newPicBoard.append(empty)
        if board[i][0]==1:
            #wait a sec is white 1 or is it black??? - to check 
            #we'll say it's white for the moment
            piece = board[i][1]
            #so piece can be between 1 and 16 with 6 diff options
            #so just discover that switch case isn't a thing with python, sad will use the good old elif
            if piece>8:
                newPicBoard.append(Wp)
            elif piece == 1 or piece==8:
                newPicBoard.append(Wr)
            elif piece == 2 or piece==7:
                newPicBoard.append(Wkn)
            elif piece == 3 or piece==6:
                newPicBoard.append(Wb)
            elif piece == 5:
                newPicBoard.append(Wk)
            else:
                newPicBoard.append(Wq)
                #if there is a mistake somwhere we'll get a couple extra queen on the board
        if board[i][0]==2:#so that should be black
            piece = board[i][1]
            if piece>8:
                newPicBoard.append(Bp)
            elif piece == 1 or piece==8:
                newPicBoard.append(Br)
            elif piece == 2 or piece==7:
                newPicBoard.append(Bkn)
            elif piece == 3 or piece==6:
                newPicBoard.append(Bb)
            elif piece == 5:
                newPicBoard.append(Bk)
            else:
                newPicBoard.append(Bq)

    return newPicBoard

"""
little reminder
8/1 = rock
2/7 = knight
3/6 = bishop
4 = queen
5 = king 
9 to 16 = pawn 
"""

#I think we don't need that anymore
"""
def getBoard():#this a test getBoard
    #can't access yet to the other part so we can try here
    newBoard=[
        [ 2, 1 ],[ 2 , 9 ],[ 0, 0 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 1 , 9 ],[ 1, 1 ],
        [ 2, 2 ],[ 2 ,10 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 1 ,10 ],[ 1, 2 ],
        [ 2 ,3 ],[ 2 ,11 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 1 ,11 ],[ 1, 3 ],
        [ 2 ,4 ],[ 2 ,12 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 1 ,12 ],[ 1, 4 ],
        [ 2 ,5 ],[ 2 ,13 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 1 ,13 ],[ 1, 5 ],
        [ 2, 6 ],[ 2 ,14 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 1 ,14 ],[ 1, 6 ],
        [ 2 ,7 ],[ 2 ,15 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 1 ,15 ],[ 1, 7 ],
        [ 2 ,8 ],[ 2, 16 ],[ 0 ,0 ],[ 0 ,0 ],[ 0 ,0 ],[ 0, 0 ],[ 1 ,16 ],[ 1, 8 ]]
    return newBoard
"""

def updateBoard(self):

    print(self.roundCounter)
    tell_move_to_move(self.roundCounter)
    newBoard=translateToPic(getBoard())
    #print (newBoard)
    #WE import from moves the up to date chess board
    for i in range(0,64):
        boardCells["cell{0}".format(i)] ['image'] = newBoard[i]
    print("We should be up to date!")

    self.roundCounter+=1
    #self.window.mainloop()
    #I guesss we could have that little guy here but pretty sure that's not the proper way 

def startNewGame(self):
    newBoard=[]
    for i in range(0,64):
        newBoard.append(empty)
    #print (newBoard)
    #WE import from moves the up to date chess board
    for i in range(0,64):
        boardCells["cell{0}".format(i)] ['image'] = newBoard[i]
    print("We should have a brand new empty board")

    #self.window.mainloop()
    #I guesss we could have that little guy here but pretty sure that's not the proper way 
"""
def littest():
    print("Press 1 to go to next round")
    next = int(input())

    if next==1:
        updateBoard()
        print("here you go with a beautiful board")
    else:
        print("sad you should have said yes... i'm gonna cry now")

"""


class PalamedesGUI:

    
    def __init__(self):

        #def of our main window
        self.window = tk.Tk()
        self.window.geometry("800x800")
        self.window.title("Palamedes Interface")

        global roundCounter
        self.roundCounter=0
        

        self.boardFrame = tk.Frame(self.window, height =100 , width = 100)
        #don't know why but height and width here don't change anything, weird...
        importImages()

        #now i need to create the first board
        createEmptyBoard(self.boardFrame)
        self.boardFrame.pack()
        """pack is maybe not the best one => look it up"""
        #it will stratch into the dimension

        self.btn1 = tk.Button(
        self.window,
        text="Next Player",
        font=("Arial",18),
        width = 10,
        height = 2,
        bg="black",
        fg="White",
        command = self.next_turn
        )
        self.btn1.pack(padx=10,pady=10)

        self.newBtn = tk.Button(self.window, text="Restart", command= self.reset_Game)
        self.newBtn.place(x=200,y=200, height= 20, width=50)
        #that's how to place a button in a specific position

        

        self.window.mainloop()

        

    def next_turn(self):
        print("Hello dumb ass!!!")
        updateBoard(self)
    
    def reset_Game(self):
        print("That's where all started!!!")
        self.roundCounter=0
        startNewGame(self)



PalamedesGUI()