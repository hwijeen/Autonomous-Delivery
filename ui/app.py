from flask import Flask, render_template
# import mysql.connector as mysql
from flask_socketio import SocketIO, emit
from flask import Response
from flask import Flask
import cv2


# class VideoCamera(object):
#     def __init__(self):
#         # Using OpenCV to capture from device 0. If you have trouble capturing
#         # from a webcam, comment the line below out and use a video file
#         # instead.
#         self.video = cv2.VideoCapture(0)
#         # If you decide to use video.mp4, you must have this file in the folder
#         # as the main.py.
#         # self.video = cv2.VideoCapture('video.mp4')
#
#     def __del__(self):
#         self.video.release()
#
#     def get_frame(self):
#         success, image = self.video.read()
#         # We are using Motion JPEG, but OpenCV defaults to capture raw images,
#         # so we must encode it into JPEG in order to correctly display the
#         # video stream.
#         ret, jpeg = cv2.imencode('.jpg', image)
#         return jpeg.tobytes()


# db = mysql.connect(
#     host = "localhost",
#     user = "root",
#     passwd = "newroot",
#     database = "orderdb"
# )
# cursor = db.cursor()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)


@socketio.on('robot_go')
def robot_go_py(json):
    print('received msg: ' + str(json))

@socketio.on('maint')
def maint_py(json):
    print('received msg: ' + str(json))

def some_function():
    socketio.emit('some event', {'data': 42})


@app.route('/index')
def index():
    inv = {
        "red": "10",
        "green": "10",
        "blue": "10"}

    robot_inv = {
        "red": "1",
        "green": "1",
        "blue": "1"}

    lts_address = '201'

    next_dilv = {
        'address': '101',
        'red' : '5',
        'green' : '5',
        'blue' : '5'
    }

    dilv_list = [{'address': '101', 'red':'5', 'green':'5', 'blue':'7'},
                  {'address': '102', 'red':'3', 'green':'3', 'blue':'3'}]

    robot_status = 'd'

    return render_template("index.html", robot_inv=robot_inv, lts_address=lts_address, inv=inv, next_dilv=next_dilv,
                           dilv_list=dilv_list, len_dilv_list=len(dilv_list), robot_status=robot_status)



# def go_maint():
#     if request.method == "POST":
#         if request.form['Go'] == ''


# def gen(camera):
#     while True:
#         frame = camera.get_frame()
#         yield (b'--frame\r\n'
#                b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

# @app.route('/video_feed')
# def video_feed():
#     return Response(gen(VideoCamera()),
#                     mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/worker')
def worker():
    # return render_template('index.html')
    # cursor.execute("select * from orders")
    # data = cursor.fetchall()
    # value=data
    dilv_list = [{'address': '101', 'red':'5', 'green':'5', 'blue':'7'},
                  {'address': '102', 'red':'3', 'green':'3', 'blue':'3'}]

    loader_rgb = {
        "red": "10",
        "green": "10",
        "blue": "10"}

    return render_template("worker.html", dilv_list=dilv_list, len_dilv_list=len(dilv_list), loader_rgb=loader_rgb)

# app.run(host='0.0.0.0', port=60000)


@socketio.on('request')
def request():
    print("request")
    inv = {
        "red": "21",
        "green": "11",
        "blue": "11",
        "sum": 43}

    emit('request', inv)
    emit('request', inv)

if __name__ == "__main__":
    # socketio.run(app)
    # socketio.run(app, host='0.0.0.0', port=60000)
    socketio.run(app)

