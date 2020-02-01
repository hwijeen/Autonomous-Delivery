import socketio


class Socket:
    def __init__(self):
        self.sio = socketio.Client()
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('connect_error', self.connect_error)

    def on_connect(self):
        print("Robot is connected!")

    def connect_error(self):
        print("The connection failed!")

    def disconnect(self):
        print("Robot is disconnected!")


if __name__ == '__main__':
    socket = Socket()
