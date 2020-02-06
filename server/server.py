import logging

from flask import Flask, render_template, request, Response
from flask_socketio import SocketIO, emit
from torch.utils.tensorboard import SummaryWriter


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
    global deliv_list, robot, order_db, item_db
    now_delivering = deliv_list.to_dict()
    emit('now_delivering', now_delivering, broadcast=True)

    try:
        curr_deliv = deliv_list.get_curr_deliv().to_dict()
        emit('curr_deliv', curr_deliv, broadcast=True)
    except:
        pass

    robot_inv = robot.inventory.to_dict()
    emit('robot_inv', robot_inv, broadcast=True)

    robot_info = robot.to_dict()
    emit('robot_info', robot_info, broadcast=True)

    loading_dock_inv = loading_dock.inventory.to_dict()
    emit('loading_dock_inv', loading_dock_inv, broadcast=True)

    order_db_stats = order_db.to_dict()
    item_db_stats = item_db.to_dict()
    db_stats = {**order_db_stats, **item_db_stats}
    emit('deliv_prog', db_stats, broadcast=True)

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

    curr_deliv = deliv_list.get_curr_deliv().to_dict()
    emit('curr_deliv', curr_deliv, broadcast=True)
    logger.info(f'Sent current delivery to UI: {curr_deliv}')

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
    global order_db, item_db
    order_db_stats = order_db.set_from_dict(deliv_prog)
    item_db_stats = item_db.set_from_dict(deliv_prog)
    db_stats = {**order_db_stats, **item_db_stats}
    emit('deliv_prog', db_stats, broadcast=True)
    logger.info('Update delivery progress on UI')

    order_db.write_to_tensorboard(db_stats)
    item_db.write_to_tensorboard(db_stats)


if __name__ == "__main__":

    deliv_list = DeliveryList()
    robot = Robot()
    loading_dock = LoadingDock()
    writer = SummaryWriter()
    order_db = DataBase(name='order', writer=writer)
    item_db = DataBase(name='item', writer=writer)

    socketio.run(app, host='0.0.0.0', port=60000)
