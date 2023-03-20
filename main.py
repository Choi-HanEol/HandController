import cv2
import numpy as np
import time
import HandTrackingModule as ht
import autopy   # Install using "pip install autopy"
import pyautogui
from ctypes import cast, POINTER
import math
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

# from autopy.mouse import RIGHT_BUTTON
# from autopy.mouse import LEFT_BUTTON, RIGHT_BUTTON

### Variables Declaration
pTime = 0               # Used to calculate frame rate
width = 640             # Width of Camera
height = 480            # Height of Camera
frameR = 100            # Frame Rate
smoothening = 8         # Smoothening Factor
prev_x, prev_y = 0, 0   # Previous coordinates
curr_x, curr_y = 0, 0   # Current coordinates


# cap.set(cv2.CAP_PROP_FRAME_WIDTH, 320)
cap = cv2.VideoCapture(0)   # Getting video feed from the webcam
cap.set(3, width)           # Adjusting size
cap.set(4, height)
#increase the confidence to increase precision
detector = ht.HandDetector(maxHands=2)                  # Detecting one hand at max
screen_width, screen_height = autopy.screen.size()      # Getting the screen size

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(
    IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
volRange = volume.GetVolumeRange()

minVol = volRange[0]
maxVol = volRange[1]


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
        
        # cv2.rectangle(img, (frameR, frameR), (width - frameR, height - frameR), (255, 0, 255), 2)   # Creating boundary box
        if handType1 == "Right":
            length_left, _, img = detector.findDistance(lmList1[4][0:2], lmList1[8][0:2], img)  #좌클릭, 엄지 검지 거리
            length_right, _, img = detector.findDistance(lmList1[4][0:2], lmList1[12][0:2], img) #우클릭, 엄지 중지 거리
            length_center, info, img = detector.findDistance(lmList1[0][0:2], lmList1[9][0:2], img) #마우스 이동, 손바닥 중심
            
            x3 = np.interp(info[4], (frameR,width-frameR), (0,screen_width))
            y3 = np.interp(info[5], (frameR, height-frameR), (0, screen_height))

            curr_x = prev_x + (x3 - prev_x)/smoothening
            curr_y = prev_y + (y3 - prev_y) / smoothening
            autopy.mouse.move(curr_x, curr_y)
            prev_x, prev_y = curr_x, curr_y
            
            # pyautogui.moveTo(lmList1[4][1] * 3, lmList1[4][1] * 2.25)
            if length_left <= 20:
                pyautogui.leftClick()
            if length_right <= 30:
                pyautogui.rightClick()
            cv2.circle(img, (info[4], info[5]), 15, (255, 0, 0), cv2.FILLED) 
        elif handType1 == "Left":
            x1, y1 = lmList1[4][0], lmList1[4][1]
            x2, y2 = lmList1[8][0], lmList1[8][1]
            x3, y3 = lmList1[12][0], lmList1[12][1]
            x4, y4 = lmList1[16][0], lmList1[16][1]
            x5, y5 = lmList1[20][0], lmList1[20][1]
            p1, p2 = lmList1[9][0], lmList1[9][1]
            cx, cy = (x1 + x2 + x3 + x4 + x5) // 5, (y1 + y2 + y3 + y4 + y5) // 5

            h2 = math.hypot(p1 - x2, p2 - y2)
            c2 = round(math.acos((p1 - x2) / h2) * (180 / math.pi))

            resultVolume = round(volume.GetMasterVolumeLevelScalar() * 100)
            cv2.putText(img, f'{int(resultVolume)}%', (40, 40),
                        cv2.FONT_HERSHEY_COMPLEX, 1, (250, 0, 0), 3)
            
            cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
            
            vol = np.interp(c2, [65, 180], [maxVol, minVol])  # 손의 범위를, 볼륨 범위로 변경해주는 것.
            volume.SetMasterVolumeLevel(vol, None)
             
        if len(hands) == 2:
            # Hand 2
            hand2 = hands[1]
            lmList2 = hand2["lmList"]  # List of 21 Landmark points
            bbox2 = hand2["bbox"]  # Bounding box info x,y,w,h
            centerPoint2 = hand2['center']  # center of the hand cx,cy
            handType2 = hand2["type"]  # Hand Type "Left" or move"Right"

            if handType1 == "Right":
                length_left, _, img = detector.findDistance(lmList1[4][0:2], lmList1[8][0:2], img)  #좌클릭, 엄지 검지 거리
                length_right, _, img = detector.findDistance(lmList1[4][0:2], lmList1[12][0:2], img) #우클릭, 엄지 중지 거리
                length_center, info, img = detector.findDistance(lmList1[0][0:2], lmList1[9][0:2], img) #마우스 이동, 손바닥 중심

                x3 = np.interp(info[4], (frameR,width-frameR), (0,screen_width))
                y3 = np.interp(info[5], (frameR, height-frameR), (0, screen_height))

                curr_x = prev_x + (x3 - prev_x)/smoothening
                curr_y = prev_y + (y3 - prev_y) / smoothening
                autopy.mouse.move(curr_x, curr_y)  
                prev_x, prev_y = curr_x, curr_y
                
                if length_left <= 20:
                    pyautogui.leftClick()
                if length_right <= 30:
                    pyautogui.rightClick()

                cv2.circle(img, (info[4], info[5]), 15, (255, 0, 0), cv2.FILLED)
                
                ## 볼륨
                x1, y1 = lmList2[4][0], lmList2[4][1]
                x2, y2 = lmList2[8][0], lmList2[8][1]
                x3, y3 = lmList2[12][0], lmList2[12][1]
                x4, y4 = lmList2[16][0], lmList2[16][1]
                x5, y5 = lmList2[20][0], lmList2[20][1]
                p1, p2 = lmList2[9][0], lmList2[9][1]
                cx, cy = (x1 + x2 + x3 + x4 + x5) // 5, (y1 + y2 + y3 + y4 + y5) // 5

                h2 = math.hypot(p1 - x2, p2 - y2)
                c2 = round(math.acos((p1 - x2) / h2) * (180 / math.pi))

                resultVolume = round(volume.GetMasterVolumeLevelScalar() * 100)
                cv2.putText(img, f'{int(resultVolume)}%', (40, 40),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (250, 0, 0), 3)
                
                cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
                
                vol = np.interp(c2, [65, 180], [maxVol, minVol])  # 손의 범위를, 볼륨 범위로 변경해주는 것.
                volume.SetMasterVolumeLevel(vol, None)
            
            elif handType2 == "Right":
                length_left, _, img = detector.findDistance(lmList2[4][0:2], lmList2[8][0:2], img)  #좌클릭, 엄지 검지 거리
                length_right, _, img = detector.findDistance(lmList2[4][0:2], lmList2[12][0:2], img) #우클릭, 엄지 중지 거리
                length_center, info, img = detector.findDistance(lmList2[0][0:2], lmList2[9][0:2], img) #마우스 이동, 손바닥 중심
                
                x3 = np.interp(info[4], (frameR,width-frameR), (0,screen_width))
                y3 = np.interp(info[5], (frameR, height-frameR), (0, screen_height))

                curr_x = prev_x + (x3 - prev_x)/smoothening
                curr_y = prev_y + (y3 - prev_y) / smoothening
                autopy.mouse.move(curr_x, curr_y)
                prev_x, prev_y = curr_x, curr_y
                
                cv2.circle(img, (info[4], info[5]), 15, (255, 0, 0), cv2.FILLED)
                if length_left <= 20:
                    pyautogui.leftClick()
                if length_right <= 30:
                    pyautogui.rightClick()
                    
                ##볼륨
                x1, y1 = lmList1[4][0], lmList1[4][1]
                x2, y2 = lmList1[8][0], lmList1[8][1]
                x3, y3 = lmList1[12][0], lmList1[12][1]
                x4, y4 = lmList1[16][0], lmList1[16][1]
                x5, y5 = lmList1[20][0], lmList1[20][1]
                p1, p2 = lmList1[9][0], lmList1[9][1]
                cx, cy = (x1 + x2 + x3 + x4 + x5) // 5, (y1 + y2 + y3 + y4 + y5) // 5

                h2 = math.hypot(p1 - x2, p2 - y2)
                c2 = round(math.acos((p1 - x2) / h2) * (180 / math.pi))

                resultVolume = round(volume.GetMasterVolumeLevelScalar() * 100)
                cv2.putText(img, f'{int(resultVolume)}%', (40, 40),
                            cv2.FONT_HERSHEY_COMPLEX, 1, (250, 0, 0), 3)
                
                cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
                
                vol = np.interp(c2, [65, 180], [maxVol, minVol])  # 손의 범위를, 볼륨 범위로 변경해주는 것.
                volume.SetMasterVolumeLevel(vol, None)

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