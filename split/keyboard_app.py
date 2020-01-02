import cv2
import numpy as np
import matplotlib.pyplot as plt

import time
import socket
import keyboard
import threading
import tkinter as tk
from msvcrt import getch

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

keyconn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
keyconn.bind((host_ip, 2048))
keyconn.listen(5)

serverconn, _ = keyconn.accept()

while True:
    msg = input("Input keyboard: ")
    serverconn.send(msg.encode('ascii'))
