import socket
import pickle

# socket ip
viewer_ip = "172.26.213.218"
operator_ip = "172.26.213.218"  # (나)
# operator_ip = "172.26.226.35" # (휘진)


class Socket:
    def __init__(self):
        # socket for receiving mode
        # self.modeconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # self.modeconn.connect((operator_ip, 60001))

        # socket for sending mode
        self.addrconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.addrconn.connect((operator_ip, 60002))

        # socket for receiving next destination
        self.destconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.destconn.connect((operator_ip, 60003))

        # socket for sending image
        self.imgconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.imgconn.connect((viewer_ip, 60004))

    def close(self):
        # self.modeconn.close()
        self.addrconn.close()
        self.destconn.close()
        self.imgconn.close()
