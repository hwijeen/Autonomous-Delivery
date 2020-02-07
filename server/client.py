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
    num_deliv = input('Number of deliveries in this round')
    deliv_list = []
    for _ in range(num_deliv):
        addr = input('Addr: ')
        red = input('red: ')
        green = input('green: ')
        blue = input('blue: ')
        deliv = ['addr': addr, 'red': red, 'green':green, 'blue':blue, 'status': 'pending']
        deliv_list.append(deliv)
    return deliv_list

def get_cmd_data(cmd_id):
    info = ('robot_info', {'latest_addr':102, 'next_addr':103, 'status' :'arrived', 'orientation':'clockwise'})
    deliv_list = ('deliv_list', [{'addr':101,'red':2,'green':2,'blue':2,'status':'pending'},
                                 {'addr':0,'red':0,'green':0,'blue':0,'status':'pending'}])
    load_complete = ('load_complete', None)
    status_change = ('status_change', 'maintenance')
    delivery_status = ('delivery_status', 'complete')
    stop = ('robot_info', {'latest_addr':0, 'next_addr':0, 'status': 'arrived', 'orientation':'clockwise'})
    id_to_data = {'1': info, '2': deliv_list, '3':status_change, '4': load_complete,
                  '5':delivery_status, '6':stop}

    return id_to_data[cmd_id]


command = """
1. Arrived info from robot
2. Deliv list from scheduler
3. Status change from admin UI
4. Load complete from worker UI(loader)
5. Delivery status from worker UI(unloder) to scheduler
6. Stop at loading dock
"""

for i in range(10):
    cmd_id = input(command)
    event_name, data = get_cmd_data(cmd_id)
    sio.emit(event_name, data)

