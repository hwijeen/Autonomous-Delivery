import numpy as np
import cv2

from server_utils import only_when_not_empty

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
    NUM_PENDING = 'num_pending'
    NUM_COMPLETE = 'num_complete'
    NUM_TOTAL = 'total_orders'


class Delivery:
    def __init__(self, addr, red, green, blue, status):
        self.addr = addr
        self.red = red
        self.green = green
        self.blue = blue
        self.status = status

    def set_complete(self):
        self.status = DeliveryStatus.COMPLETE

    def __add__(self, other): # to use sum()
        red = self.red + other.red
        green = self.green + other.green
        blue = self.blue + other.blue
        return Delivery.from_dict({ADDR: None, RED: red, GREEN: green,
                                   BLUE: blue})

    def __radd__(self, other): # to use sum()
        if isinstance(other, int): return self
        else: self.__add__(other)

    @only_when_not_empty
    def to_dict(self):
        return {ADDR: self.addr, RED: self.red, GREEN: self.green,
                BLUE: self.blue, STATUS: self.status}

    @classmethod
    def from_dict(cls, dic):
        return cls(dic[ADDR], dic[RED], dic[GREEN], dic[BLUE],
                   DeliveryStatus.PENDING)

class DeliveryList: # For a round
    def __init__(self):
        self.deliv_list = []
        self.deliv_sum = {}
        self.curr_idx = 0

    def set_from_dict_list(self, dict_list, orientation):
        stop_dropped = dict_list[:-1]
        if orientation == Orientation.COUNTERCLOCK:
            stop_dropped.reverse()
        self.deliv_list = [Delivery.from_dict(dic) for dic in stop_dropped]
        self.curr_idx = 0
        merged_deliv = sum(self.deliv_list)
        self.deliv_sum = merged_deliv.to_dict()
        return self.to_dict()

    def set_curr_deliv_complete(self):
        curr_deliv = self.get_curr_deliv(to_dict=False)
        curr_deliv.set_complete()
        self.curr_idx += 1
        return self.get_curr_deliv()

    @only_when_not_empty
    def get_curr_deliv(self, to_dict=True):
        curr_deliv = self.deliv_list[self.curr_idx]
        if to_dict:
            curr_deliv = curr_deliv.to_dict()
        return curr_deliv

    @only_when_not_empty
    def get_next_addr(self):
        return self.get_curr_deliv(to_dict=False).addr

    @only_when_not_empty
    def to_dict(self):
        deliv_list = [d.to_dict() for d in self.deliv_list]
        return {'deliv_list': deliv_list, 'sum': self.deliv_sum}

class DeliveryProgress:
    def set_from_dict(self, dic):
        self.num_pending = dic['num_pending']
        self.num_complete = dic['num_complete']

    def get_status(self):
        event_name = 'deliv_prog'
        data =  {'num_pending': self.num_pending,
                 'num_complete': self.num_complete,
                 'total_orders': self.num_pending + self.num_complete}
        return event_name, data

class Inventory:
    def __init__(self, red, blue, green):
        self.red = red
        self.green = blue
        self.blue = green

    @only_when_not_empty
    def fill(self, item_dict):
        self.red += item_dict[RED]
        self.green += item_dict[GREEN]
        self.blue += item_dict[BLUE]

    @only_when_not_empty
    def unfill(self, item_dict):
        self.red -= item_dict[RED]
        self.green -= item_dict[GREEN]
        self.blue -= item_dict[BLUE]

    def to_dict(self):
        return {RED: self.red, GREEN: self.green, BLUE: self.blue}

class Robot:
    def __init__(self):
        self.status = None
        self.latest_addr = None
        self.orientation = Orientation.CLOCK
        self.inventory = Inventory(0, 0, 0)

    def set_from_robot_info(self, robot_info):
        self.latest_addr = robot_info[ADDR]
        self.status = robot_info[STATUS]
        return self.to_dict()

    def set_delivering(self):
        self.status = RobotStatus.DELIVERING
        return self.status

    def set_maintenance(self):
        self.status = RobotStatus.MAINTENANCE
        return self.status

    def set_orientation_flip(self):
        self.orientation = Orientation.CLOCK if self.orientation == Orientation.COUNTERCLOCK else Orientation.COUNTERCLOCK

    def set_clockwise(self):
        self.orientation = Orientation.CLOCK

    def get_status(self):
        return self.status

    def is_turn(self, next_addr):
        if self.orientation == Orientation.CLOCK:
            if self.latest_addr in {101, 102} and next_addr is None:
                return True
            elif self.latest_addr == None and next_addr in {201, 202}:
                return True
        if self.orientation == Orientation.COUNTERCLOCK:
            if self.latest_addr in {201, 202} and next_addr is None:
                return True
            elif self.latest_addr == None and next_addr in {101, 102}:
                return True
        return False

    def to_dict(self):
        return {STATUS: self.status, ADDR:self.latest_addr,
                'orientation':self.orientation}

class LoadingDock:
    def __init__(self):
        self.inventory = Inventory(NUM_ITEM.RED, NUM_ITEM.GREEN, NUM_ITEM.BLUE)

class OrderDB:
    def __init__(self):
        self.num_pending = 0
        self.num_complete = 0
        self.num_total = 0

    def set_from_dict(self, dic):
        self.num_pending = dic[DBStats.NUM_PENDING]
        self.num_complete = dic[DBStats.NUM_COMPLETE]
        self.num_total = self.num_pending + self.num_complete
        return self.to_dict()

    def to_dict(self):
        return {DBStats.NUM_PENDING: self.num_pending,
                DBStats.NUM_COMPLETE: self.num_complete,
                DBStats.NUM_TOTAL: self.num_total}

class Video:
    def __init__(self):
        self.frame = b''

    def set_frame(self, stringData):
        self.frame = stringData

    def get_frame(self):
        return self.frame

