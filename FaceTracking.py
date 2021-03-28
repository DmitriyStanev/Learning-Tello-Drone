import cv2
from djitellopy import tello
import numpy as np

width, height = 360, 240
fbRange = [6200, 6800] ###Forward and backward range
pid = [0.4, 0.4, 0]
pError = 0

me = tello.Tello()
me.connect()
print(me.get_battery())

me.streamon()
me.takeoff()
me.send_rc_control(0, 0, 25, 0)

def findFace(img):
    faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceListCenter = []
    myFaceListArea = []

    for (x, y, width, height) in faces: ##Drawing the rectangle around the face
        cv2.rectangle(img, (x, y), (x+width, y+height), (255, 0, 0), 2)
        ## Finding the center of image
        cx = x + width // 2
        cy = y + height // 2
        area = width * height
        cv2.circle(img, (cx, cy), 5, (0, 255, 0), cv2.FILLED)
        myFaceListCenter.append([cx, cy])
        myFaceListArea.append(area)

    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListCenter[i], myFaceListArea[i]]
    else:
        return img, [[0, 0], 0]

def trackFace(me, info, width, pid, pError):
    area = info[1]
    x, y = info[0]
    fb = 0

    error = x - width // 2
    speed = pid[0] * error + pid[1] * (error - pError)
    speed = int(np.clip(speed, -100, 100))

    if area > fbRange[0] and area < fbRange[1]:
        fb = 0
    elif area > fbRange[1]:
        fb = -20
    elif area < fbRange[0] and area != 0:
        fb = 20
    # elif area == 0:
    #     me.rotate_clockwise(360) # If there's no face detected, drone is rotating to find one.

    if x == 0:
        speed = 0
        error = 0

    me.send_rc_control(0, fb, 0, speed)
    return error

while True:

    # cap = cv2.VideoCapture(0)
    # _, img = cap.read()

    img = me.get_frame_read().frame
    img = cv2.resize(img, (width, height))
    img, info = findFace(img)
    battery = me.get_battery()
    # cv2.putText(img, ("Battery:  " + me.get_battery()), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)
    pError = trackFace(me, info, width, pid, pError)
    cv2.imshow("Output", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        me.land()
        break