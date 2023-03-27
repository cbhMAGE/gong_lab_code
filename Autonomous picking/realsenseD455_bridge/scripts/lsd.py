import cv2
import numpy as np
img = cv2.imread('scripts/rgb.jpg')
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
# depth = cv2.imread('scripts/depth.jpg')
depth = np.load('scripts/depth.npy')
# print(depth[440][320])   mm
# print(img.shape)      480 640 3
# print(depth.shape)     480 640
lsd = cv2.ximgproc.createFastLineDetector()
lines = lsd.detect(gray)   
# print(lines.shape) 828 1 4 
new_lines = []
for dline in lines:
    x0 = int(round(dline[0][0]))     
    y0 = int(round(dline[0][1])) 
    d0 = depth[y0][x0]   
    x1 = int(round(dline[0][2]))     
    y1 = int(round(dline[0][3]))   
    d1 = depth[y1][x1] 
    # if d1<1500 and d0<1500 and d1>0 and d0>0:  
    # #abs(d1-d0)<100 and 
    if d1==0:
        new_lines.append(dline)
        cv2.line(img, (x0, y0), (x1,y1), 255, 1, cv2.LINE_AA) 
#drawn_img = lsd.drawSegments(img,lines)
cv2.imshow("lsd",img)
cv2.waitKey(0)
 
# for dline in dlines[0]:     
#     x0 = int(round(dline[0][0]))     
#     y0 = int(round(dline[0][1]))    
#     x1 = int(round(dline[0][2]))     
#     y1 = int(round(dline[0][3]))     
#     cv2.line(img, (x0, y0), (x1,y1), 255, 1, cv2.LINE_AA) 

# cv2.imwrite('./lines.png', img)

