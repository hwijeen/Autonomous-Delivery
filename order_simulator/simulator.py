import sys; sys.path.append('../server')
from datetime import datetime, timedelta

import numpy as np
import socketio
import eventlet
from threading import Lock
from torch.utils.tensorboard import SummaryWriter

from simulator_utils import read_time_files
from data_structures import Robot, DeliveryList, DataBase


LOADING_TIME = 5
UNLOADING_TIME = 5

queue = []
queue_lock = Lock()
start = datetime(2020, 1, 1, 0, 0, 0)
now = datetime(2020, 1, 1, 0, 0, 0)
time_lock = Lock()
init_flag = False

sio = socketio.Server()
app = socketio.WSGIApp(sio)


@sio.on('deliv_list')
def stack_deliv_list(deliv_dict_list):
    global queue, robot
    deliv_list = DeliveryList()
    deliv_list.update_from_scheduler(deliv_dict_list, robot.orientation)

    queue_lock.acquire(); queue.append(deliv_list); queue_lock.release()

    simulate_round()

def simulate_round():
    global init_flag
    if not init_flag: return # runs only once
    init_flag = True

    global queue, now, timer
    while len(queue) != 0:
        queue_lock.acquire(); this_round = queue.pop(0); queue_lock.release()

        for deliv in this_round.deliv_list:
            robot.get_ready_for_next_deliv(deliv.addr)

            if robot.is_turn():
                turn_sec = timer.turn_time(at=robot.latest_addr)
                print("Turning robot at {robot.latest_addr}: took {turn_sec} seconds.")
                time_lock.acquire(); now += timedelta(seconds=turn_sec); time_lock.release()

            travel_sec = timer.travel_time(robot.orientation, robot.latest_addr, deliv.addr)
            print("Driving robot from {robot.latest_addr} to {robot.next_addr} took {travel_sec} seconds")
            time_lock.acquire(); now += timedelta(seconds=travel_sec); time_lock.release()

            if deliv.addr != 0:
                unloading_sec = timer.unloading_time()
                print("Unloading took {unloading_sec} seconds")
                time_lock.acquire(); now += timedelta(seconds=unloading_sec); time_lock.release()

            sio.emit('unload_complete', 'complete', broadcast=True) # to scheduler
            print()

@sio.on('deliv_prog')
def update_deliv_prog(deliv_prog):
    global order_db, item_db, now, start
    order_db_stats = order_db.set_from_dict(deliv_prog)
    item_db_stats = item_db.set_from_dict(deliv_prog)
    db_stats = {**order_db_stats, **item_db_stats}
    time_lock.acquire
    walltime = (now - start).total_seconds()
    time_lock.release
    order_db.write_to_tensorboard(db_stats, walltime)
    item_db.write_to_tensorboard(db_stats, walltime)

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

    eventlet.wsgi.server(eventlet.listen(('', 5000)), app)
