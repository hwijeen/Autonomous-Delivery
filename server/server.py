import logging

from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, emit

from server_utils import *

# TODO: logging seems unnecessary
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    datefmt = '%m/%d/%Y %H:%M:%S', level=logging.INFO)
logger = logging.getLogger(__name__)
l = logging.getLogger('werkzeug')
l2 = logging.getLogger('engineio.server') 
l3 = logging.getLogger('socketio.server')
l.setLevel(logging.ERROR)
l2.setLevel(logging.ERROR)
l3.setLevel(logging.ERROR)


app = Flask(__name__)
app.config['SECRET_KEY'] = 'hotmetal'
socketio = SocketIO(app)

@app.route('/index')
def index():
    return render_template("index.html")

@app.route('/worker')
def worker():
    return render_template("worker.html")

@socketio.on('request')
def send_admin_page():
    global deliv_list, robot
    deliv_sum_list = deliv_list.get_deliv_list(drop_status=True, add_sum=True)
    emit('deliv_list_sum', deliv_sum_list, broadcast=True)

    deliv_status_list = deliv_list.get_deliv_list(drop_status=False, add_sum=False)
    emit('deliv_status_list', deliv_status_list, broadcast=True)

    curr_deliv = deliv_list.get_curr_deliv(to_dict=True, drop_status=True)
    emit('curr_deliv', curr_deliv, broadcast=True)

    robot_inv = robot.inventory.to_dict()
    emit('robot_inv', robot_inv, broadcast=True)

    robot_status = robot.get_status()
    emit('robot_status', robot_status, broadcast=True)

    loading_dock_inv = loading_dock.inventory.to_dict()
    emit('inv', loading_dock_inv, broadcast=True)

    robot_status = robot.get_status()
    emit('robot_status', robot_status, broadcast=True) # to admin UI

@socketio.on('connect')
def connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def disconnect():
    logger.info('Client disconnected')

# QUESTION: when to send delivery_prog??
@socketio.on('deliv_list')
def prepare_round(deliv_dict_list):
    global deliv_list
    deliv_list.set_from_dict_list(deliv_dict_list)
    logger.info(f'Received delivery list from scheduler: {deliv_dict_list}')

    deliv_sum_list = deliv_list.get_deliv_list(drop_status=True, add_sum=True)
    emit('deliv_list_sum', deliv_sum_list, broadcast=True)
    logger.info(f'Sent delivery list sum to the worker UI(for loader): {deliv_sum_list}')

    deliv_status_list = deliv_list.get_deliv_list(drop_status=False, add_sum=False)
    emit('deliv_status_list', deliv_status_list, broadcast=True)
    logger.info(f'Sent delivery status list to the admin UI: {deliv_status_list}')

    curr_deliv = deliv_list.get_curr_deliv(to_dict=True, drop_status=True)
    emit('curr_deliv', curr_deliv, broadcast=True)
    logger.info(f'Sent current delivery to the admin and worker UI(for unloader): {curr_deliv}')


@socketio.on('load_complete')
def start_round():
    global deliv_list, robot, loading_dock
    deliv_sum_list = deliv_list.get_deliv_list(drop_status=True, add_sum=True)
    to_load = deliv_sum_list['sum']
    robot.inventory.fill(to_load)
    loading_dock.inventory.unfill(to_load)
    logger.info('Updated robot inventory and loading dock inventory')

    robot_inv = robot.inventory.to_dict()
    emit('robot_inv', robot_inv, broadcast=True)
    logger.info(f'Sent robot inventory to the admin UI: {robot_inv}')

    loading_dock_inv = loading_dock.inventory.to_dict()
    emit('inv', loading_dock_inv, broadcast=True)
    logger.info(f'Sent loading dock inventory to the admin UI: {loading_dock_inv}')

    next_addr = deliv_list.get_next_addr()
    emit('next_addr', next_addr, broadcast=True)
    logger.info(f'Sent next address to the robot: {next_addr}')

    emit('status', RobotStatus.DELIVERING, broadcast=True) # to robot
    logger.info('Sent delivering status to the robot')

    emit('robot_status', RobotStatus.DELIVERING, broadcast=True) # to admin UI
    logger.info('Sent delivering status to the admin UI')

    #emit('deliv_list_sum', broadcast=True) # to delete
    #logger.info('Sent empty deliv list sum to the worker UI')

