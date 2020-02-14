import cv2
import numpy as np
import imutils


def preprocess(image):
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    return hsv


def find_line(image):
    image = image[160:, :]
    # low_yellow = np.array([20, 50, 200])
    # up_yellow = np.array([35, 200, 255])
    low_yellow = np.array([20, 0, 180])
    up_yellow = np.array([35, 200, 255])
    mask = cv2.inRange(image, low_yellow, up_yellow)
    edges = cv2.Canny(mask, 50, 150)
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 25, maxLineGap=25)

    return lines


def calculate_angle(lines):
    angle_sum, shift_sum = 0.0, 0.0
    count = 0
    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]

            # y1 is under y2
            if y1 > y2:
                shift_sum += (x1 - 160.0)
            # y2 is under y1
            else:
                shift_sum += (x2 - 160.0)

            angle = np.arctan((y2 - y1) / (x1 - x2)) * 180.0 / np.pi

            # our angle is a deviation from the y axis
            if angle < 0:
                angle = -90.0 - angle
            else:
                angle = 90.0 - angle

            if count != 0 and np.abs(angle - angle_sum / count) > 45.0:
                angle = 0.0

            angle_sum += angle
            count += 1

        angle = angle_sum / count
        shift = shift_sum / count

        if angle > 45.0:
            angle = 45.0
        elif angle < -45.0:
            angle = -45.0

    else:
        angle, shift = None, None

    return angle, shift


def track_line(angle, shift):
    if angle is not None:
        left = max(0.5 + 0.003 * min(0.0, shift) + 0.4 * min(0.0, angle) / 45.0, 0.1)
        right = min(-0.5 + 0.003 * max(0.0, shift) + 0.38 * max(0.0, angle) / 45.0, -0.1)
    else:
        left, right = None, None

    return left, right


def detect_obstacle(lines):
    flag = False

    if lines is None:
        return True

    return flag


def detect_stop(image):
    image = image[120:, :]

    lower_red = np.array([0, 70, 150])
    upper_red = np.array([10, 200, 200])
    mask1 = cv2.inRange(image, lower_red, upper_red)

    lower_red = np.array([170, 70, 150])
    upper_red = np.array([180, 255, 255])
    mask2 = cv2.inRange(image, lower_red, upper_red)

    mask = mask1 + mask2
    output = cv2.bitwise_and(image, image, mask=mask)

    h, s, v1 = cv2.split(output)

    cnts = cv2.findContours(v1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    if len(cnts) != 0:
        cands = []
        for i in range(len(cnts)):
            cands.append(len(cnts[i]))  # 이미지의 크기
        cand = np.asarray(cands)
        max = np.argmax(cand)

        if len(cnts[max]) < 70:
            # not used
            cX, cY = -1, -1
        else:
            M = cv2.moments(cnts[max])
            cX = int((M["m10"] / M["m00"]))
            cY = int((M["m01"] / M["m00"]))
    else:
        # not used
        cX, cY = -1, -1

    return cX, cY + 120


def detect_address(image):
    # lower_green = np.array([40, 0, 50])
    # upper_green = np.array([90, 255, 255])
    lower_green = np.array([30, 0, 40])
    upper_green = np.array([100, 100, 150])

    mask = cv2.inRange(image, lower_green, upper_green)
    output = cv2.bitwise_and(image, image, mask=mask)

    h, s, v1 = cv2.split(output)

    cnts = cv2.findContours(v1.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    cnts = imutils.grab_contours(cnts)

    if len(cnts) != 0:
        cands = []
        for i in range(len(cnts)):
            cands.append(len(cnts[i]))  # 이미지의 크기
        cand = np.asarray(cands)
        max = np.argmax(cand)

        if len(cnts[max]) < 30:
            cX, cY = -1, -1
        else:
            M = cv2.moments(cnts[max])
            cX = int((M["m10"] / M["m00"]))
            cY = int((M["m01"] / M["m00"]))

    else:
        cX, cY = -1, -1

    return cX, cY
