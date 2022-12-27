import cv2
import imutils 
#to make basics image processing stuff, turn, edges...
import numpy as np

#define size of images:
width = 500
height = 400
#weird but the size seem to change the result of the real case

#import images
img1 = cv2.imread("data\game3.jpg")
img1 = cv2.resize(img1,(width,height))
origin1=img1.copy()



img2 = cv2.imread("data\game4.jpg")
img2 = cv2.resize(img2,(width,height))


#gray it up and blur as well would be nice
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
blur1 = cv2.GaussianBlur(gray1, (5, 5), 0)
gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
blur2 = cv2.GaussianBlur(gray2, (5, 5), 0)

#absdif let's try
diff = cv2.absdiff(blur1, blur2)

#let's get a proper threshhold
thresh = cv2.threshold(diff,0,255,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]



#Dilation -> increase the object area (maybe not a good idea => update we need it)
#en faite on a besoin de faire ça pour que la forme soit plus uniforme et qu'il détecte pas 36000 traits différents
kernel = np.ones((5,5),np.uint8)
dilate = cv2.dilate(thresh,kernel, iterations=1)

#we'll get the contour now
cnts= cv2.findContours(dilate.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)


#now we'll draw all that and get the center
#what we need to transfer to the rest of the code
tot = 4
i=0 #a basic counter
#tot=4 because we have 4 info to transmit but at the end we should just need 2
send = [[],[]]*tot
#a optimser 


for c in cnts:
    M = cv2.moments(c)
    cX = int(M["m10"] / M["m00"])
    cY = int(M["m01"] / M["m00"])
    send[i]=[cX,cY]
    i+=1

    # draw the contour and center of the shape on the image
    cv2.drawContours(img2, [c], -1, (0, 255, 0), 2)
    cv2.circle(img2, (cX, cY), 2, (255, 0, 0), -1)
    #le petit 2 c'est pour la taille du pt




# Everything that we want to show

#original game
cv2.imshow("first image", origin1)
cv2.imshow("Second image",img2)

#see steps

cv2.imshow("gray",gray1)
cv2.imshow("blur",blur1)
cv2.imshow("differences",diff)

#cv2.imshow("diff with thresh", thresh)
cv2.imshow("after dilatation", dilate)
0
#results
cv2.imshow("results",img1)
#printing the x,y coordinates
for j in range(0,tot):
    print("x : ", send[j][0], "& y : ",send[j][1], "\r")
    cv2.circle(img1, (0, 0), 10, (0, 0, 255), -1)

#we just need to send the send array to the main code


cv2.waitKey(0)
cv2.destroyAllWindows()


