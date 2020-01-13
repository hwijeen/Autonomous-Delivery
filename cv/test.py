import cv2
import numpy as np
import time
import socket
from sys import *
import threading
from adafruit_servokit import ServoKit


def thread1():
    # Here we loop forever to send messages out to the server via the middleware.
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        # frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        # frame = frame[120:360, 160:480]

        cropped = frame[320:480, :]

        blur = cv2.GaussianBlur(cropped, (5, 5), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        low_yellow = np.array([15, 40, 40])
        up_yellow = np.array([30, 255, 255])
        mask = cv2.inRange(hsv, low_yellow, up_yellow)
        edges = cv2.Canny(mask, 50, 150)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 50, maxLineGap=50)
        angle_sum, shift_sum = 0.0, 0.0
        left, right = 0.0, 0.0
        count = 0
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(frame, (x1, y1 + 320), (x2, y2 + 320), (0, 255, 0), 5)

                if y1 > y2:
                    angle = np.arctan((y2 - y1)/(x1 - x2)) * 180.0 / np.pi
                    shift_sum += (x1 - 320.0)
                else:
                    angle = np.arctan((y1 - y2)/(x2 - x1)) * 180.0 / np.pi
                    shift_sum += (x2 - 320.0)

                if angle < 0:
                    angle = -90.0 - angle
                else:
                    angle = 90.0 - angle
                angle_sum += angle
                count += 1

            angle = angle_sum / count
            shift = shift_sum / count

            if -75.0 < angle <= 0.0:
                if angle < -45.0:
                    angle = -45.0
                if shift < -40.0:
                    # turn left more
                    left = -0.4 + 0.001 * min(0.0, shift + 120)
                    right = 0.3 + 0.3 * angle / 50.0
                elif shift > 40.0:
                    # turn left less
                    left = -0.4 + 0.001 * max(0.0, shift - 120)
                    right = 0.5 + 0.3 * angle / 50.0
                else:
                    # turn left smoothly
                    left = -0.4
                    right = 0.4 + 0.3 * angle / 50.0
            elif 0.0 < angle < 75.0:
                if angle > 45.0:
                    angle = 45.0
                if shift < -40.0:
                    # turn right less
                    left = -0.5 + 0.3 * angle / 50.0
                    right = 0.4 + 0.001 * min(0.0, shift + 120)
                elif shift > 40.0:
                    # turn right more
                    left = -0.3 + 0.3 * angle / 50.0
                    right = 0.4 + 0.001 * max(00.0, shift - 120)
                else:
                    # turn right smoothly
                    left = -0.4 + 0.3 * angle / 50.0
                    right = 0.4

            kit.continuous_servo[0].throttle = left
            kit.continuous_servo[1].throttle = right
            print("Angle: %.2f, Shift: %d, Left: %.4f, Right: %.4f" % (angle, shift, left, right))

        '''
        else:
            kit.continuous_servo[0].throttle = 0
            kit.continuous_servo[1].throttle = 0
        '''
        # 추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()

        # String 형태로 변환한 이미지를 socket을 통해서 전송
        imgconn.send(bytes(str(len(stringData)).ljust(16), 'utf8'))
        imgconn.send(stringData)
        # print('send data')


def thread2():
    while True:
        key_data = keyconn.recv(4).decode('ascii')
        # keyconn.send(msg.encode('ascii'))
        print("Keyboard input:", key_data)

        if key_data == "w":
            kit.continuous_servo[0].throttle = -1
            kit.continuous_servo[1].throttle = 1
            # kit.continuous_servo[0].throttle = 1
            # kit.continuous_servo[1].throttle = -1
        elif key_data == "s":
            kit.continuous_servo[0].throttle = 1
            kit.continuous_servo[1].throttle = -1
            # kit.continuous_servo[0].throttle = -1
            # kit.continuous_servo[1].throttle = 1
        elif key_data == "a":
            kit.continuous_servo[0].throttle = -0.8
            kit.continuous_servo[1].throttle = -0.2
            # kit.continuous_servo[0].throttle = -0.2
            # kit.continuous_servo[1].throttle = -1
        elif key_data == "d":
            kit.continuous_servo[0].throttle = 0.2
            kit.continuous_servo[1].throttle = 0.8
            # kit.continuous_servo[0].throttle = 1
            # kit.continuous_servo[1].throttle = 0.2
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
