import cv2
import numpy as np
import time

import eventlet
import socketio

import vision
import matplotlib.pyplot as plt

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})

orientation_flag = 'clock'
# orientation_flag = 'counterclock'

ADDRESS = {0: {'addr_x': 40, 'addr_y': 125, 'prev_count': 30, 'next_address': 101},
           101: {'addr_x': 270, 'addr_y': 80, 'prev_count': 35, 'next_address': 102},
           102: {'addr_x': 40, 'addr_y': 140, 'prev_count': 55, 'next_address': 103},
           103: {'addr_x': 120, 'addr_y': 100, 'prev_count': 60, 'next_address': 203},
           203: {'addr_x': 280, 'addr_y': 80, 'prev_count': 40, 'next_address': 202},
           202: {'addr_x': 80, 'addr_y': 130, 'prev_count': 50, 'next_address': 201},
           201: {'addr_x': 0, 'addr_y': 0, 'prev_count': 0, 'next_address': None}}


REV_ADDRESS = {0: {'addr_x': 240, 'addr_y': 120, 'prev_count': 30, 'next_address': 201},
               201: {'addr_x': 50, 'addr_y': 120, 'prev_count': 35, 'next_address': 202},
               202: {'addr_x': 280, 'addr_y': 120, 'prev_count': 55, 'next_address': 203},
               203: {'addr_x': 210, 'addr_y': 150, 'prev_count': 60, 'next_address': 103},
               103: {'addr_x': 20, 'addr_y': 60, 'prev_count': 40, 'next_address': 102},
               102: {'addr_x': 300, 'addr_y': 120, 'prev_count': 50, 'next_address': 101},
               101: {'addr_x': 0, 'addr_y': 0, 'prev_count': 0, 'next_address': None}}

@sio.event
def connect(sid, environ):
    print('connect ', sid)
    time.sleep(1)
    sio.emit('next_addr', 101)
    sio.emit('status', 'delivering')


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


@sio.on('info')
def address(sid, data):
    robot_info = data
    print("Address: %d, Status: %s" % (robot_info['addr'], robot_info['status']))

    if robot_info['status'] == 'obstacle':
        time.sleep(5)
        sio.emit('status', 'delivering')
    elif robot_info['status'] == 'arrived':
        time.sleep(3)
        sio.emit('next_addr', ADDRESS[robot_info['addr']]['next_address'])
        sio.emit('status', 'delivering')
    elif robot_info['status'] == 'rotation':
        if orientation_flag == 'clock':
            sio.emit('next_addr', REV_ADDRESS[robot_info['addr']]['next_address'])
        else:
            sio.emit('next_addr', ADDRESS[robot_info['addr']]['next_address'])
        sio.emit('status', 'delivering')


@sio.on('video')
def show_image(sid, data):
    stringData = data
    data = np.fromstring(stringData, dtype='uint8')
    rgb_img = cv2.imdecode(data, 1)
    hsv_img = vision.preprocess(rgb_img)
    '''
    result = vision.draw_address(hsv_img, rgb_img)

    cv2.imshow('Streaming', result)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        pass
    '''

    lines = vision.find_line(hsv_img)
    image = vision.draw_obstacle(rgb_img, lines)
    
    cv2.imshow('Streaming', image)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        pass

    # plt.imshow(np.real(hsv_img))
    # plt.pause(0.01)


@sio.on('turn')
def turn(sid, data):
    print(data)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
