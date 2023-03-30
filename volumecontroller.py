# import HandTrackingModule as ht
from lib import *
        
##볼륨
def vol_controller(lmList, volume, volRange, img):
    minVol = volRange[0]
    maxVol = volRange[1]
    
    x1, y1 = lmList[4][0], lmList[4][1]
    x2, y2 = lmList[8][0], lmList[8][1]
    x3, y3 = lmList[12][0], lmList[12][1]
    x4, y4 = lmList[16][0], lmList[16][1]
    x5, y5 = lmList[20][0], lmList[20][1]
    p1, p2 = lmList[9][0], lmList[9][1]
    cx, cy = (x1 + x2 + x3 + x4 + x5) // 5, (y1 + y2 + y3 + y4 + y5) // 5

    h2 = math.hypot(p1 - x2, p2 - y2)
    c2 = round(math.acos((p1 - x2) / h2) * (180 / math.pi))

    resultVolume = round(volume.GetMasterVolumeLevelScalar() * 100)
    cv2.putText(img, f'{int(resultVolume)}%', (40, 40),
                cv2.FONT_HERSHEY_COMPLEX, 1, (250, 0, 0), 3)
    
    cv2.circle(img, (cx, cy), 15, (255, 0, 0), cv2.FILLED)
    
    vol = np.interp(c2, [65, 180], [maxVol, minVol])  # 손의 범위를, 볼륨 범위로 변경해주는 것.
    volume.SetMasterVolumeLevel(vol, None)