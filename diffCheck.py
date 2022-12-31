import cv2
import numpy as np
#from sentence_transformers import SentenceTransformer, util
from calibration import calibration, findCell, spotCell
from skimage.metrics import structural_similarity
from PIL import Image
from numpy import asarray

#Load the model
#print("Loading the Neural Network Model...")
#model=SentenceTransformer('clip-ViT-B-32')
#it takes a lot of time tho

def checkRessemblance(ROI1,ROI2):
    ROI1=cv2.cvtColor(ROI1, cv2.COLOR_BGR2GRAY)
    ROI2=cv2.cvtColor(ROI2, cv2.COLOR_BGR2GRAY)
    score, diff = structural_similarity(ROI1, ROI2, full=True)
    print("Similarity Score: {:.3f}%".format(score*100))
    return score*100

def buildROI(board,previousImage,newImage,cell=""):
    xLowerLeft, yLowerLeft,xUpperRight,yUpperRight=findCell(board,cell)
    ROI1=previousImage[yUpperRight:yLowerLeft,xLowerLeft:xUpperRight]
    ROI2=newImage[yUpperRight:yLowerLeft,xLowerLeft:xUpperRight]
    cv2.rectangle(image1,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
    cv2.rectangle(image2,(xLowerLeft,yLowerLeft),(xUpperRight,yUpperRight),(0,0,255),2)
    return ROI1,ROI2

board='empty.jpeg'
boardWitness=np.array(Image.open('empty.jpeg').resize((400,400)))
image1=np.array(Image.open('position0.jpg').resize((400,400)))
image2=np.array(Image.open('position1.jpg').resize((400,400)))
coordinates, cells = calibration(board)

nb1,nb2=buildROI(boardWitness,image1,image2,"H5")
checkRessemblance(nb1, nb2)

nb3,nb4=buildROI(boardWitness,image1,image2,"E2")
checkRessemblance(nb3, nb4)
"""
data1=Image.fromarray(image1ROI)
data2=Image.fromarray(image2ROI)
data1.save('image1ROI.png')
data2.save('image2ROI.png')
"""
print("press x to quit")

while True:
    cv2.imshow('Image1',image1)
    cv2.imshow('Image2',image2)
    if cv2.waitKey(1) & 0xff ==ord('x'):
        break

