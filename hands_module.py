import mediapipe as mp
import cv2
# import time


class handDetect():
    def __init__(self, mode=False, maxHands=2, complexity=1, detectionCnf=0.5, trackCnf=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.complexity = complexity
        self.detectionCnf = detectionCnf
        self.trackCnf = trackCnf

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(
            self.mode, self.maxHands, self.complexity, self.detectionCnf, self.trackCnf)
        self.mpDraw = mp.solutions.drawing_utils

    def findHands(self, img, draw=True):
        imgRgb = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRgb)
        if self.results.multi_hand_landmarks:
            for handLms in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(
                        img, handLms, self.mpHands.HAND_CONNECTIONS)

        return img

    def findPos(self, img, handNo=0, draw=True):
        lmlist = []
        if self.results.multi_hand_landmarks:
            myhand = self.results.multi_hand_landmarks[handNo]
            for id, lm in enumerate(myhand.landmark):
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmlist.append([id, cx, cy])
                
        return lmlist


def main():
    cap = cv2.VideoCapture(0)
    detector = handDetect()
    while True:
        succes, img = cap.read()
        img = detector.findHands(img)
        lmlist = detector.findPos(img)
        if len(lmlist)!=0:
            print(lmlist[0])
        cv2.imshow("Image", img)
        cv2.waitKey(1)


if __name__ == "__main__":
    main()