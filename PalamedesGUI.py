import tkinter as tk
from tkinter import *
from moves import getBoard, tell_move_to_move
import customtkinter
import numpy as np
from numpy import asarray
from PIL import Image


from sentence_transformers import SentenceTransformer, util
from calibration import calibration, findCell, spotCell
from skimage.metrics import structural_similarity
from numpy import asarray
import glob
import os
import time   
import pickle
import serial
import keyboard
import requests

#chatGPT idea to use threading
#import threading

#while playing a normal game we take this one out on the other hand we need it for debugging 
#comPort = 'COM11' 
#ser = serial.Serial(comPort,baudrate = 2000000, timeout = 1)


#that will be to define the window 0 is chess mode & 1 is robot
mode = 0

#global variables
homeJ1= 2000
homeJ2= 9000
homeJ3= 500
everyoneHome= "J1"+str(homeJ1)+"J2"+str(homeJ2)+"J3"+str(homeJ3)
max_Time_Response=30 #how many seconds we wait in a loop before killing it



class robot:
    J1max=20000
    J1min=50
    J2max=20000
    J2min=50
    J3max=10000
    J3min=50
    Xmax=1000
    Xmin=-1000
    Ymax=1000
    Ymin=-1000
    Zmax=1000
    Zmin=50
    plus_minus_btn=50#when you press + or - it will do the written jump
    plus_minus_btnB=200

    #thoseare the start position 
    J1 = 2000
    J2 = 9000
    J3 = 500
    X = 0
    Y = 0
    Z = 10
    grip = 1
    gripBtnText = "Close gripper"
    moveJarray = [[2000,9000,500],["0","0","00"]] #That's what i changed to upthe start Js
    goToarray= [["+","+","+"],["0","0","0"],["0000","0000","0000"]]#first the sign, then the number, then the zeroes to complete
    toSave = [[] for _ in range(64)]
    toSaveIndex=0

    toSave=[]



### we import every pictures ###
def importImages():
    #first littleapproximation here I'm gonna define all of them as global, not the best move but should work for the moment
    
    #an empty png of 64x64 to fill the empty cells with something
    global empty
    empty=tk.PhotoImage(file ="data/empty64.png")
    empty=empty.subsample(1, 1)
    #subsample is to resize to be use in a button

    
    #black pieces
    global Bk
    Bk = tk.PhotoImage(file ="data/Bk.png")
    Bk=Bk.subsample(1, 1)
    global Bb
    Bb = tk.PhotoImage(file ="data/Bb.png")
    Bb=Bb.subsample(1, 1)
    global Bkn
    Bkn = tk.PhotoImage(file ="data/Bkn.png")
    Bkn=Bkn.subsample(1, 1)
    global Bp
    Bp = tk.PhotoImage(file ="data/Bp.png")
    Bp=Bp.subsample(1, 1)
    global Bq
    Bq = tk.PhotoImage(file ="data/Bq.png")
    Bq=Bq.subsample(1, 1)
    global Br
    Br = tk.PhotoImage(file ="data/Br.png")
    Br=Br.subsample(1, 1)

    #white pieces
    global Wb
    Wb = tk.PhotoImage(file ="data/Wb.png")
    Wb=Wb.subsample(1, 1)
    global Wk
    Wk = tk.PhotoImage(file ="data/Wk.png")
    Wk=Wk.subsample(1, 1)
    global Wkn
    Wkn=tk.PhotoImage(file ="data/Wkn.png")
    Wkn=Wkn.subsample(1, 1)
    global Wp
    Wp = tk.PhotoImage(file ="data/Wp.png")
    Wp=Wp.subsample(1, 1)
    global Wq
    Wq = tk.PhotoImage(file ="data/Wq.png")
    Wq=Wq.subsample(1, 1)
    global Wr
    Wr = tk.PhotoImage(file ="data/Wr.png")
    Wr=Wr.subsample(1, 1)

    

    

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


def updateBoard(self):

    #print(self.roundCounter)
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
    #yeah would be nice to have the pieces on the board
    updateBoard(self)



def controlMenu(self):

    #forget stuff
    self.title.pack_forget()
    self.main_fame.pack_forget()

    #remember stuff
    self.title2.pack(padx=12,pady=10, side=tk.TOP,fill=tk.BOTH) 
    self.secondary_frame.pack()

    self.window.geometry("850x700")



