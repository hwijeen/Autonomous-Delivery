import socketio
import time
import mysql.connector as mysql
import pdb


class Socket:
    def __init__(self):
        self.sio = socketio.Client()
        self.sio.on('connect', self.on_connect)
        self.sio.on('disconnect', self.disconnect)
        self.sio.on('connect_error', self.connect_error)

    def on_connect(self):
        print("I'm connected!")

    def connect_error(self):
        print("The connection failed!")

    def disconnect(self):
        print("I'm disconnected")

class DB_Reader():
    def __init__(self, flag):
        self.db = db = mysql.connect(
                host = "localhost",
                user = "root",
                passwd = "",
                database = "orderdb"
            )
        self.cursor = self.db.cursor()
        
        self.cur_val = flag
        self.prev_val = None
    
    def init_flag(self):
        query = "CHECKSUM TABLE items"
        self.cursor.execute(query)
        flag = self.cursor.fetchall()[0][1]
        return flag

    def detect_change(self):
        query = "CHECKSUM TABLE items"
        self.cursor.execute(query)
        change_flag = self.cursor.fetchall()[0][1]
        
        self.prev_val = self.cur_val
        self.cur_val = change_flag
        
        return change_flag


    def count_pending(self):
        query1 = "SELECT count(*) FROM orders"
        self.cursor.execute(query1)
        total_orders = self.cursor.fetchall()[0][0]
        

        query2 = "SELECT count(if(pending = 1, pending, null)) FROM orders"
        self.cursor.execute(query2)
        pending_orders = self.cursor.fetchall()[0][0]
        
        return total_orders, pending_orders

    def count_items(self):
        query1 = "SELECT sum(red) FROM orders"
        self.cursor.execute(query1)
        red = self.cursor.fetchall()[0][0]

        query1 = "SELECT sum(green) FROM orders"
        self.cursor.execute(query1)
        green = self.cursor.fetchall()[0][0]
        
        query1 = "SELECT sum(blue) FROM orders"
        self.cursor.execute(query1)
        blue = self.cursor.fetchall()[0][0]

        if (red == None) or (green == None) or (blue == None):
            return None, None

        total_items = red + green + blue


        query2 = "SELECT sum(red) FROM items WHERE sub_id=0"
        self.cursor.execute(query2)
        red2 = self.cursor.fetchall()[0][0]

        query2 = "SELECT sum(green) FROM items WHERE sub_id = 0"
        self.cursor.execute(query2)
        green2 = self.cursor.fetchall()[0][0]

        query2 = "SELECT sum(blue) FROM items WHERE sub_id = 0"
        self.cursor.execute(query2)
        blue2 = self.cursor.fetchall()[0][0]


        query2 = "SELECT sum(red) FROM orders WHERE id NOT in (SELECT id FROM items)"
        self.cursor.execute(query2)
        red3 = self.cursor.fetchall()[0][0]

        query2 = "SELECT sum(green) FROM orders WHERE id NOT in (SELECT id FROM items)"
        self.cursor.execute(query2)
        green3 = self.cursor.fetchall()[0][0]

        query2 = "SELECT sum(blue) FROM orders WHERE id NOT in (SELECT id FROM items)"
        self.cursor.execute(query2)
        blue3 = self.cursor.fetchall()[0][0]


        query2 = "SELECT sum(red) FROM items WHERE sub_id!=0"
        self.cursor.execute(query2)
        red = self.cursor.fetchall()[0][0]

        query2 = "SELECT sum(green) FROM items WHERE sub_id!=0"
        self.cursor.execute(query2)
        green = self.cursor.fetchall()[0][0]

        query2 = "SELECT sum(blue) FROM items WHERE sub_id!=0"
        self.cursor.execute(query2)
        blue = self.cursor.fetchall()[0][0]
    
        if (red3 == None) or (green3 == None) or (blue3 == None):
            red3, green3, blue3 = 0, 0, 0


        if (red2 == None) or (green2 == None) or (blue2 == None):
            red2, green2, blue2 = 0, 0, 0

        if (red == None) or (green == None) or (blue == None):
            return None, None

        complete_items = red + green + blue
        # complete_items = (red2 + green2 + blue2) - (red + green + blue)
        pending_items = (red2+ green2 + blue2) + (red3+ green3 + blue3)#- complete_items

        return pending_items, complete_items


def main():
    socket = Socket()
    socket.sio.connect('http://172.26.226.35:60000')
    # socket.sio.connect('http://172.26.229.141:60000')
    db_manager = DB_Reader(0)
    flag = 0

    flag = db_manager.init_flag()
    del db_manager

    while True:
        db_manager = DB_Reader(flag)
        total_orders, pending_orders = db_manager.count_pending()
        pending_items, complete_items = db_manager.count_items()
        # print(total_orders, pending_orders)

        if (pending_items == None) or (complete_items == None) or (total_orders == None) or (pending_orders == None):
            time.sleep(2)
            continue


        change_flag = db_manager.detect_change()
        if flag != change_flag:
            flag = change_flag 
            msg = {'pending_order':pending_orders, 'complete_order':total_orders - pending_orders, 'pending_item':int(pending_items), 'complete_item':int(complete_items)}
            print(msg)
            socket.sio.emit('deliv_prog', msg)
            
        del db_manager
        time.sleep(2)

        

if __name__ == "__main__":
    main()
