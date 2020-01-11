import cv2
import numpy as np
import matplotlib.pyplot as plt
import time

# import keyboard
import socket
import threading
from pynput import keyboard


def recvall(sock, count):
    buf = b''
    while count:
        newbuf = sock.recv(count)
        if not newbuf: return None
        buf += newbuf
        count -= len(newbuf)
    return buf


def thread1():
    while True:
        length = recvall(robotconn, 16)  # 길이 16의 데이터를 먼저 수신하는 것은 여기에 이미지의 길이를 먼저 받아서 이미지를 받을 때 편리하려고 하는 것이다.
        print("Length is %d" % int(length))
        stringData = recvall(robotconn, int(length))
        data = np.fromstring(stringData, dtype='uint8')
        rgb_img = cv2.imdecode(data, 1)
        cropped = rgb_img[360:480, :]

        blur = cv2.GaussianBlur(cropped, (5, 5), 0)
        hsv = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
        low_yellow = np.array([18, 94, 140])
        up_yellow = np.array([48, 255, 255])
        mask = cv2.inRange(hsv, low_yellow, up_yellow)
        edges = cv2.Canny(mask, 80, 150)

        # im2, cnts, hierarachy = cv2.findContours(edges, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)

        lines = cv2.HoughLinesP(edges, 1, np.pi / 180, 40, maxLineGap=50)
        if lines is not None:
            for line in lines:
                x1, y1, x2, y2 = line[0]
                cv2.line(rgb_img, (x1, y1 + 360), (x2, y2 + 360), (0, 255, 0), 5)
                angle = np.arctan((y2 - y1) / (x2 - x1))
                shift = ((x1 + x2) / 2) - 320.0
                print(angle, shift)
                time.sleep(1)
        # plt.imshow(np.real(rgb_img))
        # plt.pause(0.01)
        # ax.clear()

        cv2.imshow('Streaming', rgb_img)
        # cv2.waitKey(0)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break


def thread2():
    def on_press(key):
        try:
            print('alphanumeric key {0} pressed'.format(key.char))
            msg = key.char
            # print('Key pressed: ', msg)
            serverconn.send(msg.encode('ascii'))
            # serverconn.recv(4)

            if msg == "q":
                serverconn.close()

        except AttributeError:
            print('special key {0} pressed'.format(key))

    def on_release(key):
        print('{0} released'.format(key))
        serverconn.send('x'.encode('ascii'))
        # serverconn.recv(4)

        if key.char == "q":
            serverconn.close()

        if key == keyboard.Key.esc:
            # Stop listener
            return False

    # Collect events until released
    with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
        listener.join()

    # while True:
    #    if keyboard.read_key():
    #        # msg = input("Keyboard input: ")
    #        # print(msg)
    #        msg = keyboard.read_key()
    #        print(msg)
    #        serverconn.send(msg.encode('ascii'))


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

    keyconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    keyconn.bind((host_ip, 2048))
    keyconn.listen(5)

    # stream images
    fig = plt.figure(1)
    ax = fig.add_subplot(111)

    robotconn, _ = imgconn.accept()
    serverconn, _ = keyconn.accept()

    t1 = threading.Thread(target=thread1)
    t2 = threading.Thread(target=thread2)

    t1.start()
    t2.start()

    t1.join()
    t2.join()

    print("finished")
