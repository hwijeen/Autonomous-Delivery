import cv2
import numpy as np
import socket
import matplotlib.pyplot as plt

import vision


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


if __name__ == "__main__":
    # Get the hostname and IP address of this machine and display it.
    host_name = socket.gethostname()

    try:
        host_ip = socket.gethostbyname(socket.gethostname())
        # On many linux systems, this always gives 127.0.0.1. Hence...
    except:
        host_ip = ''

    if not host_ip or host_ip.startswith('127.'):
        # Now we get the address the hard way.
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('4.2.2.1', 0))
        host_ip = s.getsockname()[0]

    print("Server Hostname:: ", host_name)
    print("Server IP:: ", host_ip)

    imgconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    imgconn.bind((host_ip, 60004))
    imgconn.listen(5)

    robotconn, _ = imgconn.accept()

    while True:
        length = recvall(robotconn, 16)  # 길이 16의 데이터를 먼저 수신하는 것은 여기에 이미지의 길이를 먼저 받아서 이미지를 받을 때 편리하려고 하는 것이다.
        # print("Length is %d" % int(length))
        stringData = recvall(robotconn, int(length))
        data = np.fromstring(stringData, dtype='uint8')
        rgb_img = cv2.imdecode(data, 1)

        # line
        blur = cv2.GaussianBlur(rgb_img, (5, 5), 0)
        hsv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)

        lines = vision.find_line(hsv_img[160:, :])
        image = vision.draw_obstacle(rgb_img, lines)

        cv2.imshow('Streaming', image)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        '''
        # checking hsv value
        rgb_img = cv2.imdecode(data, 1)
        hsv_img = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2HSV)
        plt.imshow(np.real(hsv_img))
        plt.pause(0.01)
        '''