import cv2
from djitellopy import tello
import mediapipe as mp
import time
import numpy as np

width, height = 480, 360

me = tello.Tello()
me.connect()
print(me.get_battery())

pError = 0

me.streamoff()
me.streamon()
me.takeoff()
me.send_rc_control(0, 0, 25, 0)

class poseDetector():
    def __init__(self, mode=False, upperBodyOnly=False, smoothLandmarks=True,
                 detectionConfidence=0.5, trackingConfidence=0.5):
        self.mode = mode
        self.upperBodyOnly = upperBodyOnly
        self.smoothLandmarks = smoothLandmarks
        self.detectionConfidence = detectionConfidence
        self.trackingConfidence = trackingConfidence
        self.mpPose = mp.solutions.pose
        self.pose = self.mpPose.Pose(self.mode, self.upperBodyOnly, self.smoothLandmarks,
                                     self.detectionConfidence, self.trackingConfidence)
        self.mpDraw = mp.solutions.drawing_utils

    def findPose(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)  ## Pose object uses only RGB images
        self.results = self.pose.process(imgRGB)
        if self.results.pose_landmarks:
            if draw:
                self.mpDraw.draw_landmarks(img, self.results.pose_landmarks,
                                           self.mpPose.POSE_CONNECTIONS)
        return img

    def findPosition(self, img, draw=True):
        landmarkListC = []

        if self.results.pose_landmarks:
            for id, landmark in enumerate(self.results.pose_landmarks.landmark):

                height, width, channel = img.shape
                m1 = int(width / 2)
                m2 = int(height / 3)

                cx, cy = int(landmark.x * width), int(landmark.y * height)
                landmarkListC.append([id, cx, cy])

                if id == 0:
                    cv2.arrowedLine(img, (m1, m2), (cx, cy), (255, 100, 0), 2)
                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)


                if len(landmarkListC) > 21:
                    cv2.putText(img, str((int(width / 2), int(height / 4))), (10, 120), cv2.FONT_HERSHEY_PLAIN, 1,
                                (255, 0, 255), 2)

                    cv2.putText(img, str(landmarkListC[0]), (10, 180), cv2.FONT_HERSHEY_PLAIN, 1,
                                (255, 0, 255), 2)

                    if abs(landmarkListC[19][2] - landmarkListC[12][2]) < 8 and abs(
                            landmarkListC[20][1] - landmarkListC[11][1]) < 8:
                        cv2.putText(img, "XXX Hands Crossed", (100, 440), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 255, 0), 4)

                    if abs(landmarkListC[19][2] - landmarkListC[12][2]) < 8 and abs(landmarkListC[20][1] - landmarkListC[11][1]) < 8:
                        cv2.putText(img, "XXX Hands Crossed", (100, 440), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                    if abs(landmarkListC[19][2] - landmarkListC[0][2]) < 8 and abs(
                            landmarkListC[19][1] - landmarkListC[0][1]) < 8 or abs(
                            landmarkListC[20][2] - landmarkListC[0][2]) < 8 and abs(
                            landmarkListC[20][1] - landmarkListC[0][1]) < 8:
                        cv2.putText(img, "Na ko mirishi???", (100, 440), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                    if landmarkListC[13][2] > landmarkListC[15][2] and (landmarkListC[13][2] - landmarkListC[11][2] < 10):
                        cv2.putText(img, "Left Hand is Up!", (50, 40), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                    if landmarkListC[14][2] > landmarkListC[16][2] and (landmarkListC[14][2] - landmarkListC[12][2] < 10):
                        cv2.putText(img, "Right Hand is Up!", (50, 40), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

        return landmarkListC


    def checkPose(self, img, landmarkListC):

        fb = 0

        posesDetected = {
            'rightHandUpClosed': False,
            'leftHandUpClosed': False,
            'crossHands': False,
            'touchingNose': False,
            'rightHandUpOpen': False,
            'leftHandUpOpen': False
        }

        if len(landmarkListC) > 21:
            if landmarkListC[13][2] > landmarkListC[15][2] and (landmarkListC[13][2] - landmarkListC[11][2] < 10):
                posesDetected['rightHandUpClosed'] = True

            if landmarkListC[14][2] > landmarkListC[16][2] and (landmarkListC[14][2] - landmarkListC[12][2] < 10):
                posesDetected['leftHandUpClosed'] = True

            if abs(landmarkListC[19][2] - landmarkListC[0][2]) < 8 and abs(landmarkListC[19][1] - landmarkListC[0][1]) < 8 or abs(
                            landmarkListC[20][2] - landmarkListC[0][2]) < 8 and abs(landmarkListC[20][1] - landmarkListC[0][1]) < 8:
                posesDetected['touchingNose'] = True

            if abs(landmarkListC[19][2] - landmarkListC[12][2]) < 8 and abs(
                    landmarkListC[20][1] - landmarkListC[11][1]) < 8:
                posesDetected['crossHands'] = True


            if posesDetected['rightHandUpClosed'] == True:
                fb = 20
            if posesDetected['leftHandUpClosed'] == True:
                fb = -20

            me.send_rc_control(0, fb, 0, 0)

            return posesDetected

    def track(self, img, landmarkList, width, pid, pError):

        if len(landmarkList) != 0:
            x = landmarkList[0][1]
            y = landmarkList[0][2]
            ud = 0

            height, width, channel = img.shape
            m1 = int(width / 2)
            m2 = int(height / 3)

            error = x - width // 2
            speed = pid[0] * error + pid[1] * (error - pError)
            speed = int(np.clip(speed, -100, 100))

            if m2 > landmarkList[0][2]:
                ud = 20
            elif m2 < landmarkList[0][2]:
                ud = -20
            # elif x > landmarkList[0][1]:
            #     yaw = -20
            # elif x < landmarkList[0][1]:
            #     yaw = 20

            if x == 0:
                speed = 0
                error = 0

            print('UpDown ---> ', str(ud), 'Speed ---> ', str(speed))
            print(error)

            me.send_rc_control(0, 0, ud, speed)
            return error
        else:
            error = 0
            return error


def main():
    pError = 0
    pTime = 0
    detector = poseDetector()
    pid = [0.4, 0.4, 0]

    while True:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (width, height))
        img = detector.findPose(img)
        landmarkListC = detector.findPosition(img)
        detector.checkPose(img, landmarkListC)
        pError = detector.track(img, landmarkListC, width, pid, pError)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, f' FPS: {int(fps)}', (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("MediaPipe Pose", img)
        cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            me.land()
            break


if __name__ == "__main__":
    main()