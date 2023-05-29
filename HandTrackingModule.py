
"""
Hand Tracking Module
By: Computer Vision Zone
Website: https://www.computervision.zone/
"""

from lib import *
import mediapipe as mp
from tensorflow.keras.models import load_model

class HandDetector:
    """
    Finds Hands using the mediapipe library. Exports the landmarks
    in pixel format. Adds extra functionalities like finding how
    many fingers are up or the distance between two fingers. Also
    provides bounding box info of the hand found.
    """

    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, minTrackCon=0.5):
        """
        :param mode: In static mode, detection is done on each image: slower
        :param maxHands: Maximum number of hands to detect
        :param detectionCon: Minimum Detection Confidence Threshold
        :param minTrackCon: Minimum Tracking Confidence Threshold
        """
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = detectionCon
        self.minTrackCon = minTrackCon

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode, max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.minTrackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.tipIds = [4, 8, 12, 16, 20]
        self.fingers = []
        self.lmList = []

    def findHands(self, img, draw=True, flipType=True):
        """
        Finds hands in a BGR image.
        :param img: Image to find the hands in.
        :param draw: Flag to draw the output on the image.
        :return: Image with or without drawings
        """
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)
        allHands = []
        
        h, w, c = img.shape
        if self.results.multi_hand_landmarks:
            for handType, handLms in zip(self.results.multi_handedness, self.results.multi_hand_landmarks):
                myHand = {}
                ## lmList
                mylmList = []
                xList = []
                yList = []
                for id, lm in enumerate(handLms.landmark):
                    px, py, pz = int(lm.x * w), int(lm.y * h), int(lm.z * w)
                    mylmList.append([px, py, pz])
                    xList.append(px)
                    yList.append(py)
                ## bbox
                xmin, xmax = min(xList), max(xList)
                ymin, ymax = min(yList), max(yList)
                boxW, boxH = xmax - xmin, ymax - ymin
                bbox = xmin, ymin, boxW, boxH
                cx, cy = bbox[0] + (bbox[2] // 2), \
                         bbox[1] + (bbox[3] // 2)

                myHand["lmList"] = mylmList
                myHand["bbox"] = bbox
                myHand["center"] = (cx, cy)

                if flipType:
                    if handType.classification[0].label == "Right":
                        myHand["type"] = "Right"
                    else:
                        myHand["type"] = "Left"
                else:
                    myHand["type"] = handType.classification[0].label
                allHands.append(myHand)

                ## draw
                if draw:
                    self.mpDraw.draw_landmarks(img, handLms,
                                               self.mpHands.HAND_CONNECTIONS)
                    cv2.rectangle(img, (bbox[0] - 20, bbox[1] - 20),
                                  (bbox[0] + bbox[2] + 20, bbox[1] + bbox[3] + 20),
                                  (255, 0, 255), 2)
                    cv2.putText(img, myHand["type"], (bbox[0] - 30, bbox[1] - 30), cv2.FONT_HERSHEY_PLAIN,
                                2, (255, 0, 255), 2)
            # print(len(self.results.multi_hand_landmarks))
        if draw:
            return allHands, img
        else:
            return allHands


    def findGesture(self, img, actions, seq_length, model, seq, action_seq, handlen):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.result = self.hands.process(imgRGB)
        this_action = ' '
        con = False
        if self.result.multi_hand_landmarks is not None:
            for res in self.result.multi_hand_landmarks:
                if handlen == 1 and con == False:
                    con = True
                    continue
                joint = np.zeros((21, 4))
                
                for j, lm in enumerate(res.landmark):
                    joint[j] = [lm.x, lm.y, lm.z, lm.visibility]

                # Compute angles between joints
                v1 = joint[[0 ,1 ,2 ,3 ,0 ,5 ,6 ,7 ,0 ,9 ,10 ,11 ,0 ,13 ,14 ,15 ,0 ,17 ,18 ,19], :3] # Parent joint
                v2 = joint[[1 ,2 ,3 ,4 ,5 ,6 ,7 ,8 ,9 ,10 ,11 ,12 ,13 ,14 ,15 ,16 ,17 ,18 ,19 ,20], :3] # Child joint
                v = v2 - v1 # [20, 3]
                # Normalize v
                v = v / np.linalg.norm(v, axis=1)[:, np.newaxis]

                # Get angle using arcos of dot product
                angle = np.arccos(np.einsum('nt,nt->n',
                                            v[[0 ,1 ,2 ,4 ,5 ,6 ,8 ,9 ,10 ,12 ,13 ,14 ,16 ,17 ,18] ,:],
                                            v[[1 ,2 ,3 ,5 ,6 ,7 ,9 ,10 ,11 ,13 ,14 ,15 ,17 ,18 ,19] ,:])) # [15,]

                angle = np.degrees(angle) # Convert radian to degree

                d = np.concatenate([joint.flatten(), angle])

                seq.append(d)

                # self.mpDraw.draw_landmarks(img, res, self.mpHands.HAND_CONNECTIONS)

                if len(seq) < seq_length:
                    continue

                input_data = np.expand_dims(np.array(seq[-seq_length:], dtype=np.float32), axis=0)

                y_pred = model.predict(input_data).squeeze()

                i_pred = int(np.argmax(y_pred))
                conf = y_pred[i_pred]

                if conf < 0.9:
                    continue

                action = actions[i_pred]
                action_seq.append(action)

                if len(action_seq) < 3:
                    continue

                this_action = '?'
                if action_seq[-1] == action_seq[-2] == action_seq[-3]:
                    this_action = action

                cv2.putText(img, f'{this_action.upper()}', org=(int(res.landmark[0].x * img.shape[1]), int(res.landmark[0].y * img.shape[0] + 20)), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=1, color=(255, 255, 255), thickness=2)
                if handlen == 0:
                    break
                
        return this_action, img, actions, seq_length, model, seq, action_seq


    def fingersUp(self, myHand):
        """
        Finds how many fingers are open and returns in a list.
        Considers left and right hands separately
        :return: List of which fingers are up
        """
        myHandType = myHand["type"]
        myLmList = myHand["lmList"]
        if self.results.multi_hand_landmarks:
            fingers = []
            # Thumb
            if myHandType == "Right":
                if myLmList[self.tipIds[0]][0] > myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)
            else:
                if myLmList[self.tipIds[0]][0] < myLmList[self.tipIds[0] - 1][0]:
                    fingers.append(1)
                else:
                    fingers.append(0)

            # 4 Fingers
            for id in range(1, 5):
                if myLmList[self.tipIds[id]][1] < myLmList[self.tipIds[id] - 2][1]:
                    fingers.append(1)
                else:
                    fingers.append(0)
        return fingers

    def findDistance(self, p1, p2, img=None):
        """
        Find the distance between two landmarks based on their
        index numbers.
        :param p1: Point1
        :param p2: Point2
        :param img: Image to draw on.
        :param draw: Flag to draw the output on the image.
        :return: Distance between the points
                 Image with output drawn
                 Line information
        """

        x1, y1 = p1
        x2, y2 = p2
        cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
        length = math.hypot(x2 - x1, y2 - y1)
        info = (x1, y1, x2, y2, cx, cy)
        if img is not None:
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            cv2.circle(img, (x2, y2), 15, (255, 0, 255), cv2.FILLED)
            cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), 3)
            cv2.circle(img, (cx, cy), 15, (255, 0, 255), cv2.FILLED)
            return length, info, img
        else:
            return length, info


