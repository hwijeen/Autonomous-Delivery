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


@socketio.on('status_change')
def status_change(json):
    print('received msg: ' + str(json))


@socketio.on('delivery_status')
def delivery_status(json):
    print('received msg: ' + str(json))


@socketio.on('load_complete')
def load_complete():
    print('load complete received')

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

    dilv_list = [{'addr': '101', 'red':'5', 'green':'5', 'blue':'7'},
                  {'addr': '102', 'red':'3', 'green':'3', 'blue':'3'}]

    robot_status = 'd'

    return render_template("index.html", robot_inv=robot_inv, inv=inv,
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

    return render_template("worker.html")

# app.run(host='0.0.0.0', port=60000)

@socketio.on("")
def update_currdeliv():
    print("curr_deliv")
    curr_deliv = {
        "addr": 102,
        "red": 4,
        "green": 4,
        "blue": 4
    }
    emit("curr_deliv", curr_deliv, broadcast=True)

@socketio.on("")
def update_deliv_prog():
    print("update deliv prog")
    deliv_prog = {
        "num_pending": 5,
        "num_complete": 15,
        "total_orders": 20
    }
    emit("deliv_prog", deliv_prog)

@socketio.on("")
def update_deliv_status_list():
    print("update_deliv_status_list")
    deliv_status_list = [{'id': 1, 'addr': 101, 'red': 5, 'green': 5, 'blue': 7, 'status' : 'complete'},
                 {'id': 2, 'addr': 102, 'red': 5, 'green': 0, 'blue': 2, 'status' : 'complete'},
                 {'id': 3, 'addr': 103, 'red': 7, 'green': 1, 'blue': 3, 'status' : 'pending'}]
    emit("deliv_status_list", deliv_status_list)

@socketio.on('')
def update_inv():
    print("update_inv")
    inv = {
        "red": 10,
        "green": 13,
        "blue": 2,
        "sum": 25}
    emit('inv', inv)

@socketio.on('')
def update_robot_inv():
    print("update robot inv")
    robot_inv = {
        "red": 1,
        "green": 3,
        "blue": 1,
        "sum": 5}
    emit('robot_inv', robot_inv)

@socketio.on('')
def update_robot_status():
    print("update_robot_status")
    info = {
        "addr": 1,
        "status": "delivering"}
    # status=["delivering", "maintenance", "obstacle", "arrived"]
    emit('info', info)

@socketio.on('')
def update_deliv_list_sum():
    print("update_deliv_list_sum")
    deliv_list_sum = { "deliv_list": [{'id': 1, 'addr': 101, 'red': 5, 'green': 5, 'blue': 7},
                                    {'id': 2, 'addr': 102, 'red': 5, 'green': 0, 'blue': 2},
                                    {'id': 3, 'addr': 103, 'red': 7, 'green': 1, 'blue': 3}],
                        "sum": {"red": 12, "green": 6, "blue": 12}}
    emit('deliv_list_sum', deliv_list_sum)


if __name__ == "__main__":
    # socketio.run(app)
    # socketio.run(app, host='0.0.0.0', port=60000)
    socketio.run(app)

