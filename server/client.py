"""
A code mimicing client side(scheduler and robot) to test server.
"""
import socketio
import random

import numpy as np


sio = socketio.Client()
sio.connect('http://localhost:60001')

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
    if cmd_id == '1':
        return ('deliv_list', make_delivery_list())
    elif cmd_id == '2':
        return ('robot_info', {'latest_addr':102, 'next_addr':102, 'status' :'arrived', 'orientation':'clockwise'})
    elif cmd_id == '3':
        return ('robot_info', {'latest_addr':0, 'next_addr':None, 'status': 'arrived', 'orientation':'clockwise'})

command = """
1. Make deliv list like scheduler
2. Arrived info from robot
3. Stop at loading dock
"""

while True:
    cmd_id = input(command)
    event_name, data = get_cmd_data(cmd_id)
    sio.emit(event_name, data)

