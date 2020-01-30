import cv2
import numpy as np
import time
from adafruit_servokit import ServoKit

import vision


ADDRESS = {0: {'addr_x': 40, 'addr_y': 120, 'prev_count': 40, 'next_address': 101},
           101: {'addr_x': 280, 'addr_y': 65, 'prev_count': 50, 'next_address': 102},
           102: {'addr_x': 40, 'addr_y': 80, 'prev_count': 55, 'next_address': 103},
           103: {'addr_x': 120, 'addr_y': 40, 'prev_count': 70, 'next_address': 203},
           203: {'addr_x': 280, 'addr_y': 80, 'prev_count': 65, 'next_address': 202},
           202: {'addr_x': 80, 'addr_y': 80, 'prev_count': 70, 'next_address': 201}}


class Robot:
    def __init__(self, sio):
        self.status = {'addr': 0, 'status': 'arrived'}
        self.next_address = None

        self.cap = cv2.VideoCapture(0)
        self.kit = ServoKit(channels=16)

        self.sio = sio

    def control(self):
        count, prev_count = 0, 0
        prev_left, prev_right = 0.0, 0.0
        # Here we loop forever to send messages out to the server via the middleware.
        while self.cap.isOpened():
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, (320, 240))

            if self.status['status'] is 'delivering':
                blur = cv2.GaussianBlur(frame, (5, 5), 0)
                hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

                # track line
                lines = vision.find_line(hsv[160:, :])
                angle, shift = vision.calculate_angle(lines)
                left, right = vision.track_line(angle, shift)

                stop_x, stop_y = vision.detect_stop(hsv)
                addr_x, addr_y = vision.detect_address(hsv)
                obstacle_flag = vision.detect_obstacle(lines)

                if left is None or right is None:
                    self.kit.continuous_servo[0].throttle = prev_right
                    self.kit.continuous_servo[1].throttle = prev_left
                else:
                    self.kit.continuous_servo[0].throttle = right
                    self.kit.continuous_servo[1].throttle = left
                    prev_right = right
                    prev_left = left

                if obstacle_flag is True:
                    self.status['status'] = 'obstacle'
                    self.send_message('info', self.status)

                elif stop_y > 210:
                    self.status['status'] = 'arrived'
                    time.sleep(0.5)
                    self.kit.continuous_servo[0].throttle = 0
                    self.kit.continuous_servo[1].throttle = 0
                    # set prev address
                    self.status['addr'] = 0
                    # reset count
                    count, prev_count = 0, 0
                    # send message to operatorUI
                    self.send_message('info', self.status)
                    print("Arrived at stop sign")

                else:
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
                    prev_address = self.status['addr']
                    if prev_address in [101, 203]:
                        if addr_x > ADDRESS[prev_address]['addr_x'] and addr_y > ADDRESS[prev_address]['addr_y'] or prev_count > ADDRESS[prev_address]['prev_count']:
                            if prev_count > 10:
                                self.status['addr'] = ADDRESS[prev_address]['next_address']

                                print("Arrived at %d" % self.status['addr'])
                                print("Addr-x: %d, addr-y: %d" % (addr_x, addr_y))
                                print("frame count %d, prev count %d " % (count, prev_count))

                                prev_count = 0

                                if self.next_address == self.status['addr']:
                                    self.status['status'] = 'arrived'
                                    time.sleep(0.5)
                                    self.kit.continuous_servo[0].throttle = 0
                                    self.kit.continuous_servo[1].throttle = 0

                                self.send_message('info', self.status)

                    elif prev_address in [0, 102, 103, 202]:
                        if addr_x < ADDRESS[prev_address]['addr_x'] and addr_y > ADDRESS[prev_address]['addr_y'] or prev_count > ADDRESS[prev_address]['prev_count']:
                            if prev_count > 10:
                                self.status['addr'] = ADDRESS[prev_address]['next_address']

                                print("Arrived at %d" % self.status['addr'])
                                print("Addr-x: %d, addr-y: %d" % (addr_x, addr_y))
                                print("frame count %d, prev count %d " % (count, prev_count))

                                prev_count = 0

                                if self.next_address == self.status['addr']:
                                    self.status['status'] = 'arrived'
                                    time.sleep(0.5)
                                    self.kit.continuous_servo[0].throttle = 0
                                    self.kit.continuous_servo[1].throttle = 0

                                self.send_message('info', self.status)

                count += 1
                prev_count += 1

            else:
                self.kit.continuous_servo[0].throttle = 0.0
                self.kit.continuous_servo[1].throttle = 0.0

            # 추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            data = np.array(imgencode)
            stringData = data.tostring()

            self.send_message('image', stringData)

            time.sleep(0.01)

    def send_message(self, type, msg):
        if type == 'info':
            self.sio.emit('status', msg)
        elif type == 'image':
            # String 형태로 변환한 이미지를 socket을 통해서 전송
            self.sio.emit('image', msg)
