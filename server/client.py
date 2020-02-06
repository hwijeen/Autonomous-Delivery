import socketio
import random

import cv2
import numpy as np


sio = socketio.Client()
sio.connect('http://localhost:60000')

@sio.on('connect')
def connect():
    print('Connected!')

@sio.on('disconnect')
def disconnect():
    print('Disconnected!')

cap = cv2.VideoCapture(0)
def get_frame():
    ret, frame = cap.read()
    encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 90]
    result, imgencode = cv2.imencode('.jpg', frame, encode_param)
    data = np.array(imgencode)
    stringData = data.tostring()
    return stringData

ADDR = [101, 102, 103, 201, 202, 203]
NUM_ORDERS = [1,2]
NUM = [1, 3, 5]

def get_cmd_data(cmd_id):
    #d_l = [{'addr':random.choice(ADDR),'red':random.choice(NUM),'green':random.choice(NUM),'blue':random.choice(NUM),'status':'pending'} for i in range(random.choice(NUM_ORDERS))]
    #deliv_list = ('deliv_list', [{'addr':103 ,'red':1,'green':3,'blue':2,'status':'pending'},
    #                             {'addr':201,'red':2,'green':2,'blue':2,'status':'pending'},
    #                             {'addr':0,'red':0,'green':0,'blue':0,'status':'pending'}])
    deliv_list = ('deliv_list', [{'addr':101,'red':2,'green':2,'blue':2,'status':'pending'},
                                 {'addr':0,'red':0,'green':0,'blue':0,'status':'pending'}])
    empty_list = ('deliv_list', [{'addr':0, 'red':0, 'green':0, 'blue':0, 'status': 0}])
    info = ('robot_info', {'latest_addr':102, 'next_addr':103, 'status' :'arrived', 'orientation':'clockwise'})
    load_complete = ('load_complete', None)
    status_change = ('status_change', 'maintenance')
    delivery_status = ('delivery_status', 'complete')
    video_frame = ('video', get_frame())
    stop = ('robot_info', {'latest_addr':None, 'next_addr':None, 'status': 'arrived', 'orientation':'clockwise'})
    id_to_data = {'1': info, '2': deliv_list, '3':status_change, '4': load_complete,
                  '5':delivery_status, '6':video_frame, '7':stop, '8': empty_list}

    return id_to_data[cmd_id]


command = """
1. Info from robot
2. Deliv list from scheduler
3. Status change from admin UI
4. Load complete from worker UI(loader)
5. Delivery status from worker UI(unloder) to scheduler
6. Video from robot(not implemented)
7. Stop at loading dock
8. Send empty deliv list from scheduler
"""

for i in range(10):
    cmd_id = input(command)
    event_name, data = get_cmd_data(cmd_id)
    sio.emit(event_name, data)

