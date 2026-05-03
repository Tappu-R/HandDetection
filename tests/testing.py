import numpy as np
import cv2

sheet = np.zeros((200,200), dtype=np.uint16)

for i in range(1,4,2):
    sheet = cv2.line(sheet, (20,4), (54,99),(0,255,0),3)

cv2.imshow('tset', sheet)
cv2.waitKey(0)
cv2.destroyAllWindows()