# def main():
#     cap = cv2.VideoCapture(0)
#     detector = HandDetector(detectionCon=0.8, maxHands=2)
#     while True:
#         # Get image frame
#         success, img = cap.read()
#         # Find the hand and its landmarks
#         hands, img = detector.findHands(img)  # with draw
#         # hands = detector.findHands(img, draw=False)  # without draw

#         if hands:
#             # Hand 1
#             hand1 = hands[0]
#             lmList1 = hand1["lmList"]  # List of 21 Landmark points
#             bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
#             centerPoint1 = hand1['center']  # center of the hand cx,cy
#             handType1 = hand1["type"]  # Handtype Left or Right

#             fingers1 = detector.fingersUp(hand1)

#             if len(hands) == 2:
#                 # Hand 2
#                 hand2 = hands[1]
#                 lmList2 = hand2["lmList"]  # List of 21 Landmark points
#                 bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
#                 centerPoint2 = hand2['center']  # center of the hand cx,cy
#                 handType2 = hand2["type"]  # Hand Type "Left" or "Right"

#                 fingers2 = detector.fingersUp(hand2)

#                 # Find Distance between two Landmarks. Could be same hand or different hands
#                 length, info, img = detector.findDistance(lmList1[8][0:2], lmList2[8][0:2], img)  # with draw
#                 # length, info = detector.findDistance(lmList1[8], lmList2[8])  # with draw
#         # Display
#         cv2.imshow("Image", img)
#         cv2.waitKey(1)


# if __name__ == "__main__":
#     main()