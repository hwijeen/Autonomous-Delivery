import time

import robot
import socket_manager


class Manager:
    def __init__(self):
        self.socket = socket_manager.Socket()
        self.robot = robot.Robot(self.socket.sio)
        self.socket.sio.on('next_addr', self.recv_addr)
        self.socket.sio.on('status', self.recv_mode)
        # self.socket.sio.connect('http://172.26.213.218:5000')
        self.socket.sio.connect('http://172.26.226.35:60000')

    def recv_addr(self, data):
        next_address = data
        if next_address not in [0, 101, 102, 103, 201, 202, 203]:
            print("wrong message")
        else:
            self.robot.next_address = next_address
            print("Next destination: %d " % next_address)

    def recv_mode(self, data):
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

        elif data == 'misdelivery':
            self.robot.status['status'] = 'maintenance'
            self.robot.status['addr'] = 0
            self.robot.kit.continuous_servo[0].throttle = 0
            self.robot.kit.continuous_servo[1].throttle = 0
            print("Miss delivery, maintenance mode")


if __name__ == "__main__":
    manager = Manager()
    manager.robot.control()
