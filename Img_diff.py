import cv2
import imutils 
#to make basics image processing stuff, turn, edges...
import numpy as np

#import images
img1 = cv2.imread("game3.jpg")
img1 = cv2.resize(img1,(600,400))
cv2.imshow("first image",img1)
img2 = cv2.imread("game4.jpg")
img2 = cv2.resize(img2,(600,400))


#gray it up and blur as well would be nice
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
blur1 = cv2.GaussianBlur(gray1, (5, 5), 0)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
blur2 = cv2.GaussianBlur(gray2, (5, 5), 0)

"""
cv2.imshow("original",img1)
cv2.imshow("gray",gray1)
cv2.imshow("blur",blur1)
"""

#absdif let's try
diff = cv2.absdiff(blur1, blur2)

#let's get a proper threshhold
thresh = cv2.threshold(diff, 0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]
#thresh2 = cv2.adaptiveThreshold(diff,255,cv2.ADAPTIVE_THRESH_GAUSSIAN_C,cv2.THRESH_BINARY,1,2)


#Dilation -> increase the object area (maybe not a good idea)
#en faite on a besoin de faire ça pour que la forme soit plus uniforme 
kernel = np.ones((5,5),np.uint8)
dilate = cv2.dilate(thresh,kernel, iterations=1)
#cv2.imshow("thresh1", dilate)
#dilate = cv2.dilate(thresh2,kernel, iterations=1)
#cv2.imshow("thresh2", dilate)
#cv2.imshow("Dilation",dilate)

#we'll get the contour now
cnts= cv2.findContours(dilate.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)
#print("that's the cnts: ", cnts)

#now we'll draw all that and get the center
i=0
ptx = [[],[]]*4
pty= [[],[]]*4
#deso c'est degeu mais efficace
for c in cnts:
    #print(c)
    #print(cnts)
    M = cv2.moments(c)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    ptx[i]=cX
    pty[i]=cY
    
    #print("X",i,"=",cX)
    #print("Y",i,"=",cY)
    i+=1


    # draw the contour and center of the shape on the image
    cv2.drawContours(img1, [c], -1, (0, 255, 0), 2)
    cv2.circle(img1, (cX, cY), 2, (255, 0, 0), -1)
    #le petit 2 c'est pour la taille du pt

for j in range(0,i):
    print("x : ", ptx[j], "& y : ",pty[j], "\r")
    cv2.circle(img1, (0, 0), 10, (0, 0, 255), -1)
#print("my little i=",i)

cv2.imshow("first",img1)
#cv2.imshow("second",img2)
cv2.imshow("diff", diff)
cv2.imshow("thresh try", thresh) 
#cv2.imshow("thresh gaus", thresh2) 

cv2.waitKey(0)
cv2.destroyAllWindows()


