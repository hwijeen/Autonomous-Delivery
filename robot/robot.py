import cv2
import time
import numpy as np
from adafruit_servokit import ServoKit

import vision


ADDRESS = {0: {'prev_count': 50, 'next_address': 101},
           101: {'prev_count': 110, 'next_address': 102},
           102: {'prev_count': 85, 'next_address': 103},
           103: {'prev_count': 125, 'next_address': 203},
           203: {'prev_count': 110, 'next_address': 202},
           202: {'prev_count': 95, 'next_address': 201},
           201: {'prev_count': 40, 'next_address': 0}}


REV_ADDRESS = {0: {'prev_count': 65, 'next_address': 201},
               201: {'prev_count': 90, 'next_address': 202},
               202: {'prev_count': 90, 'next_address': 203},
               203: {'prev_count': 115, 'next_address': 103},
               103: {'prev_count': 80, 'next_address': 102},
               102: {'prev_count': 87, 'next_address': 101},
               101: {'prev_count': 40, 'next_address': 0}}


class Robot:
    def __init__(self, sio):
        self.status = {'latest_addr': 0, 'status': 'arrived', 'orientation': 'clock', 'next_addr': None}
        self.prev_info = {'left': 0.0, 'right': 0.0, 'count': 0, 'prev_count': 0}
        self.rotation_flag = False
        self.obstacle_count = 0

        self.cap = cv2.VideoCapture(0)
        self.kit = ServoKit(channels=16)

        self.frame = None

        self.sio = sio

    def capture(self):
        while self.cap.isOpened():
            _, self.frame = self.cap.read()

    def operate(self):
        # Here we loop forever to send messages out to the server via the middleware.
        while True:
            start = time.time()
            if self.frame is not None:
                frame = cv2.resize(self.frame, (320, 240))
                image = vision.preprocess(frame)

                if self.rotation_flag is True:
                    time.sleep(0.1)
                    self.rotate()
                elif self.status['status'] == 'delivering':
                    # track line
                    lines = vision.find_line(image)
                    angle, shift = vision.calculate_angle(lines)
                    left, right = vision.track_line(angle, shift)

                    stop_x, stop_y = vision.detect_stop(image)
                    obstacle_flag = vision.detect_obstacle(lines)
                    if obstacle_flag is True:
                        self.obstacle_count += 1
                    else:
                        self.obstacle_count = 0

                    self.control(left, right, stop_y)

                    self.prev_info['count'] += 1
                    self.prev_info['prev_count'] += 1
                else:
                    self.kit.continuous_servo[0].throttle = 0.0
                    self.kit.continuous_servo[1].throttle = 0.0

                if time.time() - start > 0.03:
                    print("Elapsed time for one frame: %.4f" % (time.time() - start))
                time.sleep(max(0, 0.03 - (time.time() - start)))

    def control(self, left, right, stop_y):
        # stop if obstacle is present
        if self.obstacle_count > 2:
            self.kit.continuous_servo[0].throttle = 0
            self.kit.continuous_servo[1].throttle = 0
            self.status['status'] = 'obstacle'
            self.send_message('info', self.status)
            print("Obstacle is in the road. No line detected")
        # stop if detect stop sign
        elif stop_y > 190:
            time.sleep(0.7)
            self.kit.continuous_servo[0].throttle = 0
            self.kit.continuous_servo[1].throttle = 0
            print("Arrived at stop sign")
            print("frame count %d, prev count %d " % (self.prev_info['count'], self.prev_info['prev_count']))
            print("stop_y %.4f" % stop_y)
            self.correction()
            self.status['status'] = 'arrived'
            # set prev address
            self.status['latest_addr'] = 0
            # reset count
            self.prev_info['count'], self.prev_info['prev_count'] = 0, 0
            self.status['next_addr'] = None
            # send message to operatorUI
            self.send_message('info', self.status)
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
            if self.status['orientation'] == 'clock':
                if prev_address == 201:
                    if self.prev_info['prev_count'] > ADDRESS[prev_address]['prev_count']:
                        time.sleep(0.7)
                        self.kit.continuous_servo[0].throttle = 0
                        self.kit.continuous_servo[1].throttle = 0
                        print("Arrived at stop sign by frame")
                        self.correction()
                        self.status['status'] = 'arrived'
                        # set prev address
                        self.status['latest_addr'] = 0
                        # reset count
                        self.prev_info['count'], self.prev_info['prev_count'] = 0, 0
                        self.status['next_addr'] = None
                        # send message to operatorUI
                        self.send_message('info', self.status)
                else:
                    if self.prev_info['prev_count'] > ADDRESS[prev_address]['prev_count']:
                        self.status['latest_addr'] = ADDRESS[prev_address]['next_address']
                        print("Arrived at %d" % self.status['latest_addr'])
                        print("frame count %d, prev count %d " % (self.prev_info['count'], self.prev_info['prev_count']))
                        self.prev_info['prev_count'] = 0
                        self.send_message('info', self.status)

            else:
                if prev_address == 101:
                    if self.prev_info['prev_count'] > REV_ADDRESS[prev_address]['prev_count']:
                        time.sleep(0.7)
                        self.kit.continuous_servo[0].throttle = 0
                        self.kit.continuous_servo[1].throttle = 0
                        print("Arrived at stop sign by frame")
                        self.correction()
                        self.status['status'] = 'arrived'
                        # set prev address
                        self.status['latest_addr'] = 0
                        # reset count
                        self.prev_info['count'], self.prev_info['prev_count'] = 0, 0
                        self.status['next_addr'] = None
                        print(self.status)
                        # send message to operatorUI
                        self.send_message('info', self.status)

                else:
                    if self.prev_info['prev_count'] > REV_ADDRESS[prev_address]['prev_count']:
                        self.status['latest_addr'] = REV_ADDRESS[prev_address]['next_address']
                        print("Arrived at %d" % self.status['latest_addr'])
                        print("frame count %d, prev count %d " % (self.prev_info['count'], self.prev_info['prev_count']))
                        self.prev_info['prev_count'] = 0
                        self.send_message('info', self.status)

            if self.status['next_addr'] == self.status['latest_addr']:
                self.kit.continuous_servo[0].throttle = 0
                self.kit.continuous_servo[1].throttle = 0
                self.status['status'] = 'arrived'
                self.send_message('info', self.status)

    def rotate(self):
        if self.status['orientation'] == 'counterclock':
            if self.status['latest_addr'] in [0, 102]:
                self.kit.continuous_servo[0].throttle = -0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(1.2)
                self.kit.continuous_servo[0].throttle = 0.3
                self.kit.continuous_servo[1].throttle = -0.3
                time.sleep(0.1)

                # reverse servo value
                temp = self.prev_info['left']
                self.prev_info['left'] = -1 * self.prev_info['right']
                self.prev_info['right'] = -1 * temp

                self.kit.continuous_servo[0].throttle = 0
                self.kit.continuous_servo[1].throttle = 0
                time.sleep(0.3)
                self.rotation_flag = False

            elif self.status['latest_addr'] in [101, 103]:
                self.kit.continuous_servo[0].throttle = -0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(1.4)

                # reverse servo value
                temp = self.prev_info['left']
                self.prev_info['left'] = -1 * self.prev_info['right']
                self.prev_info['right'] = -1 * temp

                self.kit.continuous_servo[0].throttle = 0
                self.kit.continuous_servo[1].throttle = 0
                # time.sleep(0.1)
                self.rotation_flag = False

        else:
            if self.status['latest_addr'] in [0, 203]:
                self.kit.continuous_servo[0].throttle = 0.5
                self.kit.continuous_servo[1].throttle = 0.5
                time.sleep(1.2)
                self.kit.continuous_servo[0].throttle = 0.3
                self.kit.continuous_servo[1].throttle = -0.3
                time.sleep(0.1)

                # reverse servo value
                temp = self.prev_info['left']
                self.prev_info['left'] = -1 * self.prev_info['right']
                self.prev_info['right'] = -1 * temp

                self.kit.continuous_servo[0].throttle = 0
                self.kit.continuous_servo[1].throttle = 0
                time.sleep(0.3)
                self.rotation_flag = False

            elif self.status['latest_addr'] == 201:
                self.kit.continuous_servo[0].throttle = 0.5
                self.kit.continuous_servo[1].throttle = 0.5
                time.sleep(1.4)

                # reverse servo value
                temp = self.prev_info['left']
                self.prev_info['left'] = -1 * self.prev_info['right']
                self.prev_info['right'] = -1 * temp

                self.kit.continuous_servo[0].throttle = 0
                self.kit.continuous_servo[1].throttle = 0
                # time.sleep(0.1)
                self.rotation_flag = False
            elif self.status['latest_addr'] == 202:
                self.kit.continuous_servo[0].throttle = -0.5
                self.kit.continuous_servo[1].throttle = -0.5
                time.sleep(1.3)

                # reverse servo value
                temp = self.prev_info['left']
                self.prev_info['left'] = -1 * self.prev_info['right']
                self.prev_info['right'] = -1 * temp

                self.kit.continuous_servo[0].throttle = 0
                self.kit.continuous_servo[1].throttle = 0
                # time.sleep(0.1)
                self.rotation_flag = False

    def correction(self):
        if self.status['orientation'] == 'clock':
            self.kit.continuous_servo[0].throttle = 0.0
            self.kit.continuous_servo[1].throttle = 0.5

            time.sleep(0.2)

            self.kit.continuous_servo[0].throttle = 0.0
            self.kit.continuous_servo[1].throttle = 0.0
        else:
            self.kit.continuous_servo[0].throttle = -0.5
            self.kit.continuous_servo[1].throttle = 0.0

            time.sleep(0.2)

            self.kit.continuous_servo[0].throttle = 0.0
            self.kit.continuous_servo[1].throttle = 0.0

    def send_message(self, type, msg):
        self.sio.emit('robot_info', msg)
