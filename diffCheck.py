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

def AIcheck(board,image1,image2,cell=""):
    global counter
    name=""
    counter=counter+1
    ROI1,ROI2=buildROI(board,image1,image2,cell)
    name1="ROIA"+ str(counter)+".png"
    name2="ROIB"+ str(counter)+".png"
    data1=Image.fromarray(ROI1)
    data2=Image.fromarray(ROI2)
    data1.save(name1)
    data2.save(name2)

    firstImage = model.encode(Image.open(name1))
    secondImage = model.encode(Image.open(name2))
    text = model.encode(['ROIA','ROIB'])

    #cos_scores = util.cos_sim(firstImage,text)
    #print(cos_scores)
    #print("now trying something else")
    cos_scores2 = util.cos_sim(firstImage,secondImage)
    print(cos_scores2)


def checkRessemblance(ROI1,ROI2):
    ROI1=cv2.cvtColor(ROI1, cv2.COLOR_BGR2GRAY)
    ROI2=cv2.cvtColor(ROI2, cv2.COLOR_BGR2GRAY)
    score, diff = structural_similarity(ROI1, ROI2, full=True)
    #print("Similarity Score: {:.3f}%".format(score*100))
    return score*100

def buildROI(board,previousImage,newImage,cell=""):
    xLowerLeft, yLowerLeft,xUpperRight,yUpperRight=findCell(board,cell)
    ROI1=previousImage[yUpperRight:yLowerLeft,xLowerLeft:xUpperRight]
    ROI2=newImage[yUpperRight:yLowerLeft,xLowerLeft:xUpperRight]
    #cv2.rectangle(image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
    #cv2.rectangle(image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
    return ROI1,ROI2

def checkEveryCell(image1,image2):
    diffArray=[]
    for cell in cells:
        ROI1,ROI2=buildROI(boardWitness,image1,image2,cell)
        score = checkRessemblance(ROI1, ROI2)

        if score < threshold:
            xLowerLeft, yLowerLeft,xUpperRight,yUpperRight=findCell(boardWitness,cell)
            cv2.rectangle(image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
            cv2.rectangle(image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)

            print("There is a difference at : ")
            print(score)
            print(cell)
            print("")
            diffArray.append(cell)
    return diffArray

#checkEveryCell(image0,image1)
AIcheck(boardWitness,image0,image1,"A1")
AIcheck(boardWitness,image0,image1,"E2")
AIcheck(boardWitness,image0,image1,"D4")
"""
data1=Image.fromarray(image1ROI)
data2=Image.fromarray(image2ROI)
data1.save('image1ROI.png')
data2.save('image2ROI.png')
"""
print("press x to quit")

while True:
    cv2.imshow('Image1',image0)
    cv2.imshow('Image2',image1)
    if cv2.waitKey(1) & 0xff ==ord('x'):
        break