def gameMenu(self):
    
    #forget stuff first
    self.title2.pack_forget()
    self.secondary_frame.pack_forget()

    #remember stuff 
    self.title.pack(pady=12,padx=10)
    self.main_fame.pack(padx=10,pady=10)

   
    self.window.geometry("950x950")


def fillThe0(x):
    if x>= 10000:
        return ""
    elif x>=1000:
        return "0"
    elif x >=100:
        return "00"
    elif x >= 10:
        return "000"
    else:
        return "0000"

def antiLoop(start_time):
    if keyboard.is_pressed('d'):
        print("Key 'd' pressed. Stopping...")
        return  1# Exit the loop and stop the code
    elif time.time() - start_time > max_Time_Response: 
        print("Timeout: 'ready' signal not received within 5 seconds")
        return  1 # Exit the function on timeout
    else:
        return 0

def receive_response(expect_ready=False):
        start_time=time.time()

        while True:
            print("Listening to Arduino...")

            if antiLoop(start_time):
                print("Exiting due to timeout or button press.")
                return None  # Exit the function on timeout or button press

            input_data = ser.readline().decode().strip()
            print(input_data)

            if input_data == "J":
                continue

            if input_data != "":
                return int(input_data)

            if expect_ready and input_data == "ready":
                # Update GUI
                break


    
def sendToArduino(ArdString):
    command=ArdString
    command=command+'\r'
    ser.write(command.encode()) 

    start_time = time.time()  # Record the start time

    while True:
        print("we're sending to Arduino.......")
        if antiLoop(start_time): #we check for d buton or too long loop
            print("We're killing the loop!")
            break # Exit the function on timeout or button press
        line = ser.readline().decode().strip()
        if line == "ready":
            print("We received an answer, Arduino is ready")
            break  # End of data, exit the loop

        


#we need this one to listen for the updated version of J1, J2, J3 after sending XYZ coordinate
def sendAndListen(stringToSend):
    command=stringToSend+'\r'
    ser.write(command.encode())
    check=0
    #start_time = time.time()  # Record the start time


    robot.J1 = receive_response()
    robot.J2 = receive_response()
    receive_response(expect_ready=True)
    
    


def askForReset():
    command="reset"+'\r'
    ser.write(command.encode())

    start_time = time.time()  # Record the start time

    while True:
        print("we're reseting.......")

        if antiLoop(start_time): #we check for d buton or too long loop
            print("We're killing the loop!")
            return 0 # Exit the function on timeout or button press

        line = ser.readline().decode().strip()
        if line == "ready":
            print("We got a reset")
            return 1

        


class PalamedesGUI:

