import socket
import threading
import time
import pickle

import robot
import socket_manager


class Manager():
    def __init__(self):
        self.socket = socket_manager.Socket()
        self.robot = robot.Robot(self.socket.addrconn, self.socket.imgconn)

    def keyboard(self):
        while True:
            next_address = pickle.loads(self.socket.destconn.recv(16))
            if next_address not in ['0', '101', '102', '103', '201', '202', '203', 'm', 'r']:
                print("wrong message")
            # maintenance mode
            elif next_address == 'm':
                self.robot.kit.continuous_servo[0].throttle = 0
                self.robot.kit.continuous_servo[1].throttle = 0
                self.robot.status['status'] = 'maintenance'
                print("Maintenance mode")
            elif next_address == 'r':
                print("Turn around")
                self.robot.rotation_flag = True
            elif next_address == '0':
                self.robot.status['next_addr'] = None
                print("Next destination: stop")
                self.robot.status['status'] = 'delivering'
                print("Start delivery")
            else:
                self.robot.status['next_addr'] = int(next_address)
                print("Next destination: %d " % int(next_address))
                self.robot.status['status'] = 'delivering'
                print("Start delivery")

    def start_and_join(self, threads):
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    manager = Manager()

    threads = []
    threads.append(threading.Thread(target=manager.robot.operate))
    threads.append(threading.Thread(target=manager.keyboard))

    manager.start_and_join(threads)
    manager.socket.close()
