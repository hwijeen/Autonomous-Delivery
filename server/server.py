import logging

from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, emit

from data_structures import *
from server_utils import turn_off_default_loggers, set_logger_format

logger = logging.getLogger(__name__)
set_logger_format()
turn_off_default_loggers()

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
def refresh():
    try:
        global deliv_list, robot
        now_delivering = deliv_list.to_dict()

        emit('now_delivering', now_delivering, broadcast=True)

        curr_deliv = deliv_list.get_curr_deliv()
        emit('curr_deliv', curr_deliv, broadcast=True)

        robot_inv = robot.inventory.to_dict()
        emit('robot_inv', robot_inv, broadcast=True)

        robot_status = robot.get_status()
        emit('robot_status', robot_status, broadcast=True)

        loading_dock_inv = loading_dock.inventory.to_dict()
        emit('loading_dock_inv', loading_dock_inv, broadcast=True)

        robot_status = robot.get_status()
        emit('robot_status', robot_status, broadcast=True) # to admin UI
    except:
        pass

@socketio.on('connect')
def connect():
    logger.info('Client connected')

@socketio.on('disconnect')
def disconnect():
    logger.info('Client disconnected')

@socketio.on('deliv_list')
def prepare_round(deliv_dict_list):
    global deliv_list, robot
    orientation = robot.orientation
    now_delivering = deliv_list.set_from_dict_list(deliv_dict_list, orientation)
    logger.info(f'Received delivery list from scheduler: {now_delivering}')

    emit('now_delivering', now_delivering, broadcast=True)
    logger.info(f'Sent delivery list sum to UI: {now_delivering}')

    curr_deliv = deliv_list.get_curr_deliv()
    emit('curr_deliv', curr_deliv, broadcast=True)
    logger.info(f'Sent current delivery to the UI: {curr_deliv}')

@socketio.on('load_complete')
def start_round():
    global deliv_list, robot, loading_dock
    now_delivering = deliv_list.to_dict()
    to_load = now_delivering['sum']
    robot.inventory.fill(to_load)
    loading_dock.inventory.unfill(to_load)
    logger.info('Updated robot inventory and loading dock inventory')

    robot_inv = robot.inventory.to_dict()
    emit('robot_inv', robot_inv, broadcast=True)
    loading_dock_inv = loading_dock.inventory.to_dict()
    emit('loading_dock_inv', loading_dock_inv, broadcast=True)
    logger.info(f'Sent robot inventory to the UI: {robot_inv}')
    logger.info(f'Sent loading dock inventory to the UI: {loading_dock_inv}')

    next_addr = deliv_list.get_next_addr()
    if robot.is_turn(next_addr):
        robot.set_orientation_flip()
        emit('turn', broadcast=True)
        logger.info(f'Flipping robot orientation, now {robot.orientation}')
    emit('next_addr', next_addr, broadcast=True)
    logger.info(f'Sent next address to the robot: {next_addr}')

    robot_status = robot.set_delivering()
    emit('status', robot_status, broadcast=True) # to robot
    logger.info('Sent delivering status to the robot')

    emit('robot_status', robot_status, broadcast=True) # to admin UI
    logger.info('Sent delivering status to the admin UI')

@socketio.on('info')
def handle_robot_status_from_robot(robot_info):
    global robot
    robot_info = robot.set_from_robot_info(robot_info)
    logger.info(f'Recieved robot info from robot: {robot_info}')

    emit('robot_status', robot_info[STATUS], broadcast=True)
    logger.info(f'Sent robot info to the UI: {robot_info}')

@socketio.on('delivery_status')
def handle_delivery_status_from_worker(delivery_status):
    global deliv_list, robot
    if delivery_status == Arrived.CORRECT:
        to_unload = deliv_list.get_curr_deliv()
        logger.info(f'Arrived at destination, unloading: {to_unload}')
        robot.inventory.unfill(to_unload)
        logger.info(f'Updated robot inventory upon delivery complete')

        robot_inv = robot.inventory.to_dict()
        emit('robot_inv', robot_inv, broadcast=True)
        logger.info(f'Sent robot inventory to the admin UI: {robot_inv}')

        next_deliv = deliv_list.set_curr_deliv_complete()
        logger.info('Updated current delivery as complete')
        emit('curr_deliv', next_deliv, broadcast=True)
        logger.info(f'Sent current delivery to the admin and  worker UI(for unloader): {next_deliv}')

        updated_now_delivering = deliv_list.to_dict()
        emit('now_delivering', updated_now_delivering, broadcast=True)
        logger.info(f'Sent updated list to admin UI: {updated_now_delivering}')

        # TODO: does scheduler write this into DB?
        emit('unload_complete', DeliveryStatus.COMPLETE, broadcast=True)
        logger.info('Send delivery complete message to the scheduler')

        next_addr = deliv_list.get_next_addr()
        if robot.is_turn(next_addr):
            robot.set_orientation_flip()
            emit('turn', broadcast=True)
            logger.info(f'Flipping robot orientation, now: {robot.orientation}')
        emit('next_addr', next_addr, broadcast=True)
        logger.info(f'Sent next addr to robot: {next_addr}')

        robot_status = robot.set_delivering()
        emit('status', robot_status, broadcast=True) # to robot
        emit('robot_status', robot_status, broadcast=True) # admin UI
        logger.info(f'Sent delivering mode to robot: {robot_status}')
        logger.info('Sent robot status to admin UI')

    elif delivery_status == Arrived.INCORRECT:
        robot.set_clockwise()
        logger.info('Robot orientation set to clockwise')
        robot_status = robot.set_maintenance()
        emit('robot_status', robot_status, broadcast=True) # admin UI
        emit('status', Arrived.INCORRECT, broadcast=True) # to robot
        logger.info(f'Put robot in maintenance mode due to incorrect delivery: {robot_status}')

@socketio.on('status_change')
def handle_robot_status(robot_status):
    global robot
    if robot_status == RobotStatus.MAINTENANCE:
        robot_status = robot.set_maintenance()
        logger.info('Put robot in maintenance mode manually')

    elif robot_status == RobotStatus.DELIVERING:
        robot_status = robot.set_delivering()
        logger.info('Put robot in delivering mode manually')

    emit('status', robot_status, broadcast=True) # to robot
    emit('robot_status',robot_status, broadcast=True) # back to admin UI

@socketio.on('replenish')
def update_loading_dock():
    global robot
    robot_inv = robot.inventory
    updated_inv = {RED: NUM_ITEM.RED - robot_inv.red,
                   GREEN: NUM_ITEM.GREEN - robot_inv.green,
                   BLUE: NUM_ITEM.BLUE - robot_inv.blue}
    emit('loading_dock_inv', updated_inv, broadcast=True)
    logger.info(f'Replenished inventory to {updated_inv}, sent to admin UI')

@socketio.on('deliv_prog')
def update_deliv_prog(deliv_prog):
    global order_db
    db_status = order_db.set_from_dict(deliv_prog)
    emit('deliv_prog', db_status, broadcast=True)
    logger.info('Update delivery progress on UI')

@socketio.on('video')
def stram_video(frame):
    global video
    video.set_frame(frame)

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
    order_db = OrderDB()
    video = Video()
    delivery_prob = DeliveryProgress()

    socketio.run(app, host='0.0.0.0', port=60000)

