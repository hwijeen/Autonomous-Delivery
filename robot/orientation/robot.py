import cv2
import numpy as np
import time
from adafruit_servokit import ServoKit

import vision


ADDRESS = {0: {'addr_x': 40, 'addr_y': 160, 'prev_count': 30, 'next_address': 101},
           101: {'addr_x': 270, 'addr_y': 115, 'prev_count': 45, 'next_address': 102},
           102: {'addr_x': 40, 'addr_y': 130, 'prev_count': 45, 'next_address': 103},
           103: {'addr_x': 120, 'addr_y': 130, 'prev_count': 65, 'next_address': 203},
           203: {'addr_x': 280, 'addr_y': 120, 'prev_count': 50, 'next_address': 202},
           202: {'addr_x': 80, 'addr_y': 140, 'prev_count': 50, 'next_address': 201}}


REV_ADDRESS = {0: {'addr_x': 240, 'addr_y': 135, 'prev_count': 30, 'next_address': 201},
               201: {'addr_x': 50, 'addr_y': 120, 'prev_count': 50, 'next_address': 202},
               202: {'addr_x': 280, 'addr_y': 140, 'prev_count': 45, 'next_address': 203},
               203: {'addr_x': 210, 'addr_y': 165, 'prev_count': 67, 'next_address': 103},
               103: {'addr_x': 20, 'addr_y': 110, 'prev_count': 45, 'next_address': 102},
               102: {'addr_x': 300, 'addr_y': 140, 'prev_count': 45, 'next_address': 101}}


