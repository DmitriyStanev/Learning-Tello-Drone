import cv2
import sys
import numpy as np
from cv2 import Tracker

def findFace(img):
    faceCascade = cv2.CascadeClassifier("Resources/haarcascade_frontalface_default.xml")
    imgGray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    faces = faceCascade.detectMultiScale(imgGray, 1.2, 8)

    myFaceListCenter = []
    myFaceListArea = []

    for (x, y, w, h) in faces:
        cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
        cx = x + w // 2
        cy = y + h // 2
        area = w * h
        cv2.circle(img, (cx, cy), 4, (0, 0, 255), cv2.FILLED)
        myFaceListCenter.append([cx, cy])
        myFaceListArea.append(area)
        # box = (x, y, w, h)
        # tracker = cv2.TrackerCSRT_create()
        # tracker.init(img, box)
        # tracker.update(img)

        # tracker = cv2.TrackerCSRT_create()
        # tracker = cv2.TrackerMIL_create()
        # video = cv2.VideoCapture(0)
        # if not video.isOpened():
        #     print("Could not open video...")
        #     sys.exit()
        # ok, frame = video.read()
        # bbox = (287, 23, 86, 320)
        # bbox = cv2.selectROI(frame, False)
        # ok = tracker.init(frame, bbox)


    if len(myFaceListArea) != 0:
        i = myFaceListArea.index(max(myFaceListArea))
        return img, [myFaceListCenter[i], myFaceListArea[i]]
    else:
        return img, [[0], [0], 0]

cap = cv2.VideoCapture(0)

while True:
    _, img = cap.read()
    img, info = findFace(img)
    print("Area ---> ", info[1], "Center --->", info[0])
    cv2.imshow("Detection + Tracking", img)
    cv2.waitKey(1)
