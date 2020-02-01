import cv2
import numpy as np
import imutils


def find_line(image):
    low_yellow = np.array([20, 45, 65])
    up_yellow = np.array([35, 255, 255])
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
            shift = 0.0
        elif angle < -45.0:
            angle = -45.0
            shift = 0.0

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
    angles = []
    tops = []
    bots = []
    flag = False

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            bot_angle = np.arctan((y2 - y1) / (x1 - x2)) * 180.0 / np.pi
            # our angle is a deviation from the y axis
            if bot_angle < 0:
                bot_angle = -90.0 - bot_angle
            else:
                bot_angle = 90.0 - bot_angle
            # cv2.line(image, (x1, y1 + 160), (x2, y2 + 160), (0, 255, 0), 3)

            angles.append(np.abs(bot_angle))
            tops.append(min(y1, y2))
            bots.append(max(y1, y2))

        if max(angles) > 65.0 and min(angles) < 30.0:
            if np.abs(tops[np.argmax(angles)] - tops[np.argmin(angles)]) < 20 and np.abs(bots[np.argmax(angles)] - tops[np.argmin(angles)]) < 20:
                flag = True
                print("Obstacle is in the road")
                print(angles)
                print(tops)
                print(bots)

    return flag


def draw_obstacle(image, lines):
    angles = []
    tops = []
    bots = []
    flag = False

    if lines is not None:
        for line in lines:
            x1, y1, x2, y2 = line[0]
            bot_angle = np.arctan((y2 - y1) / (x1 - x2)) * 180.0 / np.pi
            # our angle is a deviation from the y axis
            if bot_angle < 0:
                bot_angle = -90.0 - bot_angle
            else:
                bot_angle = 90.0 - bot_angle
            cv2.line(image, (x1, y1 + 160), (x2, y2 + 160), (0, 255, 0), 3)

            angles.append(np.abs(bot_angle))
            tops.append(min(y1, y2))
            bots.append(max(y1, y2))

        if max(angles) > 70.0 and min(angles) < 10.0:
            if np.abs(tops[np.argmax(angles)] - tops[np.argmin(angles)]) < 10 \
                    and np.abs(bots[np.argmax(angles)] - tops[np.argmin(angles)]) < 10:
                if max(tops) - min(bots) > 0:
                    flag = True

    return image


def detect_stop(image):
    image = image[120:240, :]

    lower_red = np.array([0, 70, 150])
    upper_red = np.array([10, 200, 200])
    mask1 = cv2.inRange(image, lower_red, upper_red)

    # np.array([160, 100, 150])

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
            '''
            cv2.drawContours(image, [cnts[max]], -1, (0, 255, 0), 2)
            cv2.putText(image, "stop", (cX - 20, cY - 50), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)
            '''
    else:
        # not used
        cX, cY = -1, -1

    return cX, cY + 160


def detect_address(image):
    # lower_green = np.array([40, 0, 50])
    # upper_green = np.array([90, 255, 255])
    lower_green = np.array([30, 10, 40])
    upper_green = np.array([100, 100, 200])

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
            '''
            cv2.drawContours(image, [cnts[max]], -1, (0, 255, 0), 2)
            cv2.putText(image, "stop", (cX - 20, cY - 50), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)
            '''
    else:
        cX, cY = -1, -1

    return cX, cY