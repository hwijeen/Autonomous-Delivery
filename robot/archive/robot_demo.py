import cv2
import numpy as np
import socket
import time
import pickle
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

        # print("Angle: %.2f, Shift: %d, Left: %.4f, Right: %.4f" % (angle, shift, left, -right))

    else:
        left, right = None, None

    return left, right


def sign_detecting(image):
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


def address_detecting(image):
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


def vision():
    global prev_address, next_address
    global stop_flag, mode_flag
    global prev_left, prev_right
    global count, prev_count
    # Here we loop forever to send messages out to the server via the middleware.
    while cap.isOpened():
        # Capture frame-by-frame
        ret, frame = cap.read()
        frame = cv2.resize(frame, (320, 240))

        if mode_flag is False:
            blur = cv2.GaussianBlur(frame, (5, 5), 0)
            hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

            left, right = line_tracking(hsv)
            stop_x, stop_y = sign_detecting(hsv)
            addr_x, addr_y = address_detecting(hsv)

            if stop_flag is True:
                kit.continuous_servo[0].throttle = 0
                kit.continuous_servo[1].throttle = 0
            # when stop_flag is False
            else:
                if stop_y > 200:
                    stop_flag = True
                    time.sleep(0.3)
                    kit.continuous_servo[0].throttle = 0
                    kit.continuous_servo[1].throttle = 0
                    # set prev address
                    prev_address = 0
                    # reset count
                    count, prev_count = 0, 0
                    # send message to operatorUI
                    addrconn.send(pickle.dumps("s"))
                    destconn.send(pickle.dumps(int(prev_address)))
                    print("Arrived at stop sign")

                # check stop value
                '''
                if addr_x > 0.0:
                    print("x position: %.4f, y position: %.4f" % (addr_x, addr_y))
                    stop_flag = True
                    kit.continuous_servo[0].throttle = 0
                    kit.continuous_servo[1].throttle = 0
                    msg = pickle.dumps(int(prev_address))
                    destconn.send(msg)
                '''

                # detect 101
                # (20, 160), (26, 169), (36, 162), (14, 144)
                # counter: (305, 125), (315, 135), (302, 77) / (122, 121)
                # if prev_address == 0 and addr_x > 280 and addr_y > 80:
                if prev_address == 0:
                    if addr_x < 40 and addr_y > 120 or prev_count > 50:
                        if prev_count > 20:
                            print("Arrived at 101")
                            print("Addr-x: %d, addr-y: %d" % (addr_x, addr_y))
                            print("frame count %d, prev count %d " % (count, prev_count))
                            prev_address = 101
                            prev_count = 0
                        if next_address == prev_address:
                            stop_flag = True
                            time.sleep(0.15)
                            kit.continuous_servo[0].throttle = 0
                            kit.continuous_servo[1].throttle = 0
                            addrconn.send(pickle.dumps("s"))
                            destconn.send(pickle.dumps(int(prev_address)))
                # detect 102
                # (245, 41), (279, 44), (267, 46), (292, 41)
                # counter: (6, 126), (16, 126), (10, 126)
                # elif prev_address == 101 and addr_x < 60 and addr_y > 60:
                elif prev_address == 101:
                    if addr_x > 160 and addr_y > 80 or prev_count > 50:
                        if prev_count > 20:
                            print("Arrived at 102")
                            print("Addr-x: %d, addr-y: %d" % (addr_x, addr_y))
                            print("frame count %d, prev count %d " % (count, prev_count))
                            prev_address = 102
                            prev_count = 0
                        if next_address == prev_address:
                            stop_flag = True
                            time.sleep(0.5)
                            kit.continuous_servo[0].throttle = 0
                            kit.continuous_servo[1].throttle = 0
                            addrconn.send(pickle.dumps("s"))
                            destconn.send(pickle.dumps(int(prev_address)))
                # detect 103
                # (19, 173), (19, 158), (29, 152), (21, 157), (18, 152), (12, 155)
                # counter: (288, 123) , (279, 124) (281, 122) / (190, 122), (218, 130), (280, 114)
                # elif prev_address == 102 and addr_x > 300 and addr_y > 120:
                elif prev_address == 102:
                    if addr_x < 40 and addr_y > 120 or prev_count > 55:
                        if prev_count > 10:
                            print("Arrived at 103")
                            print("Addr-x: %d, addr-y: %d" % (addr_x, addr_y))
                            print("frame count %d, prev count %d " % (count, prev_count))
                            prev_address = 103
                            prev_count = 0
                        if next_address == prev_address:
                            stop_flag = True
                            time.sleep(0.15)
                            kit.continuous_servo[0].throttle = 0
                            kit.continuous_servo[1].throttle = 0
                            addrconn.send(pickle.dumps("s"))
                            destconn.send(pickle.dumps(int(prev_address)))
                # detect 203
                # (29, 96), (5, 172)
                # counter: (287, 123), (302, 131), (309, 124), (294, 83)
                # elif prev_address == 103 and addr_x > 290 and addr_y > 120:
                elif prev_address == 103:
                    if addr_x < 80 and addr_y > 40 or prev_count > 70:
                        if prev_count > 20:
                            print("Arrived at 203")
                            print("Addr-x: %d, addr-y: %d" % (addr_x, addr_y))
                            print("frame count %d, prev count %d " % (count, prev_count))
                            prev_address = 203
                            prev_count = 0
                        if next_address == prev_address:
                            stop_flag = True
                            time.sleep(0.15)
                            kit.continuous_servo[0].throttle = 0
                            kit.continuous_servo[1].throttle = 0
                            addrconn.send(pickle.dumps("s"))
                            destconn.send(pickle.dumps(int(prev_address)))
                # detect 202
                # (277, 42), (288, 44), (276, 41), (285, 45)
                # counter: (49, 126), (64, 123), (41, 131), (42, 129)
                # elif prev_address == 203 and addr_x < 80 and addr_y > 100:
                elif prev_address == 203:
                    if addr_x > 280 and addr_y > 80 or prev_count > 65:
                        if prev_count > 20:
                            print("Arrived at 202")
                            print("Addr-x: %d, addr-y: %d" % (addr_x, addr_y))
                            print("frame count %d, prev count %d " % (count, prev_count))
                            prev_address = 202
                            prev_count = 0
                        if next_address == prev_address:
                            stop_flag = True
                            time.sleep(0.5)
                            kit.continuous_servo[0].throttle = 0
                            kit.continuous_servo[1].throttle = 0
                            addrconn.send(pickle.dumps("s"))
                            destconn.send(pickle.dumps(int(prev_address)))
                # detect 201
                # (67, 67), (73, 68), (55, 71), (70, 72)
                # counter: (236, 126), (238, 123), (240, 126)
                # elif prev_address == 202 and addr_y > 120:
                elif prev_address == 202:
                    if addr_x < 80 and addr_y > 40 or prev_count > 70:
                        if prev_count > 20:
                            print("Arrived at 201")
                            print("Addr-x: %d, addr-y: %d" % (addr_x, addr_y))
                            print("frame count %d, prev count %d " % (count, prev_count))
                            prev_address = 201
                            prev_count = 0
                        if next_address == prev_address:
                            stop_flag = True
                            kit.continuous_servo[0].throttle = 0
                            kit.continuous_servo[1].throttle = 0
                            addrconn.send(pickle.dumps("s"))
                            destconn.send(pickle.dumps(int(prev_address)))

                if left is None or right is None:
                    kit.continuous_servo[0].throttle = prev_right
                    kit.continuous_servo[1].throttle = prev_left
                else:
                    kit.continuous_servo[0].throttle = right
                    kit.continuous_servo[1].throttle = left
                    prev_right = right
                    prev_left = left

                count += 1
                prev_count += 1

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
        next_address = pickle.loads(destconn.recv(16))
        if next_address not in [0, 101, 102, 103, 201, 202, 203]:
            print("wrong message")
        else:
            print(next_address)


