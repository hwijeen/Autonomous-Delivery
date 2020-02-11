import mysql.connector as mysql
import time

from order_generator import write_to_db, delete_all_in_table


def get_db(host_ip):
    db = mysql.connect(host=host_ip,
                       user="user",
                       passwd="hotmetal",
                       database="orderdb")
    cursor= db.cursor()
    return db, cursor

def unpack_orders(all_orders):
    intervals = []
    arrival_times = []
    reds, greens, blues = [], [], []
    addrs = []

    start_time = all_orders[0][6]
    for order in all_orders:
        id_, name, r, g, b, pending, orderdate, filldate, addr = order
        intv = orderdate - start_time # time delta

        intervals.append(intv)
        arrival_times.append(orderdate)
        reds.append(r)
        greens.append(g)
        blues.append(b)
        addrs.append(addr)

    return intervals, arrival_times, reds, greens, blues, addrs


if __name__ == '__main__':
    host_ip = '172.26.220.250'

    db ,cursor = get_db(host_ip)
    query = 'select * from 200210_table'
    cursor.execute(query)
    all_orders = cursor.fetchall()

    yn = input("Press y to delete everything from orders and items table")
    if yn == 'y':
        delete_all_in_table(db, cursor)

    intervals, arrival_times, reds, greens, blues, addrs = unpack_orders(all_orders)

    write_to_db(db, cursor, intervals, arrival_times, reds, greens, blues,
                addrs, real_time=True)

