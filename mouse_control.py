import pyautogui
import hands_module
import cv2
import time
import math

cap = cv2.VideoCapture(0)

# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
pTime = 0
#increase the confidence to increase precision
detector = hands_module.handDetect(detectionCnf=0.9)
while True:
    success, img = cap.read()
    img = cv2.flip(img,1)   #웹캠 좌우반전
    img = detector.findHands(img)
    lmlist = detector.findPos(img, draw=False)
    if len(lmlist):
        x1, y1 = lmlist[4][1], lmlist[4][2]  #position of 엄지 끝
        x2, y2 = lmlist[8][1], lmlist[8][2]  #position of 검지 끝
        x3, y3 = lmlist[12][1], lmlist[12][2]   #position of 중지 끝
        cx_left, cy_left = (x1+x2)//2, (y1+y2)//2      #centre of line joining above two pts
        cx_right, cy_right = (x3+x2)//2, (y3+y2)//2  #centre of line joining above two pts
        cv2.line(img, (x1, y1), (x2, y2), (255, 0, 0), 6)
        cv2.line(img, (x1, y1), (x3, y3), (0, 255, 0), 6)    #우클릭
        length_left = math.hypot(x2 - x1, y2 - y1)
        length_right = math.hypot(x3 - x1, y3 - y1)
        # print(length)
        cv2.circle(img, (cx_left, cy_left), 15, (255, 0, 0), cv2.FILLED)
        cv2.circle(img, (cx_right, cy_right), 15, (0, 255, 0), cv2.FILLED)
        pyautogui.moveTo(cx_left * 2, cy_left * 2)    
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