import numpy as np
import cv2

from server_utils import only_when_not_empty

ADDR = 'addr'
RED = 'red'
GREEN = 'green'
BLUE = 'blue'
STATUS = 'status'
NUM_ITEM = 26

class RobotStatus:
    ARRIVIED = 'arrived'
    MAINTENANCE = 'maintenance'
    DELIVERING = 'delivering'
    OBSTACLE = 'obstacle'

class RobotRotation:
    CLOCK = 'clock'
    COUNTERCLOCK = 'counterclock'

class DeliveryStatus:
    PENDING = 'pending'
    COMPLETE = 'complete'

class Arrived:
    CORRECT = 'complete'
    INCORRECT = 'misdelivery'


class Delivery:
    def __init__(self, addr, red, green, blue, status):
        self.addr = addr
        self.red = red
        self.green = green
        self.blue = blue
        self.status = status

    def set_complete(self):
        self.status = DeliveryStatus.COMPLETE

    def __add__(self, other):
        red = self.red + other.red
        green = self.green + other.green
        blue = self.blue + other.blue
        return Delivery.from_dict({ADDR: None, RED: red, GREEN: green,
                                   BLUE: blue})

    def __radd__(self, other):
        if isinstance(other, int): return self
        else: self.__add__(other)

    def to_dict(self, drop_status=False, drop_addr=False):
        deliv_dict = {ADDR: self.addr, RED: self.red, GREEN: self.green,
                      BLUE: self.blue, STATUS: self.status}
        if drop_status:
            deliv_dict.pop(STATUS)
        if drop_addr:
            deliv_dict.pop(ADDR)
        return deliv_dict

    @classmethod
    def from_dict(cls, dic):
        return cls(dic[ADDR], dic[RED], dic[GREEN], dic[BLUE],
                   DeliveryStatus.PENDING)

class DeliveryList: # For a round
    def __init__(self):
        self.deliv_list = []
        self.curr_idx = 0

    def set_from_dict_list(self, dict_list, rotation):
        stop_dropped = dict_list[:-1]
        if rotation == RobotRotation.COUNTERCLOCK:
            stop_dropped.reverse()
        self.deliv_list = [Delivery.from_dict(dic) for dic in stop_dropped]
        self.curr_idx = 0

    def set_curr_deliv_complete(self):
        curr_deliv = self.get_curr_deliv()
        curr_deliv.set_complete()
        self.curr_idx += 1

    @only_when_not_empty
    def get_curr_deliv(self, to_dict=False, drop_status=True): # to admin UI
        curr_deliv = self.deliv_list[self.curr_idx]
        if to_dict:
            curr_deliv = curr_deliv.to_dict(drop_status)
        return curr_deliv

    @only_when_not_empty
    def get_next_addr(self): # to robot
        curr_deliv = self.get_curr_deliv()
        next_addr = curr_deliv.addr
        return next_addr

    @only_when_not_empty
    def get_deliv_list(self, drop_status, add_sum): # to worker UI
        deliv_list = [d.to_dict(drop_status) for d in self.deliv_list]
        data = {'deliv_list': deliv_list}
        if add_sum:
            merged_deliv = sum(self.deliv_list)
            item_sum = merged_deliv.to_dict(drop_status=True, drop_addr=True)
            data['sum'] = item_sum
        return data

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
        self.rotation = RobotRotation.CLOCK
        self.inventory = Inventory(0, 0, 0)

    def set_from_robot_info(self, robot_info):
        self.latest_addr = robot_info[ADDR]
        self.status = robot_info[STATUS]

    def set_delivering(self):
        self.status = RobotStatus.DELIVERING

    def set_maintenance(self):
        self.status = RobotStatus.MAINTENANCE

    def set_rotation_flip(self):
        self.rotation = RobotRotation.CLOCK if self.rotation == RobotRotation.COUNTERCLOCK else RobotRotation.COUNTERCLOCK

    def set_clockwise(self):
        self.rotation = RobotRotation.CLOCK

    def get_status(self):
        return self.status

    def is_turn(self, next_addr):
        if self.rotation == RobotRotation.CLOCK:
            if self.latest_addr in {101, 102} and next_addr is None:
                return True
            elif self.latest_addr == None and next_addr in {201, 202}:
                return True
        if self.rotation == RobotRotation.COUNTERCLOCK:
            if self.latest_addr in {201, 202} and next_addr is None:
                return True
            elif self.latest_addr == None and next_addr in {101, 102}:
                return True
        return False


class LoadingDock:
    def __init__(self):
        self.inventory = Inventory(NUM_ITEM, NUM_ITEM, NUM_ITEM)

class OrderDB:
    def __init__(self):
        self.num_pending = 0
        self.num_complete = 0
        self.num_total_orders = 0

    def update_from_dict(self, dic):
        self.num_pending = dic['num_pending']
        self.num_complete = dic['num_complete']
        self.num_total_orders = self.num_pending + self.num_complete

    def to_dict(self):
        return {'num_pending': self.num_pending,
                'num_complete': self.num_complete,
                'total_orders': self.num_total_orders}

class Video:
    def __init__(self):
        self.frame = b''

    def set_frame(self, stringData):
        self.frame = stringData

    def get_frame(self):
        return self.frame

