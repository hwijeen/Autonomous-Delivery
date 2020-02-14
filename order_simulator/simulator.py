import time
import sys; sys.path.append('../server')
from datetime import datetime, timedelta

import numpy as np
import socketio
import eventlet
from threading import Lock, Thread
from torch.utils.tensorboard import SummaryWriter

from simulator_utils import read_time_files
from data_structures import Robot, DeliveryList, DataBase


LOADING_TIME = 5
UNLOADING_TIME = 5

start = datetime(2020, 1, 1, 0, 0, 0)
now = datetime(2020, 1, 1, 0, 0, 0)

sio = socketio.Server()
app = socketio.WSGIApp(sio)
PORT = 60001

@sio.on('hello')
def init_req(sid, msg):
    global now
    req_time = now.strftime('%Y-%m-%d %H:%M:%S')
    time.sleep(1)
    sio.emit('request_deliv_list', req_time) # almost same as in the last address
    print(f'Requested delivery list at {req_time}')

@sio.on('connect')
def greeting(*args):
    print('Connected!')

@sio.on('deliv_list')
def stack_deliv_list(sid, deliv_dict_list):
    global robot, deliv_list, now
    if len(deliv_dict_list) == 1:
        now += timedelta(seconds=10)
        req_time = now.strftime('%Y-%m-%d %H:%M:%S')
        time.sleep(1)
        sio.emit('request_deliv_list', req_time) # almost same as in the last address
        print(f'Requested delivery list at {req_time}')
        return

    deliv_list.update_from_scheduler(deliv_dict_list, robot.orientation)

    simulate_round()

    req_time = now.strftime('%Y-%m-%d %H:%M:%S')
    time.sleep(3)
    sio.emit('request_deliv_list', req_time) # almost same as in the last address
    print(f'Requested delivery list at {req_time}')


def simulate_round():
    global now, timer, deliv_list
    print('='*80)
    start_time = now.strftime('%Y-%m-%d %H:%M:%S')
    print(f'Simulation starting for round {deliv_list.num_round} at {start_time}')
    print('-'.join([str(d.addr) for d in deliv_list.deliv_list]))

    for deliv in deliv_list.deliv_list:
        robot.latest_addr = robot.next_addr
        robot.get_ready_for_next_deliv(deliv.addr)

        if robot.is_turn():
            turn_sec = timer.turn_time(at=robot.latest_addr)
            print(f"\tTurning robot at {robot.latest_addr}: took {turn_sec:.2f} seconds.")
            now += timedelta(seconds=turn_sec)

        travel_sec = timer.travel_time(robot.orientation, robot.latest_addr, deliv.addr)
        print(f"Driving robot from {robot.latest_addr} to {robot.next_addr} took {travel_sec:.2f} seconds")
        now += timedelta(seconds=travel_sec)

        # robot.latest_addr = robot.next_addr
        # robot.get_ready_for_next_deliv(deliv.addr)

        if deliv.addr != 0:
            unloading_sec = timer.unloading_time()
            print(f"\tUnloading took {unloading_sec:.2f} seconds")
            now += timedelta(seconds=unloading_sec)

            time.sleep(3)
            complete_msg = {'addr': deliv.addr, 'time': now.strftime('%Y-%m-%d %H:%M:%S')}
            sio.emit('unload_complete', complete_msg) # to scheduler

            print('Sent unload complete message to the scheduler')
    print('='*80 + '\n')

@sio.on('deliv_prog')
def update_deliv_prog(sid, deliv_prog):
    global order_db, item_db, now, start
    print(f'Delivery progress received from scheduler: {deliv_prog}')
    order_db_stats = order_db.set_from_dict(deliv_prog)
    item_db_stats = item_db.set_from_dict(deliv_prog)
    db_stats = {**order_db_stats, **item_db_stats}
    walltime = (now - start).total_seconds()
    order_db.write_to_tensorboard(db_stats, walltime)
    item_db.write_to_tensorboard(db_stats, walltime)
    print(f'Written to tensorboard')

class Timer:
    def __init__(self, clock, counterclock, turn):
        self.clock = clock
        self.counterclock = counterclock
        self.turn = turn
        self.loading = LOADING_TIME
        self.unloading = UNLOADING_TIME
        self.eps = 0.1

    def travel_time(self, orientation, from_, to):
        assert orientation in {'clock', 'counterclock'}
        time_dict = self.clock if orientation == 'clock' else self.counterclock
        return np.random.normal(time_dict[from_][to], self.eps)

    def turn_time(self, at):
        return np.random.normal(self.turn[at], self.eps)

    def loading_time(self):
        return np.random.normal(self.loading, self.eps)

    def unloading_time(self):
        return np.random.normal(self.unloading, self.eps)

    @classmethod
    def from_files(cls, clock_fpath, counterclock_fpath, turn_fpath):
        clock, counterclock, turn = read_time_files(clock_fpath, counterclock_fpath, turn_fpath)
        return cls(clock, counterclock, turn)


if __name__ == "__main__":
    clock_fpath = 'time_files/clock.csv'
    counterclock_fpath = 'time_files/counter_clock.csv'

    turn_fpath = 'time_files/turn.csv'

    timer = Timer.from_files(clock_fpath, counterclock_fpath, turn_fpath)
    robot = Robot()
    deliv_list = DeliveryList()
    writer = SummaryWriter(comment='simulated')
    order_db = DataBase('order', writer)
    item_db = DataBase('item', writer)

    print(f'Server running at port {PORT}')
    eventlet.wsgi.server(eventlet.listen(('', PORT)), app, log_output=False)