def receive_mode():
    global mode_flag, stop_flag
    while True:
        # receive message (go / maintenance mode)
        # msg = modeconn.recv(4).decode('ascii')
        msg = pickle.loads(modeconn.recv(16))

        # go mode
        if msg == 'd':
            mode_flag = False
            stop_flag = False
            print("Start delivery")
        # maintenance mode
        elif msg == 'm':
            mode_flag = True
            stop_flag = True
            kit.continuous_servo[0].throttle = 0
            kit.continuous_servo[1].throttle = 0
            time.sleep(1)
            print("Maintenance mode")


if __name__ == "__main__":
    # global variable
    prev_address = 0
    next_address = None
    stop_flag, mode_flag = True, False
    prev_left, prev_right = 0.0, 0.0
    count, prev_count = 0, 0

    # OperatorUI IP# operator_ip = "172.26.220.250" (민석)
    #     # operator_ip = "172.26.213.218" (나)


    # Viewer IP
    viewer_ip = "172.26.213.218"

    # OperatorUI IP
    operator_ip = "172.26.226.35" # (휘진)

    # image
    cap = cv2.VideoCapture(0)

    # servo
    kit = ServoKit(channels=16)

    # socket for receiving mode
    modeconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    modeconn.connect((operator_ip, 60001))

    # socket for sending mode
    addrconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    addrconn.connect((operator_ip, 60002))

    # socket for receiving next destination
    destconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    destconn.connect((operator_ip, 60003))

    # socket for sending image
    imgconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    imgconn.connect((viewer_ip, 60004))

    t1 = threading.Thread(target=vision)
    t2 = threading.Thread(target=delivery)
    t3 = threading.Thread(target=receive_mode)

    t1.start()
    t2.start()
    t3.start()

    t1.join()
    t2.join()
    t3.join()

    modeconn.close()
    addrconn.close()
    destconn.close()
    imgconn.close()
