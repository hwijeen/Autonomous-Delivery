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
        global deliv_list, robot, order_db
        now_delivering = deliv_list.to_dict()
        emit('now_delivering', now_delivering, broadcast=True)

        robot_inv = robot.inventory.to_dict()
        emit('robot_inv', robot_inv, broadcast=True)

        robot_info = robot.to_dict()
        emit('robot_info', robot_info, broadcast=True)

        loading_dock_inv = loading_dock.inventory.to_dict()
        emit('loading_dock_inv', loading_dock_inv, broadcast=True)

        db_status = order_db.set_from_dict(deliv_prog)
        emit('deliv_prog', db_status, broadcast=True)
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
    logger.info(f'Received delivery list from scheduler: {deliv_dict_list}')
    orientation = robot.orientation
    now_delivering = deliv_list.update_from_scheduler(deliv_dict_list, orientation)
    emit('now_delivering', now_delivering, broadcast=True)
    logger.info(f'Setting delivery list: {now_delivering}')

@socketio.on('load_complete')
def start_round():
    global deliv_list, robot, loading_dock
    to_load = deliv_list.deliv_sum
    robot.inventory.fill(to_load)
    loading_dock.inventory.unfill(to_load)

    robot_inv = robot.inventory.to_dict()
    loading_dock_inv = loading_dock.inventory.to_dict()
    emit('robot_inv', robot_inv, broadcast=True)
    emit('loading_dock_inv', loading_dock_inv, broadcast=True)

    next_addr = deliv_list.get_curr_deliv().addr
    if robot.is_turn(next_addr):
        emit('turn', broadcast=True)
        logger.info('Flipping robot')
    robot_info = robot.upon_load_complete(next_addr)
    emit('robot_info', robot_info, broadcast=True)
    logger.info(f'Sending info to robot {robot_info}')

@socketio.on('robot_info')
def update_from_robot(robot_info):
    global robot
    robot_info = robot.update_from_robot(robot_info)
    logger.info(f'Recieved robot info from robot: {robot_info}')
    emit('robot_info', robot_info, broadcast=True)

@socketio.on('delivery_status')
def handle_delivery_status_from_worker(delivery_status):
    global deliv_list, robot
    if delivery_status == Arrived.CORRECT:
        to_unload = deliv_list.get_curr_deliv().to_dict()
        robot_inv = robot.inventory.unfill(to_unload)
        emit('robot_inv', robot_inv, broadcast=True)

        updated_now_delivering, next_deliv = deliv_list.set_curr_deliv_complete()
        emit('now_delivering', updated_now_delivering, broadcast=True)
        logger.info(f'Updated now delivering: {updated_now_delivering}')

        emit('unload_complete', DeliveryStatus.COMPLETE, broadcast=True)

        robot.upon_delivery_complete(next_deliv.addr)
        if robot.is_turn(next_deliv.addr):
            emit('turn', broadcast=True)
            logger.info('Flipping robot')
        emit('robot_info', robot.to_dict(), broadcast=True)
        logger.info(f'Sending info to robot {robot.to_dict()}')

    elif delivery_status == Arrived.INCORRECT:
        robot_info = robot.upon_misdelivery()
        emit('robot_info', robot_info, broadcast=True)

@socketio.on('status_change')
def handle_robot_status(robot_status):
    global robot
    robot_info = robot.set_status(robot_status)
    emit('robot_info', robot_info, broadcast=True)

@socketio.on('replenish')
def update_loading_dock():
    global robot, loading_dock
    robot_inv = robot.inventory
    updated_inv = {RED: NUM_ITEM.RED - robot_inv.red,
                   GREEN: NUM_ITEM.GREEN - robot_inv.green,
                   BLUE: NUM_ITEM.BLUE - robot_inv.blue}
    loading_dock.inventory.set(updated_inv)
    emit('loading_dock_inv', updated_inv, broadcast=True)
    logger.info(f'Replenished inventory to {updated_inv}, sent to admin UI')

@socketio.on('deliv_prog')
def update_deliv_prog(deliv_prog):
    global order_db
    db_stats = order_db.set_from_dict(deliv_prog)
    emit('deliv_prog', db_stats, broadcast=True)
    logger.info('Update delivery progress on UI')

    num_backlog = db_stats[DBStats.NUM_PENDING]
    num_total = db_stats[DBStats.NUM_TOTAL]
    order_db.write_to_tensorboard(num_backlog, num_total)

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

    socketio.run(app, host='0.0.0.0', port=60000)