#mode 0 will be with the chess game and mode 1 will be with the robot controls

    def __init__(self):
        
        #custom to be nice
        customtkinter.set_appearance_mode("light")
        customtkinter.set_default_color_theme("blue")

        #def of our main window
        self.window = customtkinter.CTk()
        if (mode==1): 
            self.window.geometry("850x700")
        else:
            self.window.geometry("950x950")

        self.roundCounter=0
        self.window.title("Palamedes The Chess Master")   



        ###First page

        #title1  
        self.title=customtkinter.CTkLabel(self.window, text="Palamedes The Chess Master",font=("Roboto",40) )
        self.title.pack(pady=12,padx=10)
        #j'ai pas compris pk mais j'arrive pas à mettre mon titre dans le main_frame

        #A full window with everythin in it to make it appear & disapear easily
        self.main_fame = customtkinter.CTkFrame(master=self.window)
        self.main_fame.pack(pady=12, padx=12)

        
       
        self.boardFrame = customtkinter.CTkFrame(master = self.main_fame, height =100 , width = 100)
        #don't know why but height and width here don't change anything, weird...
        importImages()

        #now i need to create the first board
        createEmptyBoard(self.boardFrame)
        #self.boardFrame.pack()
        self.boardFrame.pack(padx=10,pady=10)
        """pack is maybe not the best one => look it up"""
        #it will stratch into the dimension

        self.nextBtn = customtkinter.CTkButton(
        master =self.main_fame,
        text="Next Player",
        command = self.next_turn
        )
        self.nextBtn.pack(padx=10,pady=10)

        self.reStartBtn = customtkinter.CTkButton(
            master=self.main_fame, 
            text="Start", 
            command= self.reset_Game)
        self.reStartBtn.pack(padx=10,pady=10)
        #that's how to place a button in a specific position

        self.ControlBtn = customtkinter.CTkButton(
            master=self.main_fame, 
            text="Advanced Controls", 
            command= self.open_Control)
        self.ControlBtn.pack(padx=10,pady=10)


        ###second page

        #title2 
        self.title2=customtkinter.CTkLabel(master=self.window, text="Palamedes Controller",font=("Roboto",40) )
        self.title2.pack(padx=12, pady=10, side=tk.TOP)

        #A full window with everythin in it to make it appear & disapear easily
        self.secondary_frame = customtkinter.CTkFrame(master=self.window, fg_color = 'transparent')
        self.secondary_frame.pack(fill=tk.BOTH)    

        self.gameModeBtn = customtkinter.CTkButton(
            master=self.secondary_frame, 
            text="Game Mode", 
            command= self.open_GameMode)
        self.gameModeBtn.pack(padx=10, pady=10,  side=tk.TOP)

        #left side side with forward
        self.forward_frame = customtkinter.CTkFrame(self.secondary_frame, corner_radius=10, fg_color = 'transparent')
        self.forward_frame.pack(padx=12, pady=10, side=tk.LEFT)

        self.forward_label = customtkinter.CTkLabel(self.forward_frame, text="Forward Kinematics",font=customtkinter.CTkFont(size=20, weight="bold") )
        self.forward_label.pack(padx=12, pady=10, side=tk.TOP)


        #top with J1
        self.J1_currentVar = tk.StringVar()
        self.J1_currentVar.set(robot.J1)#this one will have to get away later on it's just here for test

        self.J1_frame = customtkinter.CTkFrame(self.forward_frame, fg_color = 'transparent')
        self.J1_frame.pack()

        self.J1_label = customtkinter.CTkLabel(self.J1_frame,text ="J1",  font=customtkinter.CTkFont(size=30, weight="bold"), text_color = 'darkblue')
        self.J1_label.pack(padx=20, pady=10, side=tk.TOP)

        self.J1_current = customtkinter.CTkLabel(self.J1_frame,textvariable = self.J1_currentVar, font=customtkinter.CTkFont(size=20))
        self.J1_current.pack(padx=10, pady=10, side=tk.BOTTOM)

        self.J1_minusBtnB = customtkinter.CTkButton(self.J1_frame, text="--", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 2, command = self.J1_minusB)
        self.J1_minusBtnB.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J1_minusBtn = customtkinter.CTkButton(self.J1_frame, text="-", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 2, command = self.J1_minus)
        self.J1_minusBtn.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J1_writeBox = customtkinter.CTkEntry(self.J1_frame,placeholder_text =" ... ",justify = CENTER, corner_radius = 15, width = 75,font=customtkinter.CTkFont(size=15))
        self.J1_writeBox.pack(ipadx=5, ipady=5,  side=tk.LEFT)

        self.J1_plusBtn = customtkinter.CTkButton(self.J1_frame, text="+", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 2, command = self.J1_plus)
        self.J1_plusBtn.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J1_plusBtnB = customtkinter.CTkButton(self.J1_frame, text="++", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 2, command = self.J1_plusB)
        self.J1_plusBtnB.pack(padx=5, pady=5,  side=tk.LEFT)


        #top with J2
        self.J2_currentVar = tk.StringVar()
        self.J2_currentVar.set(robot.J2)

        self.J2_frame = customtkinter.CTkFrame(self.forward_frame, fg_color = 'transparent')
        self.J2_frame.pack()

        self.J2_label = customtkinter.CTkLabel(self.J2_frame,text ="J2",  font=customtkinter.CTkFont(size=30, weight="bold"), text_color = 'red')
        self.J2_label.pack(padx=20, pady=10, side=tk.TOP)

        self.J2_current = customtkinter.CTkLabel(self.J2_frame,textvariable = self.J2_currentVar, font=customtkinter.CTkFont(size=20))
        self.J2_current.pack(padx=10, pady=10, side=tk.BOTTOM)

        self.J2_minusBtnB = customtkinter.CTkButton(self.J2_frame, text="--", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 0, command = self.J2_minusB)
        self.J2_minusBtnB.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J2_minusBtn = customtkinter.CTkButton(self.J2_frame, text="-", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 0, command = self.J2_minus)
        self.J2_minusBtn.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J2_writeBox = customtkinter.CTkEntry(self.J2_frame,justify= CENTER, placeholder_text =" ... ",corner_radius = 15, width = 75,font=customtkinter.CTkFont(size=15))
        self.J2_writeBox.pack(ipadx=5, ipady=5,  side=tk.LEFT)

        self.J2_plusBtn = customtkinter.CTkButton(self.J2_frame, text="+", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 0, command = self.J2_plus)
        self.J2_plusBtn.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J2_plusBtnB = customtkinter.CTkButton(self.J2_frame, text="++", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 0, command = self.J2_plusB)
        self.J2_plusBtnB.pack(padx=5, pady=5,  side=tk.LEFT)



        #top with J3
        self.J3_currentVar = tk.StringVar()
        self.J3_currentVar.set(robot.J3)#this one will have to get away later on it's just here for test

        self.J3_frame = customtkinter.CTkFrame(self.forward_frame, fg_color = 'transparent')
        self.J3_frame.pack()

        self.J3_label = customtkinter.CTkLabel(self.J3_frame,text ="J3",  font=customtkinter.CTkFont(size=30, weight="bold"), text_color = 'green')
        self.J3_label.pack(padx=20, pady=10, side=tk.TOP)

        self.J3_current = customtkinter.CTkLabel(self.J3_frame,textvariable = self.J3_currentVar, font=customtkinter.CTkFont(size=20))
        self.J3_current.pack(padx=10, pady=10, side=tk.BOTTOM)

        self.J3_minusBtnB = customtkinter.CTkButton(self.J3_frame, text="--", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 2, command = self.J3_minusB)
        self.J3_minusBtnB.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J3_minusBtn = customtkinter.CTkButton(self.J3_frame, text="-", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 2, command = self.J3_minus)
        self.J3_minusBtn.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J3_writeBox = customtkinter.CTkEntry(self.J3_frame,justify = CENTER, placeholder_text =" ... ",corner_radius = 15, width = 75,font=customtkinter.CTkFont(size=15))
        self.J3_writeBox.pack(ipadx=5, ipady=5,  side=tk.LEFT)

        self.J3_plusBtn = customtkinter.CTkButton(self.J3_frame, text="+", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 2, command = self.J3_plus)
        self.J3_plusBtn.pack(padx=5, pady=5,  side=tk.LEFT)

        self.J3_plusBtnB = customtkinter.CTkButton(self.J3_frame, text="++", font=customtkinter.CTkFont(size=15, weight="bold"), corner_radius = 200, width = 2, command = self.J3_plusB)
        self.J3_plusBtnB.pack(padx=5, pady=5,  side=tk.LEFT)


        #send button 
        self.forward_send = customtkinter.CTkButton(self.forward_frame, text="Move Joints", font=customtkinter.CTkFont(size=20), corner_radius = 10, command = self.forward_send)
        self.forward_send.pack(padx=10, pady=10,  side=tk.BOTTOM)



        ###middle butons frame
        self.mid_frame = customtkinter.CTkFrame(self.secondary_frame, corner_radius=10, fg_color = 'transparent')
        self.mid_frame.pack(padx=10, pady=10, side=tk.LEFT)



        """
        #reset button by chatGPT
        self.canvasReset = tk.Canvas(self.mid_frame, width=100, height=100)
        self.canvasReset.pack()
        # Create the round button by drawing an oval shape
        self.resetBtn = self.canvasReset.create_oval(10, 10, 90, 90, fill="red")
        self.resetBtn_label = self.canvasReset.create_text(50, 50, text="Reset", fill="white", font=("Helvetica", 12))
        self.canvasReset.tag_bind(self.resetBtn, "<Button-1>", self.reset)
        """
        #reset button by me
        self.resetBtn = customtkinter.CTkButton(self.mid_frame, text="Reset", font=customtkinter.CTkFont(size=20), text_color="white",corner_radius = 10, command = self.reset, fg_color="#a61414", hover_color="darkred")
        self.resetBtn.pack(padx=10, pady=10,ipady=20, side=tk.BOTTOM)

        


        #manage gripper 
        self.grip_state = tk.StringVar()
        self.grip_state.set(robot.gripBtnText)

        self.gripperBtn = customtkinter.CTkButton(self.mid_frame,textvariable = self.grip_state, corner_radius= 20, command= self.move_grip, font=customtkinter.CTkFont(size=20))
        self.gripperBtn.pack(padx=10, pady=10, side= TOP)

        #save position
        self.savePositionBtn = customtkinter.CTkButton(self.mid_frame, text="Save current position", corner_radius= 20, command= self.save_position, font=customtkinter.CTkFont(size=20))
        self.savePositionBtn.pack(padx=10, pady=10, side = BOTTOM)



        ###reverse kinematics
        self.reverse_frame = customtkinter.CTkFrame(self.secondary_frame, corner_radius=10, fg_color = 'transparent')
        self.reverse_frame.pack(padx=10, pady=10, side=tk.LEFT)

        self.reverse_label = customtkinter.CTkLabel(self.reverse_frame, text="Reverse Kinematics",font=customtkinter.CTkFont(size=20, weight="bold") )
        self.reverse_label.pack(padx=10, pady=10, side=tk.TOP)

        #XYZ frame
        self.Xyz_frame = customtkinter.CTkFrame(self.reverse_frame, corner_radius=10, fg_color = 'transparent')
        self.Xyz_frame.pack(padx=10, pady=10, side=tk.TOP)

        #for X
        self.X_currentVar = tk.StringVar()
        self.X_currentVar.set(robot.X)#this one will have to get away later on it's just here for test

        self.X_frame = customtkinter.CTkFrame(self.Xyz_frame, corner_radius=10, fg_color = 'transparent')
        self.X_frame.pack(padx=10, pady=10, side=tk.LEFT)

        self.X_label = customtkinter.CTkLabel(self.X_frame, text="X",font=customtkinter.CTkFont(size=30, weight="bold"), text_color = 'darkblue' )
        self.X_label.pack(padx = 10, pady = 10, side = tk.TOP)

        self.X_current = customtkinter.CTkLabel(self.X_frame,textvariable = self.X_currentVar, font=customtkinter.CTkFont(size=20))
        #self.X_current.pack(padx=10, pady=10)

        self.X_writeBox = customtkinter.CTkEntry(self.X_frame,justify = CENTER, placeholder_text =" ... ",corner_radius = 15, width = 50,font=customtkinter.CTkFont(size=15))
        self.X_writeBox.pack(ipadx=5, ipady=5,  side=tk.BOTTOM)


        #for Y
        self.Y_currentVar = tk.StringVar()
        self.Y_currentVar.set(robot.Y)#this one will have to get away later on it's just here for test


        self.Y_frame = customtkinter.CTkFrame(self.Xyz_frame, corner_radius=10, fg_color = 'transparent')
        self.Y_frame.pack(padx=10, pady=10, side=tk.LEFT)

        self.Y_label = customtkinter.CTkLabel(self.Y_frame, text="Y",font=customtkinter.CTkFont(size=30, weight="bold"), text_color = 'red' )
        self.Y_label.pack(padx = 10, pady = 10, side = tk.TOP)

        self.Y_current = customtkinter.CTkLabel(self.Y_frame,textvariable = self.Y_currentVar, font=customtkinter.CTkFont(size=20))
        #self.Y_current.pack(padx=10, pady=10)

        self.Y_writeBox = customtkinter.CTkEntry(self.Y_frame,justify = CENTER, placeholder_text =" ... ",corner_radius = 15, width = 50,font=customtkinter.CTkFont(size=15))
        self.Y_writeBox.pack(ipadx=5, ipady=5,  side=tk.BOTTOM)

        #for Z
        self.Z_currentVar = tk.StringVar()
        self.Z_currentVar.set(robot.Z)#this one will have to get away later on it's just here for test

        self.Z_frame = customtkinter.CTkFrame(self.Xyz_frame, corner_radius=10, fg_color = 'transparent')
        self.Z_frame.pack(padx=10, pady=10, side=tk.LEFT)

        self.Z_label = customtkinter.CTkLabel(self.Z_frame, text="Z",font=customtkinter.CTkFont(size=30, weight="bold"), text_color = 'green' )
        self.Z_label.pack(padx = 10, pady = 10, side = tk.TOP)

        self.Z_current = customtkinter.CTkLabel(self.Z_frame,textvariable = self.Z_currentVar, font=customtkinter.CTkFont(size=20))
        #self.Z_current.pack(padx=10, pady=10)

        self.Z_writeBox = customtkinter.CTkEntry(self.Z_frame,justify = CENTER, placeholder_text =" ... ",corner_radius = 15, width = 50,font=customtkinter.CTkFont(size=15))
        self.Z_writeBox.pack(ipadx=5, ipady=5,  side=tk.BOTTOM)

        #move to position button
        self.position_send = customtkinter.CTkButton(self.reverse_frame, text="Move to Position", font=customtkinter.CTkFont(size=20), corner_radius = 10, command = self.positionSend)
        self.position_send.pack(padx=10, pady=10, side=BOTTOM)


        #Hide the second page 
        if mode == 0:
            self.title2.pack_forget()
            self.secondary_frame.pack_forget()
        else:
            self.title.pack_forget()
            self.main_fame.pack_forget()
        
        self.window.mainloop()

    #main page button
    def next_turn(self):
        updateBoard(self)
    
    def reset_Game(self):
        self.roundCounter=0
        startNewGame(self)

    def open_Control(self):
        controlMenu(self)

    #Second page button
    
    def open_GameMode(self):
        gameMenu(self)
    
    def J1_minus(self):
        if robot.J1 - robot.plus_minus_btn>robot.J1min:
            robot.J1 = robot.J1 - robot.plus_minus_btn
            self.J1_currentVar.set(robot.J1)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])

            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)


            sendToArduino(stringToSend)


        else:
            print("You're trying to go lower than 0 not possible")
        

    def J1_minusB(self):
            if robot.J1 - robot.plus_minus_btnB>robot.J1min:
                robot.J1 = robot.J1 - robot.plus_minus_btnB
                self.J1_currentVar.set(robot.J1)
                self.window.update_idletasks()

                #sending to arduino part
                #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
                robot.moveJarray[0][0]=robot.J1
                robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
                robot.moveJarray[0][1]=robot.J2
                robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
                robot.moveJarray[0][2]=robot.J3
                robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])

                print("here is the matrix:")
                print(robot.moveJarray)
                stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
                print(stringToSend)


                sendToArduino(stringToSend)


            else:
                print("You're trying to go lower than 0 not possible")
        

    def J1_plus(self):
        if robot.J1 + robot.plus_minus_btn <robot.J1max:#here we have to write the max range 
            robot.J1 = robot.J1 + robot.plus_minus_btn
            self.J1_currentVar.set(robot.J1)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)



            sendToArduino(stringToSend)
        else:
            print("You're trying to go too high")
        
    def J1_plusB(self):
            if robot.J1 + robot.plus_minus_btnB <robot.J1max:#here we have to write the max range 
                robot.J1 = robot.J1 + robot.plus_minus_btnB
                self.J1_currentVar.set(robot.J1)
                self.window.update_idletasks()

                #sending to arduino part
                #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
                robot.moveJarray[0][0]=robot.J1
                robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
                robot.moveJarray[0][1]=robot.J2
                robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
                robot.moveJarray[0][2]=robot.J3
                robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
                print("here is the matrix:")
                print(robot.moveJarray)
                stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
                print(stringToSend)



                sendToArduino(stringToSend)
            else:
                print("You're trying to go too high")
        
    
    def J2_minus(self):
        if robot.J2 - robot.plus_minus_btn >robot.J2min:
            robot.J2 = robot.J2 - robot.plus_minus_btn
            self.J2_currentVar.set(robot.J2)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)
            sendToArduino(stringToSend)

        else:
            print("You're trying to go lower than 0 not possible")
        
    def J2_minusB(self):
        if robot.J2 - robot.plus_minus_btnB >robot.J2min:
            robot.J2 = robot.J2 - robot.plus_minus_btnB
            self.J2_currentVar.set(robot.J2)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)
            sendToArduino(stringToSend)

        else:
            print("You're trying to go lower than 0 not possible")
        


    def J2_plus(self):
        if robot.J2 + robot.plus_minus_btn <robot.J2max:#here we have to write the max range 
            robot.J2 = robot.J2 + robot.plus_minus_btn
            self.J2_currentVar.set(robot.J2)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)
            sendToArduino(stringToSend)
        else:
            print("You're trying to go too high")
    
    def J2_plusB(self):
        if robot.J2 + robot.plus_minus_btnB <robot.J2max:#here we have to write the max range 
            robot.J2 = robot.J2 + robot.plus_minus_btnB
            self.J2_currentVar.set(robot.J2)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)
            sendToArduino(stringToSend)
        else:
            print("You're trying to go too high")

    def J3_minus(self):
        if robot.J3 - robot.plus_minus_btn > robot.J3min:
            robot.J3 = robot.J3 - robot.plus_minus_btn
            self.J3_currentVar.set(robot.J3)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)
            sendToArduino(stringToSend)

        else:
            print("You're trying to go lower than 0 not possible")
    
    def J3_minusB(self):
        if robot.J3 - robot.plus_minus_btnB > robot.J3min:
            robot.J3 = robot.J3 - robot.plus_minus_btnB
            self.J3_currentVar.set(robot.J3)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)
            sendToArduino(stringToSend)

        else:
            print("You're trying to go lower than 0 not possible")
        


    def J3_plus(self):
        if robot.J3 + robot.plus_minus_btn <robot.J3max:#here we have to write the max range 
            robot.J3 = robot.J3 + robot.plus_minus_btn
            self.J3_currentVar.set(robot.J3)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)
            sendToArduino(stringToSend)
        else:
            print("You're trying to go too high")
    
    def J3_plusB(self):
        if robot.J3 + robot.plus_minus_btnB <robot.J3max:#here we have to write the max range 
            robot.J3 = robot.J3 + robot.plus_minus_btnB
            self.J3_currentVar.set(robot.J3)
            self.window.update_idletasks()

            #sending to arduino part
            #we're just changing J1 but we need to update everyone just in case XYZ change something somewhere
            robot.moveJarray[0][0]=robot.J1
            robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
            robot.moveJarray[0][1]=robot.J2
            robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
            robot.moveJarray[0][2]=robot.J3
            robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
            print("here is the matrix:")
            print(robot.moveJarray)
            stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
            print(stringToSend)
            sendToArduino(stringToSend)
        else:
            print("You're trying to go too high")
        



    def forward_send(self):
        # Check and update J1
        if self.J1_writeBox.get():
            if robot.J1min <= int(self.J1_writeBox.get()) < robot.J1max:
                robot.J1 = int(self.J1_writeBox.get())
                robot.moveJarray[0][0] = robot.J1
                self.J1_writeBox.delete(0, tk.END)
                self.J1_currentVar.set(robot.J1)
            else:
                print("J1 is not in the valid range (0-999)")
        else:
            print("J1 entry is empty")

        # Check and update J2
        if self.J2_writeBox.get():
            if robot.J2min <= int(self.J2_writeBox.get()) < robot.J2max:
                robot.J2 = int(self.J2_writeBox.get())
                robot.moveJarray[0][1] = robot.J2
                self.J2_writeBox.delete(0, tk.END)
                self.J2_currentVar.set(robot.J2)
            else:
                print("J2 is not in the valid range (0-999)")
        else:
            print("J2 entry is empty")

        # Check and update J3
        if self.J3_writeBox.get():
            if robot.J3min <= int(self.J3_writeBox.get()) < robot.J3max:
                robot.J3 = int(self.J3_writeBox.get())
                robot.moveJarray[0][2] = robot.J3
                self.J3_writeBox.delete(0, tk.END)
                self.J3_currentVar.set(robot.J3)
            else:
                print("J3 is not in the valid range (0-999)")
        else:
            print("J3 entry is empty")

        
        print("we send J1, J2 & J3 to the robot")
        print("J1:", end = " ")
        print(robot.J1)
        print("J2:", end = " ")
        print(robot.J2)
        print("J3:", end = " ")
        print(robot.J3)

        self.window.update_idletasks()
        #sending to arduino part
        robot.moveJarray[1][0]= fillThe0(robot.moveJarray[0][0])
        robot.moveJarray[1][1]= fillThe0(robot.moveJarray[0][1])
        robot.moveJarray[1][2]= fillThe0(robot.moveJarray[0][2])
        print("here is the matrix:")
        print(robot.moveJarray)
        stringToSend = "J1" +robot.moveJarray[1][0] + str(robot.moveJarray[0][0]) + "J2" +robot.moveJarray[1][1] + str(robot.moveJarray[0][1])+ "J3" +robot.moveJarray[1][2] + str(robot.moveJarray[0][2])
        print(stringToSend)
        sendToArduino(stringToSend)
        

    def move_grip(self):

        if robot.grip==0:
            robot.grip=1
            robot.gripBtnText="Close Gripper"
            print("We're opening the Grip")
            sendToArduino("G0")
            
        else:
            robot.grip=0
            robot.gripBtnText="Open Gripper"
            print("We're closing the grip")
            sendToArduino("G1")
    
        self.grip_state.set(robot.gripBtnText)
        self.window.update_idletasks()


    def save_position(self):
        robot.toSave.append([robot.J1, robot.J2, robot.J3])
        print("the current array: ")
        print(robot.toSave)

    
    def positionSend(self):
        print("the go to position in XYZ coordinate")

        # Check and prepare X
        if self.X_writeBox.get():
            Xinput= self.X_writeBox.get()
            robot.X=Xinput

            if Xinput[0]=="-":
                robot.goToarray[0][0]="-"
                Xinput= Xinput[1:]#now we kick out the sign
            elif Xinput[0]=="+":
                robot.goToarray[0][0]="+"
                Xinput= Xinput[1:]#now we kick out the sign
            else:
                robot.goToarray[0][0]="+"

            
            if robot.Xmin <= int(Xinput) < robot.Xmax:
                robot.goToarray[1][0]=Xinput
                robot.goToarray[2][0] = fillThe0(int(Xinput))
                self.X_writeBox.delete(0, tk.END)
            else:
                print("X is not in the valid range (0-999)")
        else:
            print("X entry is empty")
        

        # Check and prepare Y
        if self.Y_writeBox.get():
            Yinput= self.Y_writeBox.get()
            robot.Y=Yinput

            if Yinput[0]=="-":
                robot.goToarray[0][1]="-"
                Yinput= Yinput[1:]#now we kick out the sign
            elif Yinput[0]=="+":
                robot.goToarray[0][1]="+"
                Yinput= Yinput[1:]#now we kick out the sign
            else:
                robot.goToarray[0][1]="+"

            
            if robot.Ymin<= int(Yinput) < robot.Ymax:
                robot.goToarray[1][1]=Yinput
                robot.goToarray[2][1] = fillThe0(int(Yinput))
                self.Y_writeBox.delete(0, tk.END)
            else:
                print("Y is not in the valid range (0-999)")
        else:
            print("Y entry is empty")


        # Check and prepare Z
        if self.Z_writeBox.get():
            Zinput= self.Z_writeBox.get()
            robot.Z=Zinput

            robot.goToarray[0][2]="+"#just because Z has to be positive

            if not Zinput[0].isdigit():
                Zinput= Zinput[1:]#now we kick out the sign#if the fisrt char is not a digit remove it 
            
            if robot.Zmin <= int(Zinput) < robot.Zmax:
                robot.J3=Zinput
                robot.goToarray[1][2]=Zinput
                robot.goToarray[2][2] = fillThe0(int(Zinput))
                self.Z_writeBox.delete(0, tk.END)
            else:
                print("Z is not in the valid range (0-999)")
        else:
            print("Z entry is empty")
        
        print(robot.goToarray)
        stringToSend = ""

        indexArray=["X","Y","Z"]

        for i in range(len(indexArray)):
            stringToSend += indexArray[i] + robot.goToarray[0][i] + robot.goToarray[2][i] + robot.goToarray[1][i] # Concatenate the label and value

        print(stringToSend)
        sendAndListen(stringToSend)

        self.J1_currentVar.set(robot.J1)
        self.J2_currentVar.set(robot.J2)
        self.J3_currentVar.set(robot.J3)
        self.X_currentVar.set(robot.X)
        self.Y_currentVar.set(robot.Y)
        self.Z_currentVar.set(robot.Z)

        self.window.update_idletasks()


    
    def reset(self):
        if askForReset():
            print("Emergency reset was activated we're bringing everyone Home!")
            robot.J1=homeJ1
            robot.J2=homeJ2
            robot.J3=homeJ3

            self.J1_currentVar.set(robot.J1)
            self.J2_currentVar.set(robot.J2)
            self.J3_currentVar.set(robot.J3)
            self.window.update_idletasks()

        else:
            print("Arduino said no need for Homing!")
        


PalamedesGUI()