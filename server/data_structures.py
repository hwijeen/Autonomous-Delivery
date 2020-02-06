import numpy as np
import cv2

from server_utils import only_when_not_empty

DELIV_LIST = 'deliv_list'
SUM = 'sum'
LATEST_ADDR = 'latest_addr'
NEXT_ADDR = 'next_addr'
ORIENTATION = 'orientation'
ADDR = 'addr'
RED = 'red'
GREEN = 'green'
BLUE = 'blue'
STATUS = 'status'

class NUM_ITEM:
    RED = 26
    GREEN = 26
    BLUE = 26

class RobotStatus:
    ARRIVIED = 'arrived'
    MAINTENANCE = 'maintenance'
    DELIVERING = 'delivering'
    OBSTACLE = 'obstacle'

class Orientation:
    CLOCK = 'clock'
    COUNTERCLOCK = 'counterclock'

class DeliveryStatus:
    PENDING = 'pending'
    COMPLETE = 'complete'

class Arrived:
    CORRECT = 'complete'
    INCORRECT = 'misdelivery'

class DBStats:
    NUM_PENDING = 'pending'
    NUM_COMPLETE = 'complete'
    NUM_TOTAL = 'total'


class Delivery:
    def __init__(self, addr, red, green, blue, status):
        self.addr = addr
        self.red = red
        self.green = green
        self.blue = blue
        self.status = status

    def __add__(self, other): # to use sum()
        red = self.red + other.red
        green = self.green + other.green
        blue = self.blue + other.blue
        return Delivery.from_dict({ADDR: None, RED: red, GREEN: green, BLUE: blue})

    def __radd__(self, other): # to use sum()
        if isinstance(other, int): return self
        else: self.__add__(other)

    @classmethod
    def from_dict(cls, dic, default_status=DeliveryStatus.PENDING):
        return cls(dic[ADDR], dic[RED], dic[GREEN], dic[BLUE], default_status)

    def to_dict(self):
        return {ADDR: self.addr, RED: self.red, GREEN: self.green,
                BLUE: self.blue, STATUS: self.status}

class DeliveryList: # For a round
    def __init__(self):
        self.deliv_list = []
        self.deliv_sum = {}
        self.curr_idx = 0

    def reverse_order(self):
        stop = self.deliv_list.pop(-1)
        self.deliv_list.reverse()
        self.deliv_list.append(stop)

    def update_from_scheduler(self, dict_list, orientation):
        self.deliv_list = [Delivery.from_dict(dic) for dic in dict_list]
        if orientation == Orientation.COUNTERCLOCK:
            self.reverse_order()
        self.deliv_sum = sum(self.deliv_list).to_dict()
        self.curr_idx = 0
        return self.to_dict()

    def get_curr_deliv(self):
        curr_deliv = self.deliv_list[self.curr_idx]
        return curr_deliv

    def set_curr_deliv_complete(self):
        curr_deliv = self.get_curr_deliv()
        curr_deliv.status = DeliveryStatus.COMPLETE
        self.curr_idx += 1
        return self.to_dict(), self.get_curr_deliv()

    def to_dict(self):
        #deliv_list = [d.to_dict() for d in self.deliv_list[self.curr_idx:]]
        deliv_list = [d.to_dict() for d in self.deliv_list[:-1]] # drop stop
        return {DELIV_LIST: deliv_list, SUM: self.deliv_sum}

class Inventory:
    def __init__(self, red, blue, green):
        self.red = red
        self.green = blue
        self.blue = green

    def fill(self, item_dict):
        self.red += item_dict[RED]
        self.green += item_dict[GREEN]
        self.blue += item_dict[BLUE]
        return self.to_dict()

    def unfill(self, item_dict):
        self.red -= item_dict[RED]
        self.green -= item_dict[GREEN]
        self.blue -= item_dict[BLUE]
        return self.to_dict()

    def set(self, item_dict):
        self.red = item_dict[RED]
        self.green = item_dict[GREEN]
        self.blue = item_dict[BLUE]
        return self.to_dict()

    def to_dict(self):
        return {RED: self.red, GREEN: self.green, BLUE: self.blue}

class Robot:
    def __init__(self):
        self.status = None
        self.latest_addr = 0
        self.next_addr = None
        self.orientation = Orientation.CLOCK
        self.inventory = Inventory(0, 0, 0)

    def update_from_robot(self, robot_info):
        self.latest_addr = robot_info[LATEST_ADDR]
        self.status = robot_info[STATUS]
        #self.orientation = robot_info[ORIENTATION]
        return self.to_dict()

    def set_status(self, robot_status):
        self.status = robot_status
        return self.to_dict()

    def upon_misdelivery(self):
        self.orientation = Orientation.CLOCK
        self.status = RobotStatus.MAINTENANCE
        self.latest_addr = 0
        return self.to_dict()

    def upon_delivery_complete(self, next_addr):
        self.next_addr = next_addr
        self.status = RobotStatus.DELIVERING
        return self.to_dict()

    def upon_load_complete(self, next_addr):
        self.next_addr = next_addr
        self.status = RobotStatus.DELIVERING
        return self.to_dict()

    def flip_orientation(self):
        self.orientation = Orientation.CLOCK if self.orientation == Orientation.COUNTERCLOCK else Orientation.COUNTERCLOCK
        return self.orientation

    def is_turn(self, next_addr):
        if self.orientation == Orientation.CLOCK:
            if self.latest_addr in {101, 102} and next_addr == 0:
                self.flip_orientation()
                return True
            elif self.latest_addr == 0 and next_addr in {201, 202, 203}:
                self.flip_orientation()
                return True
        if self.orientation == Orientation.COUNTERCLOCK:
            if self.latest_addr in {201, 202} and next_addr == 0:
                self.flip_orientation()
                return True
            elif self.latest_addr == 0 and next_addr in {101, 102, 103}:
                self.flip_orientation()
                return True
        return False

    def to_dict(self):
        return {STATUS: self.status, LATEST_ADDR:self.latest_addr,
                NEXT_ADDR: self.next_addr, ORIENTATION:self.orientation}

class LoadingDock:
    def __init__(self):
        self.inventory = Inventory(NUM_ITEM.RED, NUM_ITEM.GREEN, NUM_ITEM.BLUE)

class DataBase:
    def __init__(self, name, writer):
        self.name = name
        self.writer = writer
        self.num_pending = 0
        self.num_complete = 0
        self.num_total = 0
        self.step = 1

    def write_to_tensorboard(self, db_stats):
        num_backlog = db_stats[DBStats.NUM_PENDING + f'_{self.name}']
        num_total = db_stats[DBStats.NUM_TOTAL + f'_{self.name}']
        self.writer.add_scalar(f'Backlogs_over_time{self.name}', num_backlog, self.step)
        self.writer.add_scalar(f'Total_{self.name}s_over_time{self.name}', num_total, self.step)
        self.step += 1

    def set_from_dict(self, dic):
        self.num_pending = dic[DBStats.NUM_PENDING + f'_{self.name}']
        self.num_complete = dic[DBStats.NUM_COMPLETE + f'_{self.name}']
        self.num_total = self.num_pending + self.num_complete
        return self.to_dict()

    def to_dict(self):
        return {DBStats.NUM_PENDING + f'_{self.name}': self.num_pending,
                DBStats.NUM_COMPLETE + f'_{self.name}': self.num_complete,
                DBStats.NUM_TOTAL + f'_{self.name}': self.num_total}

class Video:
    def __init__(self):
        self.frame = b''

    def set_frame(self, stringData):
        self.frame = stringData

    def get_frame(self):
        return self.frame

