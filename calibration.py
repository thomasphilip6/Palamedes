import cv2
import numpy as np
from PIL import Image
from numpy import asarray

letters=["A","B","C","D","E","F","G","H"]
numbers=["1","2","3","4","5","6","7","8"]
cells=[]
coordinates=[]

for letter in letters:
    for number in numbers:
        cells.append(letter + number)

nline = 7
ncol = 7
evt=0

def mouseClick(event,xPos,yPos,flags,params):
    global evt
    global xMouse
    global yMouse
    if event==cv2.EVENT_LBUTTONDOWN:
        #print(xMouse,yMouse)
        xMouse=xPos
        yMouse=yPos
        evt=event #is equal to 1 for the left click
    if event==cv2.EVENT_LBUTTONUP:
        xMouse=xPos
        yMouse=yPos
        evt=event #is equal to 4 for this one
    if event==cv2.EVENT_RBUTTONDOWN:
        xMouse=xPos
        yMouse=yPos
        evt=event #is equal to 2 for the right click
                
class Line:
    def __init__(self, image, yB, xB, yA, xA, coordinate1, coordinate2, wanted):
        self.image=image
        self.yB=yB
        self.xB=xB
        self.yA=yA
        self.xA=xA
        self.coordinate1=coordinate1
        self.wanted=wanted
        self.coordinate2=coordinate2

    def getSlope(self):
        if self.xB == self.xA:
           self.xB=self.xB - 1
        if self.yB == self.yA:
           self.yB=self.yB - 1
        slope=(self.yB-self.yA)/(self.xB-self.xA)
        return slope
    
    def originParam(self):
        originParam=self.yB-self.getSlope()*self.xB
        return originParam

    def getY(self,coordinate):
        Y=int(self.getSlope()*coordinate + self.originParam())
        X=int(coordinate)
        return X,Y
    def getX(self,coordinate):
        X=int((coordinate-self.originParam())/self.getSlope())
        Y=int(coordinate)
        return X,Y

    def drawLines(self):

        if self.wanted=='X':
            (x1,y1)=self.getX(self.coordinate1)
            (x2,y2)=self.getX(self.coordinate2)
        if self.wanted=='Y':
            (x1,y1)=self.getY(self.coordinate1)
            (x2,y2)=self.getY(self.coordinate2)
        cv2.line(self.image, (x2,y2) , (x1,y1), (0,255,255),2 )

def findCell(image,name):
    indexWanted=cells.index(str(name))
    xCase,yCase=coordinates[indexWanted][0]
    xCase1,yCase1=coordinates[indexWanted][1]
    cv2.rectangle(image,(xCase,yCase),(xCase1,yCase1),(0,255,0),2)

def findIntersections(Line1,Line2,debug,image):
    a1=Line.getSlope(Line1)
    a2=Line.getSlope(Line2)
    b1=Line.originParam(Line1)
    b2=Line.originParam(Line2)

    xIntersection=int((b2-b1)/(a1-a2))
    yIntersection=int(a1*xIntersection+b1)

    if debug==1:
        cv2.circle(image,(xIntersection,yIntersection),3,(255,0,0),2)

    return xIntersection,yIntersection

def correctData(corners):
    dataArray=[]
    if corners[1][0][0] > corners[0][0][0] + 5 and corners[1][0][1]<200:
        #if the array if filled by incrementing the x direction first instead of y
        print("case 1 : data is being reworked")
        for j in range(42,49):
            for i in range(0,7):
                dataArray.append(corners[j-i*7])
        correctedData=np.array(dataArray)

    elif corners[1][0][0] < corners[0][0][0] + 5 and corners[0][0][1] >200:
        print("case 2 : data is being reworked")
        jArray=[6,5,4,3,2,1,0]
        for j in jArray:
            for i in range(0,7):
                dataArray.append(corners[j+i*7])
        correctedData=np.array(dataArray)

    else: 
        correctedData=corners
        print("case 3 : no work on data")
    
    return correctedData


image2=np.array(Image.open('empty.jpeg').resize((400,400)))
testImage=np.array(Image.open('empty.jpeg').resize((400,400)))
grayImage = cv2.cvtColor(image2,cv2.COLOR_BGR2GRAY)
grayImage2 = cv2.cvtColor(image2,cv2.COLOR_BGR2GRAY)

retval, corners = cv2.findChessboardCorners(grayImage, (nline, ncol), None)
correctedData=correctData(corners)
if (retval):
    print("there is a board")
else:
    print("no board")

fnl = cv2.drawChessboardCorners(grayImage2, (nline, ncol), corners, retval)
fnlcorrected = cv2.drawChessboardCorners(grayImage, (nline, ncol), correctedData, retval)

print(corners)
print("now corrected data")
print(correctedData)
cv2.imshow('boardcv2',fnl)
cv2.imshow('boardcorrected',fnlcorrected)
corners=correctedData

