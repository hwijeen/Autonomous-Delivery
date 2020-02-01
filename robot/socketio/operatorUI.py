import cv2
import numpy as np
import time
import matplotlib.pyplot as plt

import eventlet
import socketio

import vision

sio = socketio.Server()
app = socketio.WSGIApp(sio, static_files={
    '/': {'content_type': 'text/html', 'filename': 'index.html'}
})


@sio.event
def connect(sid, environ):
    print('connect ', sid)
    time.sleep(1)
    sio.emit('next_addr', {'addr': 0})
    print("Next addr is 0")
    sio.emit('status', 'delivering')


@sio.event
def disconnect(sid):
    print('disconnect ', sid)


@sio.on('info')
def address(sid, data):
    robot_info = data
    print("Address: %d, Status: %s" % (robot_info['addr'], robot_info['status']))
    if robot_info['addr'] == 0:
        time.sleep(2)
        sio.emit('next_addr', {'addr': 0})
        print("Next addr is 0")
        sio.emit('status', 'delivering')
    elif robot_info['status'] == 'obstacle':
        time.sleep(5)
        sio.emit('status', 'delivering')

@sio.on('video')
def show_image(sid, data):
    stringData = data
    data = np.fromstring(stringData, dtype='uint8')
    rgb_img = cv2.imdecode(data, 1)
    blur = cv2.GaussianBlur(rgb_img, (5, 5), 0)
    hsv_img = cv2.cvtColor(blur, cv2.COLOR_BGR2HSV)
    # line
    low_yellow = np.array([20, 45, 65])
    up_yellow = np.array([35, 255, 255])
    mask = cv2.inRange(hsv_img, low_yellow, up_yellow)

    cv2.imshow('Streaming', mask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        pass

    '''
    lines = vision.find_line(hsv_img[160:, :])
    image = vision.draw_obstacle(rgb_img, lines)
    
    cv2.imshow('Streaming', mask)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        pass
    '''
    # plt.imshow(np.real(hsv_img))
    # plt.pause(0.01)


if __name__ == '__main__':
    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
