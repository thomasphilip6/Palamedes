import cv2
import numpy as np
from PIL import Image
from numpy import asarray


letters=["A","B","C","D","E","F","G","H"]
numbers=["1","2","3","4","5","6","7","8"]
cells=[]

for letter in letters:
    for number in numbers:
        cells.append(letter + number)

nline = 7
ncol = 7

class Line:
    def __init__(self, image, yB, xB, yA, xA, coordinate1, wanted):
        self.image=image
        self.yB=yB
        self.xB=xB
        self.yA=yA
        self.xA=xA
        self.coordinate1=coordinate1
        self.wanted=wanted

    def getSlope(self):
        slope=(self.yB-self.yA)/(self.xB-self.xA)
        return slope
    
    def originParam(self):
        originParam=self.yB-self.getSlope()*self.xB
        return originParam

    def getY(self):
        Y=int(self.getSlope()*self.coordinate1 + self.originParam())
        X=int(self.coordinate1)
        return X,Y
    def getX(self):
        X=(self.coordinate1-self.originParma())/self.getSlope()
        Y=int(self.coordinate1)
        return X,Y

    def drawLines(self):
        if self.wanted=='X':
            (x,y)=self.getX()
        if self.wanted=='Y':
            (x,y)=self.getY()
        cv2.line(self.image, (int(self.xB),int(self.yB)) , (x,y), (0,255,255),2 )

def calibrationChessBoard(image, nline, ncol):
    resizedImage=np.array(image.resize((400,400)))
    grayImage = cv2.cvtColor(resizedImage,cv2.COLOR_BGR2GRAY)
    retval, corners = cv2.findChessboardCorners(grayImage, (nline, ncol), None)
    lowerLeft=(int(corners[0][0][0]-approx),int(corners[0][0][1]+approx))
    upperRight=(int(corners[int(nline*ncol-1)][0][0]+approx),int(corners[int(nline*ncol-1)][0][1]-approx))

    if (retval):
        print("board detected")
    else:
        print("no board detected")

    fnl = cv2.drawChessboardCorners(grayImage, (nline, ncol), corners, retval)
    while cv2.waitKey(1) & 0xff != ord('n'):
        cv2.imshow("calibration before augmentation", image2)
        cv2.imshow("exact calibration", fnl)
        cv2.rectangle(image2,upperLeft,bottomRight,(0,0,255),3)
        
approx=0

image2=np.array(Image.open('thirdTest.jpeg').resize((400,400)))
grayImage = cv2.cvtColor(image2,cv2.COLOR_BGR2GRAY)

retval, corners = cv2.findChessboardCorners(grayImage, (nline, ncol), None)
lowerLeft=(int(corners[0][0][0]-approx),int(corners[0][0][1]+approx))
upperRight=(int(corners[48][0][0]+approx),int(corners[48][0][1]-approx))
print(corners[48][0][0])
print(corners[48][0][1])
if (retval):
    print("there is a board")
else:
    print("no board")
print(retval)
print(corners)
fnl = cv2.drawChessboardCorners(grayImage, (nline, ncol), corners, retval)

Diag1=Line(image2, int(corners[0][0][1]), int(corners[0][0][0]), int(corners[48][0][1]), int(corners[48][0][0]), 350, "Y" )   
Line.drawLines(Diag1) 

while True:
    cv2.imshow("board2", fnl)
    cv2.imshow("board", image2)
    #cv2.rectangle(image2,lowerLeft,upperRight,(0,0,255),3)
    cv2.circle(image2, (int(corners[0][0][0]),int(corners[0][0][1])),5,(0,255,0),3)#green
    cv2.circle(image2, (int(corners[1][0][0]),int(corners[1][0][1])),5,(0,255,255),3)#yellow
    cv2.circle(image2, (int(corners[6][0][0]),int(corners[6][0][1])),5,(255,255,0),3)#blue
    cv2.circle(image2, (int(corners[48][0][0]),int(corners[48][0][1])),5,(0,0,255),3)#red
    if cv2.waitKey(1) & 0xff == ord('q'):
        break


