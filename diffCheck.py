import cv2
import numpy as np
from sentence_transformers import SentenceTransformer, util
from calibration import calibration, findCell, spotCell
from skimage.metrics import structural_similarity
from PIL import Image
from numpy import asarray
import glob
import os
import time

class imageDifference:
    def __init__(self,coordinates,cells,emptyBoard,emptyBoardData,image1,image2):
        self.coordinates=coordinates
        self.cells=cells
        self.emptyBoard=emptyBoard
        self.emptyBoardData=emptyBoardData
        self.image1=image1
        self.image2=image2

    def load(self):
        #Load the model
        print("Loading the Neural Network Model...")
        global model
        model=SentenceTransformer('clip-ViT-B-32')
        global threshold
        global counter
        counter=0
        threshold=53

    def AIcheck(self,cell=""):
        print(cell)#to debug
        global counter
        name=""
        move=False
        remark=""
        thresholdDown=85
        thresholdUp=99
        counter=counter+1
        ROI1,ROI2=self.buildROI(cell)
        name1="ROIA"+ str(counter)+".png"
        name2="ROIB"+ str(counter)+".png"
        data1=Image.fromarray(ROI1)
        data2=Image.fromarray(ROI2)
        data1.save(name1)
        data2.save(name2)

        firstImage = model.encode(Image.open(name1))
        secondImage = model.encode(Image.open(name2))
        text = model.encode(['ROIA','ROIB'])

        cos_scores = util.cos_sim(firstImage,secondImage)
        print(cos_scores)

        if (cos_scores*100) < thresholdDown:
            move=True
            remark="score under 87 : real Move "
        elif (cos_scores*100) > thresholdDown and (cos_scores*100) < thresholdUp:
            move=False
            remark="score between 87 and 98 : noise"
        else:
            move=False
            remark="score over 99 : same image twice"

        return move,remark


    def checkRessemblance(self,ROI1,ROI2):
        ROI1=cv2.cvtColor(ROI1, cv2.COLOR_BGR2GRAY)
        ROI2=cv2.cvtColor(ROI2, cv2.COLOR_BGR2GRAY)
        score, diff = structural_similarity(ROI1, ROI2, full=True)
        #print("Similarity Score: {:.3f}%".format(score*100))
        return score*100

    def buildROI(self,cell=""):
        xLowerLeft, yLowerLeft,xUpperRight,yUpperRight=findCell(self.emptyBoardData,cell)
        ROI1=self.image1[yUpperRight:yLowerLeft,xLowerLeft:xUpperRight]
        ROI2=self.image2[yUpperRight:yLowerLeft,xLowerLeft:xUpperRight]
        #cv2.rectangle(image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
        #cv2.rectangle(image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
        return ROI1,ROI2

    def checkEveryCell(self):
        allScores=[]
        sortedArray=[]
        diffArray=[]
        
        for cell in self.cells:
            ROI1,ROI2=self.buildROI(cell)
            score = self.checkRessemblance(ROI1, ROI2)
            tupple=(cell,score)
            allScores.append(tupple)

        sortedArray=allScores
        sortedArray.sort(key=lambda a: a[1])
        print(sortedArray)

        for result in allScores:
            myCell,procesScore=result

            if procesScore < threshold:
                xLowerLeft, yLowerLeft,xUpperRight,yUpperRight=findCell(self.emptyBoardData,myCell)

                if procesScore > 40 and procesScore < 55:
                    move, remark = self.AIcheck(myCell)
                    print(remark)
                    if move==True:
                        print("There is a difference at : ")
                        print(procesScore)
                        print(myCell)
                        print("")
                        diffArray.append(myCell)
                        cv2.rectangle(self.image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
                        cv2.rectangle(self.image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
                else:
                    print("There is a difference at : ")
                    print(procesScore)
                    print(myCell)
                    print("")
                    diffArray.append(myCell)
                    cv2.rectangle(self.image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
                    cv2.rectangle(self.image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)

        #if we have less than two differences, we send the 8 lowest scores to the AI
        if len(diffArray) < 2:

            for i in range(0,9):
                problemCell,problemScore=sortedArray[i]
                xLowerLeft, yLowerLeft,xUpperRight,yUpperRight=findCell(self.emptyBoardData,problemCell)
                move,remark = self.AIcheck(problemCell)
                print(remark)
                if move==True:
                    print("There is a difference at : ")
                    print(problemCell)
                    print("")
                    diffArray.append(problemCell)
                    cv2.rectangle(self.image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
                    cv2.rectangle(self.image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)

        return diffArray

#creating an instance
def localTest():
    board='data\empty.jpg'
    boardWitness=np.array(Image.open('data\empty.jpg').resize((400,400)))
    image0=np.array(Image.open('data\position0.jpg').resize((400,400)))
    image1=np.array(Image.open('data\position1.jpg').resize((400,400)))
    #image2=np.array(Image.open('position2.jpg').resize((400,400)))
    #image3=np.array(Image.open('position3.jpg').resize((400,400)))
    #image4=np.array(Image.open('position4.jpg').resize((400,400)))
    #move1=np.array(Image.open('move1.jpg').resize((400,400)))
    #move2=np.array(Image.open('move2.jpg').resize((400,400)))

    coordinates, cells = calibration(board)
    move1=imageDifference(coordinates,cells,board,boardWitness,image0,image1)
    #move2=imageDifference(coordinates,cells,board,boardWitness,image1,image2)
    move1.load()
    move1.checkEveryCell()
    #move2.checkEveryCell()
    """
    move1.AIcheck("A1")
    move1.AIcheck("E2")
    move1.AIcheck("D4")
    """
    print("press x to quit")

    while True:
        cv2.imshow('Image1',image0)
        cv2.imshow('Image2',image1)
        if cv2.waitKey(1) & 0xff ==ord('x'):
            break
        
#comment or uncomment to run a test
#localTest()