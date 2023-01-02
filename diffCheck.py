import cv2
import numpy as np
from sentence_transformers import SentenceTransformer, util
from calibration import calibration, findCell, spotCell
from skimage.metrics import structural_similarity
from PIL import Image
from numpy import asarray
import glob
import os

#Load the model
print("Loading the Neural Network Model...")
model=SentenceTransformer('clip-ViT-B-32')
#it takes a lot of time tho

threshold=53
board='empty.jpeg'
boardWitness=np.array(Image.open('empty.jpeg').resize((400,400)))
image0=np.array(Image.open('position0.jpg').resize((400,400)))
image1=np.array(Image.open('position1.jpg').resize((400,400)))
image2=np.array(Image.open('position2.jpg').resize((400,400)))
image3=np.array(Image.open('position3.jpg').resize((400,400)))
image4=np.array(Image.open('position4.jpg').resize((400,400)))

move1=np.array(Image.open('move1.jpg').resize((400,400)))
move2=np.array(Image.open('move2.jpg').resize((400,400)))

coordinates, cells = calibration(board)
counter=0

class imageDifference:
    def __init__(self,coordinates,cells,emptyBoard,emptyBoardData,image1,image2):
        self.coordinates=coordinates
        self.cells=cells
        self.emptyBoard=emptyBoard
        self.emptyBoardData=emptyBoardData
        self.image1=image1
        self.image2=image2

    def AIcheck(self,cell=""):
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
        """
        cos_scores=str(cos_scores[0][0])
        cos_scores=cos_scores.replace('tensor(','')
        cos_scores=cos_scores.replace(')','')
        """
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
        diffArray=[]
        for cell in self.cells:
            ROI1,ROI2=self.buildROI(cell)
            score = self.checkRessemblance(ROI1, ROI2)

            if score < threshold:
                xLowerLeft, yLowerLeft,xUpperRight,yUpperRight=findCell(self.emptyBoardData,cell)
                
                if score > 40 and score < 55:
                    move, remark = self.AIcheck(cell)
                    print(remark)
                    if move==True:
                        print("There is a difference at : ")
                        print(score)
                        print(cell)
                        print("")
                        diffArray.append(cell)
                        cv2.rectangle(image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
                        cv2.rectangle(image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
                else:
                    print("There is a difference at : ")
                    print(score)
                    print(cell)
                    print("")
                    diffArray.append(cell)
                    cv2.rectangle(image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
                    cv2.rectangle(image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
        return diffArray

#creating an instance
move1=imageDifference(coordinates,cells,board,boardWitness,image0,image1)
move1.checkEveryCell()
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

