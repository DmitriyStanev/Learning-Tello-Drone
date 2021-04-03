import cv2
import mediapipe as mp
import time

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
        landmarkList = []
        if self.results.pose_landmarks:
            print(self.results.pose_landmarks.landmark)
            for id, landmark in enumerate(self.results.pose_landmarks.landmark):
                # print(id, landmark)
                height, width, channel = img.shape
                cx, cy = int(landmark.x * width), int(landmark.y * height)
                landmarkList.append([id, cx, cy])

                if len(landmarkList) > 21:
                    if landmarkList[13][2] > landmarkList[15][2] and (landmarkList[13][2] - landmarkList[11][2] < 10):
                        cv2.putText(img, "Right Hand is Up!", (50, 40), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                    if landmarkList[14][2] > landmarkList[16][2] and (landmarkList[14][2] - landmarkList[12][2] < 10):
                        cv2.putText(img, "Left Hand is Up!", (50, 40), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

                    if abs(landmarkList[19][2] - landmarkList[12][2]) < 8 and abs(landmarkList[20][1] - landmarkList[11][1]) < 8:
                        cv2.putText(img, "XXX Hands Crossed", (100, 440), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)


                    if abs(landmarkList[19][2] - landmarkList[0][2]) < 20 and abs(landmarkList[19][1] - landmarkList[0][1]) < 20 or abs(
                            landmarkList[20][2] - landmarkList[0][2]) < 20 and abs(landmarkList[20][1] - landmarkList[0][1]) < 20:
                        cv2.putText(img, "Na ko mirishi???", (100, 440), cv2.FONT_HERSHEY_PLAIN, 3,
                                    (0, 0, 255), 4)

        return landmarkList

    def checkPosition(self, img, landmarkListXYZ):

        posesDetected = []

        rightHandUpClosed = False
        leftHandUpClosed = False
        crossHands = False
        touchingNose = False
        rightHandUpOpen = False
        leftHandUpOpen = False

        if len(landmarkListXYZ) > 21:
            if landmarkListXYZ[13][2] > landmarkListXYZ[15][2] and (landmarkListXYZ[13][2] - landmarkListXYZ[11][2] < 10):
                rightHandUpClosed = True

            if landmarkListXYZ[14][2] > landmarkListXYZ[16][2] and (landmarkListXYZ[14][2] - landmarkListXYZ[12][2] < 10):
                leftHandUpClosed = True

            if abs(landmarkListXYZ[19][2] - landmarkListXYZ[0][2]) < 8 and abs(landmarkListXYZ[19][1] - landmarkListXYZ[0][1]) < 8:
                touchingNose = True

            if abs(landmarkListXYZ[19][2] - landmarkListXYZ[12][2]) < 8 and abs(
                    landmarkListXYZ[20][1] - landmarkListXYZ[11][1]) < 8:
                crossHands = True

            posesDetected.append(rightHandUpClosed)
            posesDetected.append(leftHandUpClosed)
            posesDetected.append(touchingNose)
            posesDetected.append(crossHands)
            posesDetected.append(rightHandUpOpen)
            posesDetected.append(leftHandUpOpen)

            return posesDetected

def main():
    pTime = 0
    cap = cv2.VideoCapture(0)
    detector = poseDetector()

    while True:
        success, img = cap.read()
        img = detector.findPose(img)
        landmarkList = detector.findPosition(img)
        landmarkListXYZ = detector.findPosition(img)
        posesDetected = detector.checkPosition(img, landmarkListXYZ)

        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime

        cv2.putText(img, str(int(fps)), (10, 70), cv2.FONT_HERSHEY_PLAIN, 3,
                    (255, 0, 255), 3)

        cv2.imshow("MediaPipe Pose", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()