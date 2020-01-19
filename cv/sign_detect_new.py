import numpy as np
import cv2
import imutils

org_image = cv2.imread("C:/Users/shins/Desktop/temp/stop_sign_519.png")

image = cv2.GaussianBlur(org_image, (5, 5), 0)
image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

#STOP SIGN - RED
def red_mask(image):
    lower_red = np.array([0, 70, 50])
    upper_red = np.array([10, 200, 200])
    mask1 = cv2.inRange(image, lower_red, upper_red)

    lower_red = np.array([170, 70, 50])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(image, lower_red, upper_red)

    mask = mask1+mask2
    obj = "stop"
    return mask, obj

#ADDRESS SIGN - GREEN
def green_mask(image):
    lower_green = np.array([30, 5, 5])
    upper_green = np.array([90, 255, 255])
    mask = cv2.inRange(image, lower_green, upper_green)
    obj = "address"
    return mask, obj

mask, obj = red_mask(image)
output = cv2.bitwise_and(image, image, mask=mask)

h, s, v1 = cv2.split(output)

cnts = cv2.findContours(v1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
cnts = imutils.grab_contours(cnts)

cv2.imshow("images", np.hstack([org_image, output]))
cv2.waitKey(0)


if len(cnts) != 0 :
    cands = []
    for i in range(len(cnts)):
        # if len(cnts[i]) > 30:
        cands.append(len(cnts[i]))  #이미지의 크기
    # print(cands)
    cand = np.asarray(cands)
    max = np.argmax(cand)

    # import pdb
    # pdb.set_trace()
    if len(cnts[max]) < 30:
        cX, cY = None, None
    else:
        M = cv2.moments(cnts[max])
        cX = int((M["m10"] / M["m00"]))
        cY = int((M["m01"] / M["m00"]))
        cv2.drawContours(org_image, [cnts[max]], -1, (0, 255, 0), 2)
        # cv2.drawContours(image, [cnts[0]], -1, (0, 255, 0), 2)
        # epsilon = cv2.arcLength(cnts[max], True)
        # approx = cv2.approxPolyDP(cnts[max], epsilon, True)
        cv2.putText(org_image, obj, (cX - 20, cY - 50), cv2.FONT_HERSHEY_SIMPLEX,
                    0.5, (255, 255, 255), 2)
    cv2.imshow("images", np.hstack([org_image, output]))
    cv2.waitKey(0)
else:
    cX, cY = None, None


