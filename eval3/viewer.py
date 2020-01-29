import cv2
import numpy as np
import socket


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
    imgconn.bind((host_ip, 1024))
    imgconn.listen(5)

    robotconn, _ = imgconn.accept()

    while True:
        length = recvall(robotconn, 16)  # 길이 16의 데이터를 먼저 수신하는 것은 여기에 이미지의 길이를 먼저 받아서 이미지를 받을 때 편리하려고 하는 것이다.
        # print("Length is %d" % int(length))
        stringData = recvall(robotconn, int(length))
        data = np.fromstring(stringData, dtype='uint8')

        hsv_img = cv2.imdecode(data, 1)

        blur = cv2.GaussianBlur(hsv_img, (5, 5), 0)
        lower_green = np.array([50, 70, 50])
        upper_green = np.array([70, 255, 255])
        mask = cv2.inRange(hsv_img, lower_green, upper_green)
        output = cv2.bitwise_and(blur, blur, mask=mask)

        # rgb_img = cv2.cvtColor(hsv_img, cv2.COLOR_HSV2BGR)
        cv2.imshow('Streaming', output)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
