import cv2
import numpy as np
import time
import socket
from sys import *
import threading
from adafruit_servokit import ServoKit


def thread1():
    prev_angle = 0.0
    # Here we loop forever to send messages out to the server via the middleware.
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()

        frame = cv2.resize(frame, (320, 240))

        cropped = frame[160:240, :]

        blur = cv2.GaussianBlur(cropped, (5, 5), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        low_yellow = np.array([20, 65, 65])
        up_yellow = np.array([35, 255, 255])
        mask = cv2.inRange(hsv, low_yellow, up_yellow)
        edges = cv2.Canny(mask, 50, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 25, maxLineGap=25)
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
                else:
                    cv2.line(frame, (x1, y1 + 160), (x2, y2 + 160), (0, 255, 0), 3)

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
            '''
            if np.abs(angle - prev_angle) > 45.0:
                angle = prev_angle
            '''

            left = max(0.5 + 0.003 * min(0.0, shift) + 0.4 * min(0.0, angle) / 45.0, 0.1)
            right = min(-0.5 + 0.003 * max(0.0, shift) + 0.38 * max(0.0, angle) / 45.0, -0.1)

            kit.continuous_servo[0].throttle = right
            kit.continuous_servo[1].throttle = left
            print("Angle: %.2f, Shift: %d, Left: %.4f, Right: %.4f" % (angle, shift, left, -right))

            prev_angle = angle

        # 추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()

        # String 형태로 변환한 이미지를 socket을 통해서 전송
        imgconn.send(bytes(str(len(stringData)).ljust(16), 'utf8'))
        imgconn.send(stringData)


def thread2():
    while True:
        key_data = keyconn.recv(4).decode('ascii')

        if key_data == "w":
            kit.continuous_servo[0].throttle = -1
            kit.continuous_servo[1].throttle = 1
        elif key_data == "s":
            kit.continuous_servo[0].throttle = 1
            kit.continuous_servo[1].throttle = -1
        elif key_data == "a":
            kit.continuous_servo[0].throttle = -0.8
            kit.continuous_servo[1].throttle = 0.2
        elif key_data == "d":
            kit.continuous_servo[0].throttle = -0.2
            kit.continuous_servo[1].throttle = 0.8
        elif key_data == "x":
            kit.continuous_servo[0].throttle = 0
            kit.continuous_servo[1].throttle = 0
        elif key_data == "q":
            kit.continuous_servo[0].throttle = 0
            kit.continuous_servo[1].throttle = 0
            cap.release()
            break


if __name__ == "__main__":
    # Get the hostname and IP address of this machine and display it.
    host_name = socket.gethostname()

    try:
        host_ip = socket.gethostbyname(socket.gethostname())
        # On many linux systems, this always gives 127.0.0.1. Hence...
    except:
        host_ip = ''

    if not host_ip or host_ip.startswith('127.'):
        # Now we get the address the hard way.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('4.2.2.1', 0))
        host_ip = s.getsockname()[0]

    print("Robot Hostname:: ", host_name)
    print("Server IP:: ", host_ip)

    if len(argv) == 2:
        ConnectTo = argv[1]  # robot_demos.py IP address
        print("Connecting to: ", argv[1])
    else:
        ConnectTo = host_ip  # connect to local host
        print("Connecting to: localhost")

    # image
    # cap = cv2.VideoCapture('../ar_source.mov')
    cap = cv2.VideoCapture(0)

    imgconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    imgconn.connect((ConnectTo, 1024))

    # servo
    kit = ServoKit(channels=16)

    keyconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    keyconn.connect((ConnectTo, 2048))

    t1 = threading.Thread(target=thread1)
    t2 = threading.Thread(target=thread2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("finished")

    imgconn.close()
    keyconn.close()
