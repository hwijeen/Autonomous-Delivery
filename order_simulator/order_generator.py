"""
Models the arrival of orders as poisson process.
The interval between orders is modeled as exponentional distribution.
Writes order directly to DB.
"""
import sys
import time
import random
import logging
import argparse
from datetime import datetime, timedelta

import numpy as np
import mysql.connector as mysql


logger = logging.getLogger(__name__)
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                datefmt = '%m/%d/%Y %H:%M:%S', level=logging.INFO)


def generate_arrival_times(now, num_orders, lambda_):
    """ Interval follows exponentional distribution """
    intervals = [] # list of timedeltas
    arrival_times = [] # list of datetimes
    for i in range(num_orders):
        beta = 1 / lambda_ # required by numpy.random.exponentional
        interval = timedelta(hours=np.random.exponential(beta))
        now += interval
        intervals.append(interval)
        arrival_times.append(now)
    return intervals, arrival_times

def generate_num_items(num_orders, n, p):
    """ Number of items follows a binomial distribution """
    reds, greens, blues = [], [], []
    for _ in range(num_orders):
        reds.append(np.random.binomial(n, p))
        greens.append(np.random.binomial(n, p))
        blues.append(np.random.binomial(n, p))
    return reds, greens, blues

def generate_addresses(num_orders):
    """ Uniformly choose adresses """
    addresses = [101, 102, 103, 201, 202, 203]
    addrs = []
    for _ in range(num_orders):
        addrs.append(int(np.random.choice(addresses)))
    return addrs

def get_db(host_ip):
    db = mysql.connect(host=host_ip,
                       user="user",
                       passwd="hotmetal",
                       database="orderdb")
    cursor= db.cursor()
    return db, cursor

def delete_all_in_table(db, cursor):
    logger.info("Delteting everthing in db")
    query_1 = 'DELETE FROM orders'
    query_2 = 'DELETE FROM items'
    cursor.execute(query_1)
    cursor.execute(query_2)
    db.commit()

def write_to_db(db, cursor, intervals, arrival_times, reds, greens, blues,\
                addrs, real_time):
    logger.info("Writing to db starting!")
    for intv, arrv, r, g, b, addr in zip(intervals, arrival_times, reds,\
                                         greens, blues, addrs):
        if real_time:
            time.sleep(intv.total_seconds())

        query = "INSERT INTO orders\
                (customer, red, green, blue, pending, orderdate, address)\
                VALUES (%s, %s, %s, %s, %s, %s, %s)"
        cust = 'a' # not important
        pend = 1
        orderd = arrv.strftime('%Y-%m-%d %H:%M:%S')
        values = (cust, int(r), int(g), int(b), pend, orderd, addr)
        cursor.execute(query, values)
        db.commit()
        logger.info(f'Addr: {addr}, Red: {r}, Green: {g}, Blue: {b}, Order date: {orderd}')


if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument('--host_ip', default='172.26.220.250')
    parser.add_argument('--real_time', action='store_true')
    parser.add_argument('--keep_db', action='store_true')
    parser.add_argument('--num_orders', type=int, default=50)
    parser.add_argument('--num_orders_per_hour', type=int, default=300)
    args = parser.parse_args()

    now = datetime(2020, 1, 1)

    db, cursor = get_db(args.host_ip)

    if not args.keep_db:
        yn = input("Press y to delete tables in DB")
        if yn == 'y':
            delete_all_in_table(db, cursor)

    intervals, arrival_times = generate_arrival_times(now, args.num_orders,\
                                                      args.num_orders_per_hour)
    reds, greens, blues = generate_num_items(args.num_orders, n=5, p=0.5)
    addrs = generate_addresses(args.num_orders)
    write_to_db(db, cursor, intervals, arrival_times, reds, greens, blues,\
                addrs, args.real_time)

