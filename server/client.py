"""
A code mimicing client side(scheduler and robot) to test server.
"""
import socketio
import random

import numpy as np


sio = socketio.Client()
sio.connect('http://localhost:60000')

@sio.on('connect')
def connect():
    print('Connected!')

@sio.on('disconnect')
def disconnect():
    print('Disconnected!')


ADDR = [101, 102, 103, 201, 202, 203]
NUM_ORDERS = [1,2]
NUM = [1, 3, 5]


def make_delivery_list():
    num_deliv = int(input('Number of deliveries in this round: '))
    deliv_list = []
    for _ in range(num_deliv):
        addr = int(input('Addr: '))
        red = int(input('red: '))
        green = int(input('green: '))
        blue = int(input('blue: '))
        deliv = {'addr': addr, 'red': red, 'green':green, 'blue':blue, 'status': 'pending'}
        deliv_list.append(deliv)
    deliv_list.append({'addr':0, 'red':0, 'green':0, 'blue':0, 'status':'pending'})
    return deliv_list

def get_cmd_data(cmd_id):
    deliv_list = ('deliv_list', make_delivery_list())
    arrived_info = ('robot_info', {'latest_addr':102, 'next_addr':103, 'status' :'arrived', 'orientation':'clockwise'})
    stop_info = ('robot_info', {'latest_addr':0, 'next_addr':0, 'status': 'arrived', 'orientation':'clockwise'})
    id_to_data = {'1': deliv_list, '2': arrived_info, '3':stop_info}

    return id_to_data[cmd_id]


command = """
1. Make deliv list like scheduler
2. Arrived info from robot
3. Stop at loading dock
"""

while True:
    cmd_id = input(command)
    event_name, data = get_cmd_data(cmd_id)
    sio.emit(event_name, data)

