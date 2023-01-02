import cv2 as cv
import cvzone
from cvzone.ColorModule import ColorFinder

import numpy as np


def get_parabola_points(points, coeff):
    width = int(capture.get(cv.CAP_PROP_FRAME_WIDTH))
    x = [i for i in range(width)]
    y = [int(coeff[0]*i**2 + coeff[1]*i + coeff[2]) for i in x]
    return np.stack([x,y], axis=1)



capture = cv.VideoCapture(1)

color_finder = ColorFinder(trackBar=False)
ball_HSV_mask_vals = {'hmin': 0, 'smin': 125, 'vmin': 145, 'hmax': 10, 'smax': 255, 'vmax': 255}
rim_HSV_mask_vals = {'hmin': 0, 'smin': 59, 'vmin': 180, 'hmax': 5, 'smax': 103, 'vmax': 239}


prev_pos_points = []


while True:
    success, original = capture.read()
    
    # Find location of rim
    frame = original.copy()
    
    frame, mask = color_finder.update(frame, rim_HSV_mask_vals)
    
    kernel = np.ones((2,4), np.uint8)
    frame = cv.dilate(frame, kernel, iterations=12)
    
    frame = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
    
    ret, frame = cv.threshold(frame, 0, 255, cv.THRESH_BINARY)
    
    frame, rim_contours = cvzone.findContours(frame, frame, minArea=400)

    if rim_contours:
        rect_coords = rim_contours[0]['bbox']
        x,y,w,h = rect_coords
        frame = cv.rectangle(original, (x,y),(x+w,y+h),(0,255,0), 2)
    else:
        frame = original
        
    
    # Find location of the ball
    masked_img, mask = color_finder.update(frame, ball_HSV_mask_vals)
    
    kernel = np.ones((2,4), np.uint8)
    frame = cv.dilate(frame, kernel, iterations=3)
    
    frame, contours = cvzone.findContours(masked_img, mask, minArea=400)
    
    if contours:
        ball_center_pos = contours[0]['center']
        prev_pos_points.append(ball_center_pos)
    else:
        prev_pos_points = []
        
    for point in prev_pos_points:
        original = cv.circle(original, point, 10, (0, 255, 0), -1)
        
    # Polynomial regression
    if len(prev_pos_points) > 1:
        # if prev_pos_points[-1][1] > prev_pos_points[-2][1]:
        coeff = np.polyfit(list(map(lambda pt: pt[0], prev_pos_points)),
                        list(map(lambda pt: pt[1], prev_pos_points)),
                        2)
        parabola_points = get_parabola_points(prev_pos_points, coeff)
        for point in parabola_points:
            original = cv.circle(original, point, 3, (255, 0, 255), -1)
    
        
        
    # Determine make or miss
    if rim_contours and len(prev_pos_points) > 1:
        rim_height = y + (h/2)
        rim_start = x
        rim_end = x+w
        ball_pts_at_rim_xs = [parabola_points[i] for i in range(rim_start+int(w/4), rim_end-int(w/4))]
        for point in ball_pts_at_rim_xs:
            original = cv.circle(original, (point), 10, (255, 0, 0), -1)
        
        if len(prev_position_points) < 4:
            made = False
            for point in ball_pts_at_rim_xs:
                if abs(point[1] - rim_height) < h/2:
                    made = True
                    break
                    
        if made:
            original = cv.putText(original, 'Make', (20,75), cv.FONT_HERSHEY_SIMPLEX, 2.5, (0,255,0), 2, cv.LINE_AA)
        else:
            original = cv.putText(original, 'Miss', (20,75), cv.FONT_HERSHEY_SIMPLEX, 2.5, (0,0,255), 2, cv.LINE_AA)
        
        
    cv.imshow('Video', original)
    
    if cv.waitKey(4) & 0xFF==ord('s'):
        break
    
capture.release()
cv.destroyAllWindows()
