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

keyconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keyconn.connect((ConnectTo, 2048))

# Here we loop forever to send messages out to the server via the middleware.
while True:
    key_data = keyconn.recv(64).decode('ascii')
    print("Keyboard input:", key_data)

    # imgconn.close()
    '''
    print("Waiting for client request...")
    servconn, addr = keyconn.accept()
    key_data = servconn.recv(4096).decode('ascii')

    if key_data:
        if key_data == "w":
            print("Keyboard input:", key_data)
        elif key_data == "s":
            print("Keyboard input:", key_data)
        elif key_data == "a":
            print("Keyboard input:", key_data)
        elif key_data == "d":
            print("Keyboard input:", key_data)
        else:
            print("Default")

        # Now we send a response back to middleware
        servconn.send(msg.encode('ascii'))
        servconn.close()
        print("Server disconnected")
    '''
