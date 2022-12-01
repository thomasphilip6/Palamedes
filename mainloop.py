import cv2
import numpy as np
import serial

width=640
height=360
fakeHeight=360+120 #used to debug a strange problem with thomas's webcam

servoValue=""
stepper1Value=""
stepper2Value=""
stepper3Value=""
command=""

#connection for the arduino
# 12 for the mega and 8 for the nano
ser = serial.Serial('COM11', baudrate = 9600, timeout = 3 ) #pyserial as to be connected within 3 seconds

#cam settings
cam=cv2.VideoCapture(0,cv2.CAP_DSHOW)
cam.set(cv2.CAP_PROP_FRAME_WIDTH, width)
cam.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
cam.set(cv2.CAP_PROP_FPS, 30)
cam.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc(*'MJPG'))

def sendMotorsInstructions(servoValue, stepper1Value, stepper2Value, stepper3Value):
    command= servoValue + ':' + stepper1Value + ':' + stepper2Value + ':' +stepper3Value + '\r'
    ser.write(command.encode())

while True:
    ignore, frame = cam.read()
    cv2.imshow('my WEBcam', frame)
    cv2.moveWindow('my WEBcam',0,0)
    if cv2.waitKey(1) & 0xff == ord('q'):
        break
cam.release()