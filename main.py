from lib import *
import HandTrackingModule as ht
import volumecontroller as vc
import autopy   # Install using "pip install autopy"
import pyautogui
from ctypes import cast, POINTER
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
            vc.vol_controller(lmList1, volume, volRange, img)
             
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
                vc.vol_controller(lmList2, volume, volRange, img)
            
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
                vc.vol_controller(lmList1, volume, volRange, img)

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