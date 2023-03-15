import pyautogui
from hands_module import HandDetector
import cv2
import time
import math

cap = cv2.VideoCapture(0)


# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
pTime = 0
#increase the confidence to increase precision
detector = HandDetector(detectionCon=0.9, maxHands=2)

while True:
    success, img = cap.read()
    img = cv2.flip(img,1)   #웹캠 좌우반전
    hands, img = detector.findHands(img, flipType=True)

    
    if hands:
        # Hand 1
        hand1 = hands[0]
        lmList1 = hand1["lmList"]  # List of 21 Landmark points
        bbox1 = hand1["bbox"]  # Bounding box info x,y,w,h
        centerPoint1 = hand1['center']  # center of the hand cx,cy
        handType1 = hand1["type"]  # Handtype Left or Right

        if handType1 == "Right":
            length_left, _, img = detector.findDistance(lmList1[4][0:2], lmList1[8][0:2], img)  #좌클릭, 엄지 검지 거리
            length_right, _, img = detector.findDistance(lmList1[4][0:2], lmList1[12][0:2], img) #우클릭, 엄지 중지 거리
            length_center, info, img = detector.findDistance(lmList1[0][0:2], lmList1[9][0:2], img) #마우스 이동, 손바닥 중심
            # pyautogui.moveTo(lmList1[4][1] * 3, lmList1[4][1] * 2.25)
            if length_left <= 20:
                pyautogui.leftClick()
            if length_right <= 30:
                pyautogui.rightClick()

            pyautogui.moveTo(info[4] * 3, info[5] * 2.25)
            cv2.circle(img, (info[4], info[5]), 15, (255, 0, 0), cv2.FILLED) 
                
        if len(hands) == 2:
            # Hand 2
            hand2 = hands[1]
            lmList2 = hand2["lmList"]  # List of 21 Landmark points
            bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
            centerPoint2 = hand2['center']  # center of the hand cx,cy
            handType2 = hand2["type"]  # Hand Type "Left" or "Right"

            if handType1 == "Right":
                length_left, _, img = detector.findDistance(lmList1[4][0:2], lmList1[8][0:2], img)  #좌클릭, 엄지 검지 거리
                length_right, _, img = detector.findDistance(lmList1[4][0:2], lmList1[12][0:2], img) #우클릭, 엄지 중지 거리
                length_center, info, img = detector.findDistance(lmList1[0][0:2], lmList1[9][0:2], img) #마우스 이동, 손바닥 중심

                if length_left <= 20:
                    pyautogui.leftClick()
                if length_right <= 30:
                    pyautogui.rightClick()

                pyautogui.moveTo(info[4] * 3, info[5] * 2.25)
                cv2.circle(img, (info[4], info[5]), 15, (255, 0, 0), cv2.FILLED) 
            
            elif handType2 == "Right":

                
                length_left, _, img = detector.findDistance(lmList2[4][0:2], lmList2[8][0:2], img)  #좌클릭, 엄지 검지 거리
                length_right, _, img = detector.findDistance(lmList2[4][0:2], lmList2[12][0:2], img) #우클릭, 엄지 중지 거리
                length_center, info, img = detector.findDistance(lmList2[0][0:2], lmList2[9][0:2], img) #마우스 이동, 손바닥 중심
                pyautogui.moveTo(info[4] * 3, info[5] * 2.25)
                cv2.circle(img, (info[4], info[5]), 15, (255, 0, 0), cv2.FILLED)
                if length_left <= 20:
                    pyautogui.leftClick()
                if length_right <= 30:
                    pyautogui.rightClick()

    cTime = time.time()
    if cTime != pTime:
        fps = 1 / (cTime - pTime)
    else:
        fps = 0
    pTime = cTime
    #displaying fps
    cv2.putText(img, f'FPS:{int(fps)}', (40, 70),
                cv2.FONT_HERSHEY_COMPLEX, 2, (255, 0, 0), 4)
    #displaying final image
    cv2.imshow('WebCam', img)
    cv2.waitKey(1)
    
#     if cv2.waitKey(1) & 0xFF == 27:     # esc로 종료
#         break

# cv2.destroyAllWindows()