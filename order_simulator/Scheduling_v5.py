import numpy as np
import mysql.connector as mysql
import pdb
import datetime
import pickle
from sys import *
from copy import deepcopy
import time
from table_manager import create_table, copy_table

import socketio

flag_ = 0

class Socket:
    def __init__(self):
        self.sio = socketio.Client()
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('connect_error', self.connect_error)

    def on_connect(self):
        print("I'm connected!")
        global flag_
        flag_ = 1

    def connect_error(self):
        print("The connection failed!")

    def disconnect(self):
        print("I'm disconnected")
        global flag_
        flag_ = 0


class Scheduler():
    def __init__(self):
        #Remaining cubes on tray
        self.red = 0
        self.green = 0
        self.blue = 0
        self.capacity = 20
        self.orders_dict = {}
        self.loading_seq = []
        self.delivery_list = []
        self.rev_list = []

        self.round = 0
        self.db = db = mysql.connect(
                host = "localhost",
                user = "user",
                passwd = "hotmetal",
                database = "orderdb"
            )
        self.cursor = self.db.cursor()

        self.get_orders_by_FIFO()

    def __del__(self):
        print('One Round DONE', end='\r')

    def unload_items(self, r=0, g=0, b=0):
        self.capacity += (r+g+b)
        self.red -= r
        self.green -= g
        self.blue -= b

    def load_items(self, r=0, g=0, b=0):
        self.capacity -= (r+g+b)
        self.red += r
        self.green += g
        self.blue += b

    def sort_by_address(self):
        list_seq = [101, 102, 103, 203, 202, 201]
        result_list = []

        for addr_ in list_seq:
            for order_ in self.delivery_list:
                if order_['addr'] == addr_:
                    result_list.append(order_)
        self.delivery_list = result_list

    def get_delivery_list(self):
        for order_ in self.loading_seq:

            if order_['round'] == 1:
                self.delivery_list.append({'addr':order_['addr'], 'red':order_['red'], 'green':order_['green'], 'blue':order_['blue']})
        # self.delivery_list.append({'addr':0, 'red':0, 'green':0, 'blue':0})
        self.sort_by_address()

        return self.delivery_list

    def get_delivery_list2(self):

        return self.delivery_list

    def make_shortcut(self, order_seq):
        i=0
        mask_1 = np.isin(np.array(order_seq), [101, 102])
        mask_2 = np.isin(np.array(order_seq), [201, 202])

        if mask_1.sum() >= 1:
            if 101 in order_seq:
                if self.orders_dict[101]['red'] + self.orders_dict[101]['green'] + self.orders_dict[101]['blue'] >= 20:
                    return [101]
                else:
                    if 102 in order_seq:
                        if self.orders_dict[101]['red'] + self.orders_dict[101]['green'] + self.orders_dict[101]['blue']+\
                            self.orders_dict[102]['red'] + self.orders_dict[102]['green'] + self.orders_dict[102]['blue'] >= 20:
                            return [101, 102]
            else:
                if self.orders_dict[102]['red'] + self.orders_dict[102]['green'] + self.orders_dict[102]['blue'] >= 20:
                    return [102]

        if mask_2.sum() >= 1:
            if 201 in order_seq:
                if self.orders_dict[201]['red'] + self.orders_dict[201]['green'] + self.orders_dict[201]['blue'] >= 20:
                    return [201]
                else:
                    if 202 in order_seq:
                        if self.orders_dict[201]['red'] + self.orders_dict[201]['green'] + self.orders_dict[201]['blue']+\
                            self.orders_dict[202]['red'] + self.orders_dict[202]['green'] + self.orders_dict[202]['blue'] >= 20:
                            return [201, 202]

        return order_seq

    def get_orders_by_FIFO(self):
        query = "SELECT address, red, green, blue, id FROM items WHERE sub_id = 0"
        # query = "SELECT address, red, green, blue, id FROM ORDERS WHERE pending=1"

        self.cursor.execute(query)
        orderdb = self.cursor.fetchall()
        # orders = np.array(orderdb)

        order_seq = []
        i = 0

        for order in orderdb:
            addr = order[0]
            id_ = order[4]

            if addr not in order_seq: #FIFO
                order_seq.append(addr)

            if addr not in self.orders_dict.keys():
                self.orders_dict[addr] = {'red': order[1], 'green':order[2], 'blue':order[3], 
                                    'order_seq':[{'red': order[1], 'green':order[2], 'blue':order[3]}],
                                    'id':[id_]
                                    }
            else:
                self.orders_dict[addr]['red'] += order[1]
                self.orders_dict[addr]['green'] += order[2]
                self.orders_dict[addr]['blue'] += order[3]
                self.orders_dict[addr]['order_seq'].append({'red': order[1], 'green':order[2], 'blue':order[3]})
                self.orders_dict[addr]['id'].append(id_)

        order_seq = self.make_shortcut(order_seq)

        while i < len(order_seq):

            addr = order_seq[i]

            r_, g_, b_ = self.orders_dict[addr]['red'], self.orders_dict[addr]['green'], self.orders_dict[addr]['blue']

            if (r_, g_, b_) == (0, 0, 0):
                i += 1
                continue
            self.round += 1
            item_cnt = r_ + g_ + b_

            if item_cnt >= self.capacity: # more than capacity 
                if r_ >= self.capacity:
                    # self.load_items(self.capacity, 0, 0)
                    self.orders_dict[addr]['red'] -= self.capacity
                    self.loading_seq.append({'addr':addr, 'red': self.capacity, 'green':0, 'blue':0, 'round': self.round})
                    self.capacity = 20
                    # self.load_items(r_, g_, b_)
                    # self.unload_items(self.capacity, 0, 0)

                elif r_ + g_ >= self.capacity:
                    # self.load_items(r_, self.capacity - r_, 0)
                    self.orders_dict[addr]['red'] -= r_
                    self.orders_dict[addr]['green'] -= (self.capacity - r_)
                    self.loading_seq.append({'addr':addr, 'red': r_, 'green':self.capacity - r_, 'blue':0, 'round': self.round})
                    # self.load_items(r_, g_, b_)
                    self.capacity = 20
                    # self.unload_items(r_, self.capacity - r_, 0)

                else:
                    self.orders_dict[addr]['red'] -= r_
                    self.orders_dict[addr]['green'] -= g_
                    self.orders_dict[addr]['blue'] -= (self.capacity - r_ - g_)
                    self.loading_seq.append({'addr':addr, 'red': r_, 'green':g_, 'blue':(self.capacity - r_ - g_), 'round': self.round})
                    # self.load_items(r_, g_, b_)
                    self.capacity = 20

            else:
                self.load_items(r_, g_, b_)
                self.orders_dict[addr]['red'] -= r_
                self.orders_dict[addr]['green'] -= g_
                self.orders_dict[addr]['blue'] -= b_
                self.loading_seq.append({'addr':addr, 'red': r_, 'green':g_, 'blue':b_, 'round': self.round})
                self.round -= 1
                i += 1 #next address

    def get_loading_order(self, scheduled_list):
        if scheduled_list:
            cube_to_loaded = {'red': 0, 'green': 0, 'blue': 0}

            for schedule_ in scheduled_list:
                cube_to_loaded['red'] += schedule_['red']
                cube_to_loaded['green'] += schedule_['green']
                cube_to_loaded['blue'] += schedule_['blue']

        return cube_to_loaded

    def get_reverse_ref_list(self):
        for loading_order in self.loading_seq:
            if loading_order['round'] == 1:
                addr = loading_order['addr']
                order_seq_ = self.orders_dict[addr]['order_seq']
                id_ = self.orders_dict[addr]['id']

                for i in range(len(order_seq_)):
                    self.rev_list.append( {'addr':addr, 'red':order_seq_[i]['red'], 'green':order_seq_[i]['green'], 'blue':order_seq_[i]['blue'], 'id':id_[i]} )   

    def append_stop(self):
        self.delivery_list.append({'addr':0, 'red':0, 'green':0, 'blue':0})


    def update_item_tables(self, data):
        # 1. Get addreses and the number of to-be-loaded cubes
        delivery = self.delivery_list[0]
        rev_list = self.rev_list

        for i in range(len(rev_list)):
            order_ = rev_list[i]

            if order_ == 0:
                break
            if delivery['addr'] == 0:
                break

            if order_['addr'] == delivery['addr']:

                ordered_r, ordered_g, ordered_b = order_['red'], order_['green'], order_['blue']

                if ordered_r >= delivery['red']:
                    new_r = ordered_r - delivery['red']
                    delivered_r = delivery['red']
                else:
                    new_r = 0
                    delivered_r = ordered_r

                if ordered_g >= delivery['green']:
                    new_g = ordered_g - delivery['green']
                    delivered_g = delivery['green']
                else:
                    new_g = 0
                    delivered_g = ordered_g

                if ordered_b >= delivery['blue']:
                    new_b = ordered_b - delivery['blue']
                    delivered_b = delivery['blue']
                else:
                    new_b = 0
                    delivered_b = ordered_b

                # Update row where 'sub_id == 0'
                query1 = "UPDATE items SET red = {}, green = {}, blue = {} WHERE id = {} AND sub_id = 0".format( str(new_r), str(new_g), str(new_b), str(order_['id']) )

                self.cursor.execute(query1)
                self.db.commit()

                # Delete row where 'sub_id == i'
                query2 = "SELECT red, green, blue, sub_id FROM items WHERE id = {}".format( str(order_['id']))
                self.cursor.execute(query2)

                (_, _, _, sub_id) = self.cursor.fetchall()[-1]

                if (new_r, new_g, new_b) == (0, 0, 0):
                    # update items table that order is completed
                    query3_1 = "UPDATE items SET filldate = now() WHERE id = {} AND sub_id = {}".format(str(order_['id']), str(0) )

                    self.cursor.execute(query3_1)
                    self.db.commit()

                    # update orders table that order is completed
                    query3_2 = "UPDATE orders SET filldate = now(), pending = 0 WHERE id = {}".format( str(order_['id']) )

                    self.cursor.execute(query3_2)
                    self.db.commit()

                # Add row where 'sub_id == i'
                query4 = "INSERT INTO items(id, sub_id, red, green, blue, filldate, address) VALUES ({}, {}, {}, {}, {}, {}, {})".format( str(order_['id']), str(sub_id + 1), str(delivered_r), str(delivered_g), str(delivered_b),'current_timestamp', order_['addr'])

                self.cursor.execute(query4)
                self.db.commit()

        if delivery['addr'] != 0:
            del self.delivery_list[0]

    def send_message(self):
        self.sio.emit('deliv_list', self.delivery_list)

    def get_message(self, data):
        update_item_tables(delivery_, rev_list)
        del self.delivery_list[0]



    # For checking backlog 
    def check_max_delay(self, cursor, orders):
        max_time = max(orders[:,0])
        cur_time = datetime.datetime.now()
        time_threshold = 100
        return ( (cur_time - max_time).seconds > time_threshold )


def main():

    create_table()

    socket = Socket()
    socket.sio.connect('http://172.26.226.35:60000')

    while True: # Scheduling per one rep
        copy_table() # Update 'items' table
        scheduler = Scheduler()
        socket.sio.on('unload_complete', scheduler.update_item_tables)
        deliv_list = scheduler.get_delivery_list()
        scheduler.get_reverse_ref_list()
        scheduler.append_stop()
        if len(deliv_list) != 1:
            socket.sio.emit('deliv_list', deliv_list)

        global flag_
        while flag_:

            deliv_list = scheduler.get_delivery_list2()
            if len(deliv_list) == 1 or len(deliv_list) == 0:
                break
            time.sleep(0.5)

        del scheduler
        time.sleep(0.5)

if __name__ == "__main__":
    main()
