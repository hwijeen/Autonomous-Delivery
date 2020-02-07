"""
Models the arrival of orders as poisson process.
The interval between orders is modeled as exponentional distribution.
"""
import sys
import time
import random
import logging

import numpy as np
import mysql.connector as mysql

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

def generate_arrival_times(num_orders, lambda_):
    intervals = []
    arrival_times = []
    arrival_time = 0
    for i in range(num_orders):
        beta = 1 / lambda_ # required by numpy.random.exponentional
        interval = np.random.exponential(beta)
        arrival_time += interval
        intervals.append(interval * 60 * 60) # in seconds
        arrival_times.append(arrival_time * 60) # in minutes
    return intervals, arrival_times

def generate_num_items(num_orders, n, p):
    reds, greens, blues = [], [], []
    for _ in range(num_orders):
        reds.append(np.random.binomial(n, p))
        greens.append(np.random.binomial(n, p))
        blues.append(np.random.binomial(n, p))
    return reds, greens, blues

def generate_addresses(num_orders):
    addresses = [101, 102, 103, 201, 202, 203]
    addrs = []
    for _ in range(num_orders):
        addrs.append(int(np.random.choice(addresses)))
    return addrs

def get_db():
    try:
        host_ip = sys.argv[1]
    except:
        host_ip = '172.26.220.250'
    db = mysql.connect(host=host_ip,
                       user="user",
                       passwd="hotmetal",
                       database="orderdb")
    cursor= db.cursor()
    return db, cursor

def delete_all_in_table(db, cursor):
    query_1 = 'DELETE FROM orders'
    query_2 = 'DELETE FROM items'
    cursor.execute(query_1)
    cursor.execute(query_2)
    db.commit()

def write_to_db(db, cursor, intervals, reds, greens, blues, addrs):
    for intv, r, g, b, addr in zip(intervals, reds, greens, blues, addrs):
        print(f'Time interval for this order: {intv:.2f} seconds')
        time.sleep(intv)
        query = "INSERT INTO orders (customer, red, green, blue, pending, address) " \
                "VALUES (%s, %s, %s, %s, %s, %s)"
        cust = 'a' # not important
        pend = 1
        values = (cust, int(r), int(g), int(b), pend, addr)
        cursor.execute(query, values)
        db.commit()
        logger.info(f'Addr: {addr}, Red: {r}, Green: {g}, Blue: {b}\n')
        print(f'Addr: {addr}, Red: {r}, Green: {g}, Blue: {b}\n')

def write_to_file(outfname, addrs, reds, greens, blues):
    f = open(outfname, 'w')
    for addr, r, g, b in zip(addrs, reds, greens, blues):
        print(f'{addr}\t{r}\t{g}\t{b}', file=f)
    print('-'*80, file=f)
    print(f'Num orders: {len(addrs)}', file=f)
    print(f'Sum of items: Red({sum(reds)}), Greens({sum(greens)}), Blues({sum(blues)})', file=f)


if __name__ == "__main__":

    NUM_ORDERS = 10
    NUM_ORDERS_PER_HOUR = 300

    db, cursor = get_db()

    delete_all_in_table(db, cursor)
    intervals, _ = generate_arrival_times(NUM_ORDERS, lambda_=NUM_ORDERS_PER_HOUR)
    reds, greens, blues = generate_num_items(NUM_ORDERS, n=5, p=0.5)
    addrs = generate_addresses(NUM_ORDERS)
    write_to_db(db, cursor, intervals, reds, greens, blues, addrs)
    write_to_file('generated_orders.txt', addrs, reds, greens, blues)

