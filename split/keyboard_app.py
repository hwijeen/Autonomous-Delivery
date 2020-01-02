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
pygame.init()
while True:
    msg = input("Input keyboard: ")
    event = pygame.event.wait()

    # if the 'close' button of the window is pressed
    if event.type == pygame.QUIT:
        # stops the application
        break

    # captures the 'KEYDOWN' and 'KEYUP' events
    if event.type in (pygame.KEYDOWN, pygame.KEYUP):
        # gets the key name
        key_name = pygame.key.name(event.key)

        # converts to uppercase the key name
        key_name = key_name.upper()
        msg = key_name

        # if any key is pressed
        if event.type == pygame.KEYDOWN:
            print(key_name)

        # if any key is released
        elif event.type == pygame.KEYUP:
            # prints on the console the released key
            print(key_name)


    serverconn.send(msg.encode('ascii'))

pygame.quit()
