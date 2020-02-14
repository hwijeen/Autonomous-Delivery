import robot
import threading
import socket_manager


class Manager:
    def __init__(self):
        self.socket = socket_manager.Socket()
        self.robot = robot.Robot(self.socket.sio)
        self.socket.sio.on('robot_info', self.recv_status)
        self.socket.sio.on('turn', self.recv_turn)
        self.socket.sio.connect('http://172.26.226.35:60000')
        # self.socket.sio.connect('http://172.26.213.218:60000')

    def recv_status(self, data):
        if data['status'] == 'maintenance':
            self.robot.kit.continuous_servo[0].throttle = 0
            self.robot.kit.continuous_servo[1].throttle = 0

        self.robot.status = data
        print(self.robot.status)

    def recv_turn(self, data):
        print("Turn around")
        self.robot.rotation_flag = True

    def start_and_join(self, threads):
        for thread in threads:
            thread.start()

        for thread in threads:
            thread.join()


if __name__ == "__main__":
    manager = Manager()

    threads = []
    threads.append(threading.Thread(target=manager.robot.capture))
    threads.append(threading.Thread(target=manager.robot.operate))

    manager.start_and_join(threads)
