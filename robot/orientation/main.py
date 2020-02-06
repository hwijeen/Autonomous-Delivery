import robot
import socket_manager


class Manager:
    def __init__(self):
        self.socket = socket_manager.Socket()
        self.robot = robot.Robot(self.socket.sio)
        self.socket.sio.on('robot_info', self.recv_status)
        self.socket.sio.on('turn', self.recv_turn)
        self.socket.sio.connect('http://172.26.226.35:60000')

    def recv_status(self, data):
        if data['status'] == 'maintenance':
            self.robot.kit.continuous_servo[0].throttle = 0
            self.robot.kit.continuous_servo[1].throttle = 0

        self.robot.status = data
        print(self.robot.status)
        '''
        # go mode
        if data == 'delivering':
            self.robot.status['status'] = 'delivering'
            print("Start delivery")

        # maintenance mode
        elif data == 'maintenance':
            self.robot.kit.continuous_servo[0].throttle = 0
            self.robot.kit.continuous_servo[1].throttle = 0
            self.robot.status['status'] = 'maintenance'
            print("Maintenance mode")

        elif data == 'misdelivery':
            self.robot.kit.continuous_servo[0].throttle = 0
            self.robot.kit.continuous_servo[1].throttle = 0
            self.robot.status['status'] = 'maintenance'
            self.robot.status['addr'] = 0
            self.robot.status['orientation'] = 'clock'
            print("Miss delivery, maintennce mode")
            self.socket.sio.emit('info', self.robot.status)
        '''

    def recv_turn(self, data):
        print("Turn around")
        self.robot.rotation_flag = True


if __name__ == "__main__":
    manager = Manager()
    manager.robot.operate()