for i in range(49):
    x=int(corners[i][0][0])
    y=int(corners[i][0][1])
    cv2.circle(image2,(x,y),2,(0,0,255),3)

print(corners[0][0][0])
print(correctedData[0][0][0])
cv2.rectangle(image2,(int(corners[0][0][0]),int(corners[0][0][1])),(int(corners[8][0][0]),int(corners[8][0][1])),(0,255,0),2)

cv2.namedWindow('board')
cv2.setMouseCallback('board',mouseClick)
counter=0
flag=0
print("Left Click to define the Y parameter for the upper right corner")
print("Right Click to define the Y parameter for the lower left corner")

while flag!=2:
    cv2.imshow('board', image2)
    if evt==1 and flag==0:
        yUpperRight = yMouse
        flag=1
    if evt==2 and flag==1:
        yLowerLeft = yMouse
        flag=2
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
Diag1=Line(image2, int(corners[0][0][1]), int(corners[0][0][0]), int(corners[48][0][1]), int(corners[48][0][0]), yUpperRight, yLowerLeft, "X" )
flag=0
print("Left Click to define the Y parameter for the upper left corner")
print("Right Click to define the Y parameter for the lower right corner")

while flag!=2:
    cv2.imshow('board', image2)
    if evt==1 and flag==0:
        yUpperLeft = yMouse
        flag=1
    if evt==2 and flag==1:
        yLowerRight = yMouse
        flag=2
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
Diag2=Line(image2, int(corners[6][0][1]), int(corners[6][0][0]), int(corners[42][0][1]), int(corners[42][0][0]), yUpperLeft, yLowerRight, "X" )
#creation of the bounding rectangle
cv2.line(image2,(Line.getX(Diag2,yUpperLeft)),(Line.getX(Diag1, yLowerLeft)),(0,0,255),2)
cv2.line(image2,(Line.getX(Diag2,yLowerRight)),(Line.getX(Diag1, yUpperRight)),(0,0,255),2)
cv2.line(image2,(Line.getX(Diag2,yUpperLeft)),(Line.getX(Diag1, yUpperRight)),(0,0,255),2)
cv2.line(image2,(Line.getX(Diag1,yLowerLeft)),(Line.getX(Diag2, yLowerRight)),(0,0,255),2)
#creating instances for the bounding rectangle
xUpperLeft,ignore = Line.getX(Diag2,yUpperLeft)
xLowerLeft,ignore = Line.getX(Diag1, yLowerLeft)
xUpperRight,ignore = Line.getX(Diag1,yUpperRight)
xLowerRight,ignore = Line.getX(Diag2,yLowerRight)

lastHorizontal=Line(image2,int(yUpperLeft),int(xUpperLeft),int(yUpperRight),int(xUpperRight),10,490,"Y")
horizontal1=Line(image2,int(yLowerLeft),int(xLowerLeft),int(yLowerRight),int(xLowerRight),10,490,"Y")
vertical1=Line(image2,int(yUpperLeft),int(xUpperLeft),int(yLowerLeft),int(xLowerLeft),10,490,"X")
lastVertical=Line(image2,int(yUpperRight),int(xUpperRight),int(yLowerRight),int(xLowerRight),10,490,"X")

#creating instances for the lines
#horizontals
horizontalsArray=[]
horizontalsArray.append(horizontal1)
for j in range(0,7):
    horizontalsArray.append(Line(image2, int(corners[j][0][1]),int(corners[j][0][0]),int(corners[j+42][0][1]),int(corners[j+42][0][0]),10,490,"Y"))
horizontalsArray.append(lastHorizontal)
for horizontal in horizontalsArray:
   Line.drawLines(horizontal)
#verticals
indexArray=[0,7,14,21,28,35,42]
verticalsArray=[]
verticalsArray.append(vertical1)
for index in indexArray:
    verticalsArray.append(Line(image2, int(corners[index][0][1]),int(corners[index][0][0]),int(corners[index+6][0][1]),int(corners[index+6][0][0]),10,490,"X"))
verticalsArray.append(lastVertical)
for vertical in verticalsArray:
    Line.drawLines(vertical)

#we'll try to fill the cell array now
for i in range(8):
    for j in range(8):
        interDuet1=findIntersections(horizontalsArray[j], verticalsArray[i],  1, testImage)
        interDuet2=findIntersections(horizontalsArray[j+1], verticalsArray[i+1],  1, testImage)
        duetArray=[interDuet1,interDuet2]
        coordinates.append(duetArray)
#print(coordinates)
#print(len(coordinates))

for i in range(9):
    for j in range(9):
        findIntersections(horizontalsArray[i], verticalsArray[j], 1, image2)
"""
for i in range(9):
    for j in range(9):
        findIntersections(verticalsArray[j], horizontalsArray[i], 1, testImage)
"""
findCell(testImage, "C3")
while True:
    cv2.imshow('board', image2)
    cv2.imshow('coordinates',testImage)
    cv2.imshow('boardcv2',fnl)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
    