class Robot:
    def __init__(self, sio):
        self.status = {'latest_addr': 0, 'status': 'arrived', 'orientation': 'clock', 'next_addr': None}
        self.prev_info = {'left': 0.0, 'right': 0.0, 'count': 0, 'prev_count': 0}
        self.rotation_flag = False

        self.cap = cv2.VideoCapture(0)
        self.kit = ServoKit(channels=16)

        self.sio = sio

    def operate(self):
        # Here we loop forever to send messages out to the server via the middleware.
        while self.cap.isOpened():
            # print(self.status)
            start = time.time()
            # Capture frame-by-frame
            ret, frame = self.cap.read()
            frame = cv2.resize(frame, (320, 240))
            image = vision.preprocess(frame)

            if self.rotation_flag is True:
                self.rotate()
            elif self.status['status'] == 'delivering':
                # track line
                lines = vision.find_line(image)
                angle, shift = vision.calculate_angle(lines)
                left, right = vision.track_line(angle, shift)

                stop_x, stop_y = vision.detect_stop(image)
                addr_x, addr_y = vision.detect_address(image)
                obstacle_flag = vision.detect_obstacle(lines)

                self.control(left, right, stop_y, addr_y, obstacle_flag)

                self.prev_info['count'] += 1
                self.prev_info['prev_count'] += 1

            # 추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
            result, imgencode = cv2.imencode('.jpg', frame, encode_param)
            data = np.array(imgencode)
            stringData = data.tostring()

            # self.send_message('image', stringData)
            time.sleep(max(0, 0.0625 - (time.time() - start)))

    def control(self, left, right, stop_y, addr_y, obstacle_flag):
        # stop if obstacle is present
        if obstacle_flag is True:
            self.kit.continuous_servo[0].throttle = 0
            self.kit.continuous_servo[1].throttle = 0
            self.status['status'] = 'obstacle'
            self.send_message('info', self.status)
        # stop if detect stop sign
        elif stop_y > 210:
            time.sleep(0.55)
            self.kit.continuous_servo[0].throttle = 0
            self.kit.continuous_servo[1].throttle = 0
            self.status['status'] = 'arrived'
            # set prev address
            self.status['latest_addr'] = 0
            # reset count
            self.prev_info['count'], self.prev_info['prev_count'] = 0, 0
            self.status['next_addr'] = None
            # send message to operatorUI
            self.send_message('info', self.status)
            print("Arrived at stop sign")
        # otherwise while moving detect address
        else:
            if left is None or right is None:
                self.kit.continuous_servo[0].throttle = self.prev_info['right']
                self.kit.continuous_servo[1].throttle = self.prev_info['left']
            else:
                self.kit.continuous_servo[0].throttle = right
                self.kit.continuous_servo[1].throttle = left
                self.prev_info['right'] = right
                self.prev_info['left'] = left

            prev_address = self.status['latest_addr']
            '''
            if prev_address is None:
                prev_address = 0
            '''
            if self.status['orientation'] == 'clock':
                if prev_address in [101, 203]:
                    if addr_y > ADDRESS[prev_address]['addr_y'] or self.prev_info['prev_count'] > ADDRESS[prev_address]['prev_count']:
                        if self.prev_info['prev_count'] > ADDRESS[prev_address]['prev_count'] - 10:
                            time.sleep(0.5)
                            self.status['latest_addr'] = ADDRESS[prev_address]['next_address']
                            print("Arrived at %d" % self.status['latest_addr'])
                            print("Addr-y: %d" % addr_y)
                            print("frame count %d, prev count %d " % (self.prev_info['count'], self.prev_info['prev_count']))
                            self.prev_info['prev_count'] = 0
                            self.send_message('info', self.status)

                elif prev_address in [0, 102, 103, 202]:
                    if addr_y > ADDRESS[prev_address]['addr_y'] or self.prev_info['prev_count'] > ADDRESS[prev_address]['prev_count']:
                        if self.prev_info['prev_count'] > ADDRESS[prev_address]['prev_count'] - 10:
                            self.status['latest_addr'] = ADDRESS[prev_address]['next_address']
                            print("Arrived at %d" % self.status['latest_addr'])
                            print("Addr-y: %d" % addr_y)
                            print("frame count %d, prev count %d " % (self.prev_info['count'], self.prev_info['prev_count']))
                            self.prev_info['prev_count'] = 0
                            self.send_message('info', self.status)

            else:
                if prev_address in [201, 103]:
                    if addr_y > REV_ADDRESS[prev_address]['addr_y'] or self.prev_info['prev_count'] > REV_ADDRESS[prev_address]['prev_count']:
                        if self.prev_info['prev_count'] > REV_ADDRESS[prev_address]['prev_count'] - 10:
                            time.sleep(0.5)
                            self.status['latest_addr'] = REV_ADDRESS[prev_address]['next_address']
                            print("Arrived at %d" % self.status['latest_addr'])
                            print("Addr-y: %d" % addr_y)
                            print("frame count %d, prev count %d " % (self.prev_info['count'], self.prev_info['prev_count']))
                            self.prev_info['prev_count'] = 0
                            self.send_message('info', self.status)

                elif prev_address in [0, 202, 203, 102]:
                    if addr_y > REV_ADDRESS[prev_address]['addr_y'] or self.prev_info['prev_count'] > REV_ADDRESS[prev_address]['prev_count']:
                        if self.prev_info['prev_count'] > REV_ADDRESS[prev_address]['prev_count'] - 10:
                            self.status['latest_addr'] = REV_ADDRESS[prev_address]['next_address']
                            print("Arrived at %d" % self.status['latest_addr'])
                            print("Addr-y: %d" % addr_y)
                            print("frame count %d, prev count %d " % (self.prev_info['count'], self.prev_info['prev_count']))
                            self.prev_info['prev_count'] = 0
                            self.send_message('info', self.status)

            if self.status['next_addr'] == self.status['latest_addr']:
                self.kit.continuous_servo[0].throttle = 0
                self.kit.continuous_servo[1].throttle = 0
                self.status['status'] = 'arrived'
                self.send_message('info', self.status)

    def rotate(self):
        if self.status['orientation'] == 'clock':
            if self.status['latest_addr'] is 0:
                self.kit.continuous_servo[0].throttle = -0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(1.2)
            elif self.status['latest_addr'] is 101:
                self.kit.continuous_servo[0].throttle = -0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(1.4)
                self.kit.continuous_servo[0].throttle = -0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(0.5)
            elif self.status['latest_addr'] is 102:
                self.kit.continuous_servo[0].throttle = 0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(0.55)
                self.kit.continuous_servo[0].throttle = -0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(1.2)
                self.prev_info['prev_count'] += 5

            self.kit.continuous_servo[0].throttle = 0
            self.kit.continuous_servo[1].throttle = 0
            self.status['orientation'] = 'counterclock'
            self.rotation_flag = False
            self.send_message('turn', '')
        else:
            if self.status['latest_addr'] is 0:
                self.kit.continuous_servo[0].throttle = 0.5
                self.kit.continuous_servo[1].throttle = 0.5
                time.sleep(1.2)
            elif self.status['latest_addr'] is 201:
                self.kit.continuous_servo[0].throttle = 0.5
                self.kit.continuous_servo[1].throttle = 0.5
                time.sleep(1.2)
            elif self.status['latest_addr'] is 202:
                self.kit.continuous_servo[0].throttle = -0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(1.3)

            self.kit.continuous_servo[0].throttle = 0
            self.kit.continuous_servo[1].throttle = 0
            self.status['orientation'] = 'clock'
            self.rotation_flag = False
            self.send_message('turn', '')

    def send_message(self, type, msg):
        if type == 'info':
            self.sio.emit('robot_info', msg)
        elif type == 'image':
            self.sio.emit('video', msg)
        elif type == 'turn':
            self.sio.emit('turn', msg)
