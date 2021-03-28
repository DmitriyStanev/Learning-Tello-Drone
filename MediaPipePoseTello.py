import cv2
from djitellopy import tello
import mediapipe as mp
import time

width, height = 480, 360

me = tello.Tello()
me.connect()
print(me.get_battery())

me.streamoff()
me.streamon()
# me.takeoff()
# me.send_rc_control(0, 0, 25, 0)

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
        landmarkListXYZ = []
        if self.results.pose_landmarks:
            print(self.results.pose_landmarks.landmark)
            for id, landmark in enumerate(self.results.pose_landmarks.landmark):

                height, width, channel = img.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                print("ID ---> ", id, "CX ---> ", cx, "CY ---> ", cy)
                if id == 0:
                    cv2.arrowedLine(img, (int(width / 2), int(height / 4)), (cx, cy), (255, 100, 0), 2)






                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)

                x, y, z = landmark.x * 100, landmark.y * 100, landmark.z * 100
                landmarkListXYZ.append([id, int(x), int(y), int(z)])

                # if id == 11 or id == 13 or id == 15 or id == 17 or id == 19 or id == 21:
                #     cv2.putText(img, str(landmarkListXYZ[id]), (3*id, 7*id), cv2.FONT_HERSHEY_PLAIN, 1, (255, 0, 255), 2)

                # if id == 0:
                #     cv2.putText(img, str(landmarkListXYZ[id]), (50, 180), cv2.FONT_HERSHEY_PLAIN, 1,
                #                 (0, 0, 255), 2)
                #
                # if id == 11:
                #     cv2.putText(img, str(landmarkListXYZ[id]), (50, 200), cv2.FONT_HERSHEY_PLAIN, 2,
                #                 (255, 0, 0), 2)
                # if id == 13:
                #     cv2.putText(img, str(landmarkListXYZ[id]), (50, 250), cv2.FONT_HERSHEY_PLAIN, 2,
                #                 (255, 0, 0), 2)
                #
                if len(landmarkListXYZ) > 21:
                    cv2.putText(img, str((int(width / 2), int(height / 4))), (10, 120), cv2.FONT_HERSHEY_PLAIN, 1,
                                (255, 0, 255), 2)
                    cv2.putText(img, str(landmarkListXYZ[0]), (10, 80), cv2.FONT_HERSHEY_PLAIN, 1,
                                (255, 0, 255), 1)
                    cv2.putText(img, str(cx), (10, 100), cv2.FONT_HERSHEY_PLAIN, 2,
                                (255, 0, 255), 1)
                    cv2.putText(img, str(cy), (100, 100), cv2.FONT_HERSHEY_PLAIN, 2,
                                (255, 0, 255), 1)
                    # cv2.putText(img, str(landmarkListXYZ[0]), (10, 80), cv2.FONT_HERSHEY_PLAIN, 1,
                    #             (255, 0, 255), 2)
                    # cv2.putText(img, str(landmarkListXYZ[20]), (10, 120), cv2.FONT_HERSHEY_PLAIN, 1,
                    #             (255, 0, 255), 2)

                    if abs(landmarkListXYZ[19][2] - landmarkListXYZ[12][2]) < 8 and abs(
                            landmarkListXYZ[20][1] - landmarkListXYZ[11][1]) < 8:
                        cv2.putText(img, "XXX Hands Crossed", (100, 440), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                    if abs(landmarkListXYZ[19][2] - landmarkListXYZ[0][2]) < 8 and abs(
                            landmarkListXYZ[19][1] - landmarkListXYZ[0][1]) < 8 or abs(
                            landmarkListXYZ[20][2] - landmarkListXYZ[0][2]) < 8 and abs(
                            landmarkListXYZ[20][1] - landmarkListXYZ[0][1]) < 8:
                        cv2.putText(img, "Na ko mirishi???", (100, 440), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                    if landmarkListXYZ[13][2] > landmarkListXYZ[15][2] and (landmarkListXYZ[13][2] - landmarkListXYZ[11][2] < 10):
                        cv2.putText(img, "Right Hand is Up!", (50, 40), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                    if landmarkListXYZ[14][2] > landmarkListXYZ[16][2] and (landmarkListXYZ[14][2] - landmarkListXYZ[12][2] < 10):
                        cv2.putText(img, "Left Hand is Up!", (50, 40), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                #
                #
                # # if id == 0:
                # #     cv2.circle(img, (cx, cy), 13, (255, 0, 255), cv2.FILLED)

                # cv2.circle(img, (int(width/2), int(height/4)), 13, (0, 255, 0), 2, cv2.FILLED) ## Here should be the center of the face


        # return landmarkList, landmarkListXYZ
        return landmarkListXYZ

    def checkPose(self, img, landmarkListXYZ):

        posesDetected = {
            "rightHandUpClosed" : False,
            "leftHandUpClosed" : False,
            "crossHands" : False,
            "touchingNose" : False,
            "rightHandUpOpen" : False,
            "leftHandUpOpen" : False
        }

        if len(landmarkListXYZ) > 21:
            if landmarkListXYZ[13][2] > landmarkListXYZ[15][2] and (landmarkListXYZ[13][2] - landmarkListXYZ[11][2] < 10):
                posesDetected["rightHandUpClosed"] = True

            if landmarkListXYZ[14][2] > landmarkListXYZ[16][2] and (landmarkListXYZ[14][2] - landmarkListXYZ[12][2] < 10):
                posesDetected["leftHandUpClosed"] = True

            if abs(landmarkListXYZ[19][2] - landmarkListXYZ[0][2]) < 8 and abs(landmarkListXYZ[19][1] - landmarkListXYZ[0][1]) < 8 or abs(
                            landmarkListXYZ[20][2] - landmarkListXYZ[0][2]) < 8 and abs(landmarkListXYZ[20][1] - landmarkListXYZ[0][1]) < 8:
                posesDetected["touchingNose"] = True

            if abs(landmarkListXYZ[19][2] - landmarkListXYZ[12][2]) < 8 and abs(
                    landmarkListXYZ[20][1] - landmarkListXYZ[11][1]) < 8:
                posesDetected["crossHands"] = True


            # return posesDetected

def main():
    pTime = 0
    cTime = 0
    cap = cv2.VideoCapture(0)
    detector = poseDetector()

    while True:
        img = me.get_frame_read().frame
        img = cv2.resize(img, (width, height))
        # battery = me.get_battery()
        # cv2.putText(img, ("Battery:  " + me.get_battery()), (20, 20), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 1)

        img = detector.findPose(img)
        landmarkList = detector.findPosition(img)
        landmarkListXYZ = detector.findPosition(img)
        # posesDetected = detector.checkPosition(img, landmarkListXYZ)
        detector.checkPose(img, landmarkListXYZ)

        # if len(landmarkListXYZ) != 0:
        #     print(landmarkListXYZ[11], landmarkListXYZ[13], landmarkListXYZ[15], landmarkListXYZ[17], landmarkListXYZ[19], landmarkListXYZ[21], )

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("MediaPipe Pose", img)
        cv2.waitKey(1)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            me.land()
            break


if __name__ == "__main__":
    main()