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

    def delivery(self):
        while True:
            next_address = pickle.loads(self.socket.destconn.recv(16))
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

    def receive_mode(self):
        while True:
            # receive message (go / maintenance mode)
            msg = pickle.loads(self.socket.modeconn.recv(64))

            # go mode
            if msg == 'operation':
                self.robot.status['status'] = 'delivering'
                print("Start delivery")
            # maintenance mode
            elif msg == 'maintenance':
                self.robot.status['status'] = 'maintenance'
                self.robot.kit.continuous_servo[0].throttle = 0
                self.robot.kit.continuous_servo[1].throttle = 0
                print("Maintenance mode")
                time.sleep(1)

    def start_and_join(self, threads):
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    manager = Manager()

    threads = []
    threads.append(threading.Thread(target=manager.robot.control))
    threads.append(threading.Thread(target=manager.delivery))
    # threads.append(threading.Thread(target=manager.receive_mode))

    manager.start_and_join(threads)
    manager.socket.close()
