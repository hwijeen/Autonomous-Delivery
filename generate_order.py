# import mysql.connector
import mysql.connector as mysql
from random import seed
from random import randint
import numpy as np
# from datetime import datetime
import time
# seed(1)
import pdb

db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "newroot",
    database = "orderdb"
)

print(db)

cursor = db.cursor()

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

# for table in tables:
#     print(table)
# cursor.execute("SELECT * FROM ORDERS")
# print(cursor.fetchall())

customers = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i']
addresses = [101, 102, 201, 301, 302, 303]
# frequency = np.random.poisson(3)
# key =3

# print (customers[randint(0, len(customers))], randint(0, 20), randint(0,10), randint(0,15), 1,
#           datetime.today().strftime("%Y-%m-%d %H:%M:%S"), addresses[randint(0, len(addresses))])
# insert new data
## defining the Query
i = 0
for i in range(0, 10):
    query = "INSERT INTO orders (customer, red, blue, green, pending, address) " \
            "VALUES (%s, %s, %s, %s, %s, %s)"


    values = (customers[randint(0, 8)], randint(0, 20), randint(0, 10), randint(0, 15), 1, addresses[randint(0, 5)])
    # random.normal
    cursor.execute(query, values)

    db.commit()
    # print(cursor.rowcount, "record inserted")
    print(i)
    i = i + 1
    time.sleep(np.random.poisson(3))

cursor.execute("SELECT * FROM ORDERS")
print(cursor.fetchall())


