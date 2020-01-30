import socketio
import threading
import time
import pickle

import robot
import socket_manager


class Manager:
    def __init__(self):
        self.socket = socket_manager.Socket()
        self.robot = robot.Robot(self.socket.sio)
        self.socket.sio.connect('http://localhost:5000')
        self.socket.sio.on('delivery', self.delivery)
        self.socket.sio.on('mode', self.receive_mode)

    def delivery(self, data):
        while True:
            next_address = data
            if next_address not in [0, 1, 101, 102, 103, 201, 202, 203]:
                print("wrong message")
            # instead of maintenance mode
            elif next_address == 1:
                self.robot.status['status'] = 'maintenance'
                self.robot.kit.continuous_servo[0].throttle = 0
                self.robot.kit.continuous_servo[1].throttle = 0
            else:
                self.robot.next_address = next_address
                self.robot.status['status'] = 'delivering'
                print(next_address)

    def receive_mode(self, data):
        while True:
            # go mode
            if data == 'delivering':
                self.robot.status['status'] = 'delivering'
                print("Start delivery")

            # maintenance mode
            elif data == 'maintenance':
                self.robot.status['status'] = 'maintenance'
                self.robot.kit.continuous_servo[0].throttle = 0
                self.robot.kit.continuous_servo[1].throttle = 0
                print("Maintenance mode")
                time.sleep(1)


if __name__ == "__main__":
    manager = Manager()
    manager.robot.control()
