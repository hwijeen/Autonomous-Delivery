import cv2
import numpy as np
import time
import socket
from sys import *
import threading
from adafruit_servokit import ServoKit


if __name__ == "__main__":
    kit = ServoKit(channels=16)
    cap = cv2.VideoCapture(0)

    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        cropped = frame[320:480, :]

        blur = cv2.GaussianBlur(cropped, (5, 5), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        # low_yellow = np.array([20, 50, 50])
        # up_yellow = np.array([40, 255, 255])
        low_yellow = np.array([20, 65, 65])
        up_yellow = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, low_yellow, up_yellow)
        edges = cv2.Canny(mask, 50, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, maxLineGap=50)
        angle_sum, shift_sum = 0.0, 0.0
        count = 0
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]

                # y1 is under y2
                if y1 > y2:
                    shift_sum += (x1 - 320.0)
                # y2 is under y1
                else:
                    shift_sum += (x2 - 320.0)

                angle = np.arctan((y2 - y1) / (x1 - x2)) * 180.0 / np.pi

                # our angle is a deviation from the y axis
                if angle < 0:
                    angle = -90.0 - angle
                else:
                    angle = 90.0 - angle

                if count != 0 and np.abs(angle - angle_sum / count) > 45.0:
                    angle = 0.0
                else:
                    cv2.line(frame, (x1, y1 + 320), (x2, y2 + 320), (0, 255, 0), 3)

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

            left = max(0.5 + 0.0015 * min(0.0, shift) + 0.4 * min(0.0, angle) / 45.0, 0.1)
            right = min(-0.5 + 0.0015 * max(0.0, shift) + 0.38 * max(0.0, angle) / 45.0, -0.1)

            kit.continuous_servo[0].throttle = right
            kit.continuous_servo[1].throttle = left
            print("Angle: %.2f, Shift: %d, Left: %.4f, Right: %.4f" % (angle, shift, left, -right))
