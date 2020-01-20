import cv2
import numpy as np
import socket
import time
import imutils
import threading
from adafruit_servokit import ServoKit


def line_tracking(image):
    # cropped = image[320:480, :]
    cropped = image[160:240, :]
    low_yellow = np.array([20, 65, 65])
    up_yellow = np.array([35, 255, 255])
    mask = cv2.inRange(cropped, low_yellow, up_yellow)
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
                cv2.line(image, (x1, y1 + 160), (x2, y2 + 160), (0, 255, 0), 3)

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

        left = max(0.5 + 0.003 * min(0.0, shift) + 0.4 * min(0.0, angle) / 45.0, 0.1)
        right = min(-0.5 + 0.003 * max(0.0, shift) + 0.38 * max(0.0, angle) / 45.0, -0.1)

        print("Angle: %.2f, Shift: %d, Left: %.4f, Right: %.4f" % (angle, shift, left, -right))

    else:
        left, right = None, None

    return left, right


def sign_detecting(image):
    lower_red = np.array([0, 70, 50])
    upper_red = np.array([10, 200, 200])
    mask1 = cv2.inRange(image, lower_red, upper_red)

    # np.array([160, 100, 150])

    lower_red = np.array([170, 70, 50])
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
            # if len(cnts[i]) > 30:
            cands.append(len(cnts[i]))  # 이미지의 크기
        # print(cands)
        cand = np.asarray(cands)
        max = np.argmax(cand)

        # import pdb
        # pdb.set_trace()
        if len(cnts[max]) < 70:
            cX, cY = None, None
        else:
            M = cv2.moments(cnts[max])
            cX = int((M["m10"] / M["m00"]))
            cY = int((M["m01"] / M["m00"]))
            cv2.drawContours(image, [cnts[max]], -1, (0, 255, 0), 2)
            cv2.putText(image, "stop", (cX - 20, cY - 50), cv2.FONT_HERSHEY_SIMPLEX,
                        0.5, (255, 255, 255), 2)
    else:
        cX, cY = None, None

    return cX, cY


def vision():
    global current_address, stop_flag
    # Here we loop forever to send messages out to the server via the middleware.
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()

        frame = cv2.resize(frame, (320, 240))

        blur = cv2.GaussianBlur(frame, (5, 5), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        left, right = line_tracking(hsv)

        cX, cY = sign_detecting(hsv)

        if cY is not None and cY > 200:
            stop_flag = True
            kit.continuous_servo[0].throttle = 0
            kit.continuous_servo[1].throttle = 0

        if left is not None and stop_flag is False:
            kit.continuous_servo[0].throttle = right
            kit.continuous_servo[1].throttle = left
            # kit.continuous_servo[0].throttle = 0
            # kit.continuous_servo[1].throttle = 0

        # 추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
        encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
        result, imgencode = cv2.imencode('.jpg', frame, encode_param)
        data = np.array(imgencode)
        stringData = data.tostring()

        # String 형태로 변환한 이미지를 socket을 통해서 전송
        imgconn.send(bytes(str(len(stringData)).ljust(16), 'utf8'))
        imgconn.send(stringData)
        time.sleep(0.01)


def delivery():
    global next_address, stop_flag
    while True:
        next_address = destconn.recv(4).decode('ascii')
        if next_address == 'q':
            kit.continuous_servo[0].throttle = 0
            kit.continuous_servo[1].throttle = 0
            cap.release()
            break

        stop_flag = False


if __name__ == "__main__":
    # Get the hostname and IP address of this machine and display it.
    host_name = socket.gethostname()
    host_ip = socket.gethostbyname(socket.gethostname())

    # OperatorUI IP
    operator_ip = "128.237.205.111"

    # Viewer IP
    viewer_ip = "128.237.205.111"

    # image
    cap = cv2.VideoCapture(0)

    # socket for sending resultant image (not necessary to need)
    imgconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    imgconn.connect((viewer_ip, 1024))

    # servo
    kit = ServoKit(channels=16)

    # socket for receiving next destination and sending current address
    destconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destconn.connect((operator_ip, 2048))

    # global variable
    current_address = 0000
    next_address = None
    stop_flag = True

    t1 = threading.Thread(target=vision)
    t2 = threading.Thread(target=delivery)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    imgconn.close()
    destconn.close()
