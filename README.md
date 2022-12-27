# Basketball Shot Predictor Using cvzone/opencv
This is a python project which tracks both a basketball and a rim and predicts if the shot will go through the rim. 

## Computer Vision
the ball and rim are isolated from the background video using HSV color masking
```
ball_HSV_mask_vals = {'hmin': 0, 'smin': 125, 'vmin': 145, 'hmax': 10, 'smax': 255, 'vmax': 255}
rim_HSV_mask_vals = {'hmin': 0, 'smin': 59, 'vmin': 180, 'hmax': 5, 'smax': 103, 'vmax': 239}
```
and then have binarization and dilation applied them. They are then detected through cvzones's ```findContours()``` function which returns the locations of all the contours, as well as a rectangle that surrounds them.
