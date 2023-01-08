import cv2
import imutils 
#to make basics image processing stuff, turn, edges...
import numpy as np





def preProces(img1, img2): 

    #gray it up and blur as well would be nice
    gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
    blur1 = cv2.GaussianBlur(gray1, (5, 5), 0)
    gray2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)
    blur2 = cv2.GaussianBlur(gray2, (5, 5), 0)

    #absdif this is the image substraction pixel by pixel, it outputs a new picture with only the differences
    diff = cv2.absdiff(blur1, blur2)

    #let's get a proper threshold to better see and understand the absdiff image => if pixel more than x% white turn it white else make it black
    thresh = cv2.threshold(diff,400,500,cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]


    #Dilation -> increase the object area (maybe not a good idea => update: we need it)
    #we need an easier shape this will make it bigger and clearer not just little small dots
    kernel = np.ones((6,6),np.uint8)
    dilate = cv2.dilate(thresh,kernel, iterations=1)

    return gray1, blur1, diff, thresh, dilate

def contours(procImg, Oimg):
    #we'll get contours of every shape
    cnts = cv2.findContours(procImg.copy(),cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)


    
    #what information we need to transfer to the rest of the code
    send =[]

    #now we'll draw all that and get the center
    for c in cnts:
        #we will only consider the shape if it's big enough
        if cv2.contourArea(c)>150:
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            send.append([cX,cY])

            # draw the contour and center of the shape on the image
            cv2.drawContours(Oimg, [c], -1, (0, 255, 0), 2)
            cv2.circle(Oimg, (cX, cY), 2, (255, 0, 0), -1)
            #the 3 int is for the size of the dot
        else:
            M = cv2.moments(c)
            cX = int(M["m10"] / M["m00"])
            cY = int(M["m01"] / M["m00"])
            #this time we don't save the data

            # draw the contour and center of the shape on the image
            cv2.drawContours(Oimg, [c], -1, (0, 0, 255), 2)
            cv2.circle(Oimg, (cX, cY), 2, (255, 0, 0), -1)
            #the 3 int is for the size of the dot

    return Oimg, send



def printDiffInfo(img1, img2,gray, blur, diff, thresh, dilate, finalImg, send, debug):
    #original game
    cv2.imshow("first image", img1)
    cv2.imshow("Second image",img2)


    if debug==1:
        #see steps
        cv2.imshow("gray",gray)
        cv2.imshow("blur",blur)
        cv2.imshow("differences",diff)
        cv2.imshow("diff with thresh", thresh)
        cv2.imshow("after dilatation", dilate)

    #results
    cv2.imshow("results",finalImg)

    cv2.waitKey(0)
    cv2.destroyAllWindows()

    #printing the x,y coordinates
    if send==[]:
        print("there is no differences!")
    else:
        for j in send:
            x=j[0]
            y=j[1]
            print("x : ", x ,"& y : ",y, "\r")
            cv2.circle(img1, (0, 0), 10, (0, 0, 255), -1)
    



### run this code to try it out###

#define size of images:
width = 400
height = 400
#weird but the size seem to change the result of the real case

#import images and resize them
img1 = cv2.imread("data\position0.jpg")
img1 = cv2.resize(img1,(width,height))

img2 = cv2.imread("data\position1.jpg")
img2 = cv2.resize(img2,(width,height))
OriginalImg2=img2.copy()
#just to make sure I can show it at the end!

gray, blur, diff, thresh, dilate = preProces(img1, img2)

finalImg, send = contours(dilate, img2)

print("Do you want to debug and see every processing step? \n 1 for Yes \n 0 for no")
debug = int(input())

printDiffInfo(img1, OriginalImg2,gray, blur, diff, thresh, dilate, finalImg, send, debug)
