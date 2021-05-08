import numpy as np
import cv2

cap = cv2.VideoCapture("video.mp4")
ret, frame = cap.read()
shape = frame.shape
# Define the codec and create VideoWriter object
# fourcc = cv2.CV_FOURCC(*'DIVX')
# out = cv2.VideoWriter('output.avi',fourcc, 20.0, (640,480))

codec = cv2.VideoWriter_fourcc(*'XVID')
out = cv2.VideoWriter('output2.mp4', codec, 30.0, (shape[1],shape[0]))

# out = cv2.VideoWriter('output.avi', -1, 20.0, (640,480))

while(cap.isOpened()):
    # print("open")
    if ret==True:
        # frame = cv2.flip(frame,0)

        # write the flipped frame
        out.write(frame) 

        # cv2.imshow('frame',frame)
        # if cv2.waitKey(100) & 0xFF == ord('q'):
        #     break
    else:
        break
    
    # print(frame.shape)
    ret, frame = cap.read()

# Release everything if job is finished
cap.release()
out.release()
cv2.destroyAllWindows()

print('video saved')