@socketio.on('info')
def handle_robot_status_from_robot(robot_info):
    global robot
    robot.set_from_robot_info(robot_info)
    logger.info(f'Recieved robot info from robot, and updated robot status: {robot_info}')

    robot_status = robot.get_status()
    emit('robot_status', robot_status, broadcast=True)
    logger.info(f'Sent robot status(set by robot itself) to the admin UI: {robot_status}')

    if robot.status == RobotStatus.ARRIVIED: pass
        # wait for worker to unload and send delivery_status
    elif robot.status == RobotStatus.OBSTACLE: pass
        # wait for admin's signal

@socketio.on('delivery_status')
def handle_delivery_status_from_worker(delivery_status):
    global deliv_list, robot
    if delivery_status == Arrived.CORRECT:
        to_unload = deliv_list.get_curr_deliv(to_dict=True, drop_status=True)
        logger.info(f'Arrived at distination, unloading: {to_unload}')
        robot.inventory.unfill(to_unload)
        logger.info(f'Updated robot inventory upon delivery complete')

        deliv_list.set_curr_deliv_complete()
        logger.info('Updated current delivery as complete')

        robot_inv = robot.inventory.to_dict()
        emit('robot_inv', robot_inv, broadcast=True)
        logger.info(f'Sent robot inventory to the admin UI: {robot_inv}')

        curr_deliv = deliv_list.get_curr_deliv(to_dict=True, drop_status=True)
        emit('curr_deliv', curr_deliv, broadcast=True)
        logger.info(f'Sent current delivery to the admin and  worker UI(for unloader): {curr_deliv}')

        deliv_status_list = deliv_list.get_deliv_list(drop_status=False, add_sum=False)
        emit('deliv_status_list', deliv_status_list, broadcast=True)
        logger.info(f'Sent updated deliv status list to admin UI: {deliv_status_list}')

        complete_msg = DeliveryStatus.COMPLETE
        emit('unload_complete', complete_msg, broadcast=True)
        logger.info('Send delivery complete message to the scheduler')

        next_addr = deliv_list.get_next_addr()
        emit('next_addr', next_addr, broadcast=True)
        logger.info(f'Sent next addr to robot: {next_addr}')

        robot.set_delivering()
        robot_status = robot.status
        emit('status', robot_status, broadcast=True) # to robot
        emit('robot_status', robot_status, broadcast=True) # admin UI
        logger.info(f'Sent delivering mode to robot: {robot_status}')
        logger.info('Sent robot status to admin UI')

    elif delivery_status == Arrived.INCORRECT:
        robot_status = RobotStatus.MAINTENANCE
        emit('robot_status', robot_status, broadcast=True) # admin UI
        emit('status', Arrived.INCORRECT, broadcast=True) # to robot
        logger.info(f'Put robot in maintenance mode due to incorrect delivery: {robot_status}')

@socketio.on('status_change')
def handle_robot_status(robot_status):
    global robot
    if robot_status == RobotStatus.MAINTENANCE:
        robot.set_maintenance()
        logger.info('Put robot in maintenance mode manually')

    elif robot_status == RobotStatus.DELIVERING:
        robot.set_delivering()
        logger.info('Put robot in delivering mode manually')

    emit('status', robot_status, broadcast=True) # to robot
    emit('robot_status', robot_status, broadcast=True) # back to admin UI
    logger.info('Sent maintenance mode to the robot and the robot')

@socketio.on('replenish')
def update_loading_dock():
    pass

#@socketio.on('video')
#def stram_video(frame):
#    global video
#    video.set_frame(frame)


def generate():
    while True:
        global video
        frame = video.get_frame()
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')
def video_feed():
    return Response(generate(), mimetype = "multipart/x-mixed-replace; boundary=frame")



if __name__ == "__main__":

    deliv_list = DeliveryList()
    robot = Robot()
    loading_dock = LoadingDock()
    video = Video()
    delivery_prob = DeliveryProgress()

    socketio.run(app, host='0.0.0.0', port=60000)

