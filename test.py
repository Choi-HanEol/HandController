import cv2
 
cap = cv2.VideoCapture(0)
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print('original size: %d, %d' % (width, height))
 
# cap.set(cv2.CAP_PROP_FRAME_WIDTH, width/3)
# cap.set(cv2.CAP_PROP_FRAME_HEIGHT, height/3)
 
width = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
height = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)
print('changed size: %d, %d' % (width, height))
while True:
    success, img = cap.read()
    cv2.imshow('WebCam', img)
    cv2.waitKey(1)