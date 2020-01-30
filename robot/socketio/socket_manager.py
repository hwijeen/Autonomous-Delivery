import socketio


class Socket:
    def __init__(self):
        self.sio = socketio.Client()
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('connect_error', self.connect_error)

    def on_connect(self):
        print("I'm connected!")

    def connect_error(self):
        print("The connection failed!")

    def disconnect(self):
        print("I'm disconnected")


if __name__ == '__main__':
    socket = Socket()
    # socket.sio.emit('my message', {'foo': 'bar'})
