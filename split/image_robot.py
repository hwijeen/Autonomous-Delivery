import cv2
import numpy as np
import time
import socket
import json
from sys import *
# from adafruit_servokit import ServoKit

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

print("Robot Hostname:: ", host_name)
print("Server IP:: ", host_ip)

if len(argv) == 2:
    ConnectTo = argv[1]     # robot_demos.py IP address
    print("Connecting to: ", argv[1])
else:
    ConnectTo = host_ip     # connect to local host
    print("Connecting to: localhost")

# servo
# kit = ServoKit(channels=16)

# image
cap = cv2.VideoCapture(0)

imgconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
imgconn.connect((ConnectTo, 1024))

# Here we loop forever to send messages out to the server via the middleware.
while cap.isOpened():
    # Capture frame-by-frame
    ret, frame = cap.read()

    frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    # 추출한 이미지를 String 형태로 변환(인코딩)시키는 과정
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
    data = np.array(imgencode)
    stringData = data.tostring()

    # String 형태로 변환한 이미지를 socket을 통해서 전송
    imgconn.send(bytes(str(len(stringData)).ljust(16), 'utf8'))
    imgconn.send(stringData)
    print('send data')
