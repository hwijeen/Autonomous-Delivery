import mysql.connector

connection = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "newroot",
    database = "orderdb"
)

#create cursor
cursor = connection.cursor()

#create new table
copy = """INSERT INTO items (id, red, blue, green, pending, orderdate, filldate, address)
       SELECT id, red, blue, green, pending, orderdate, filldate, address FROM orders"""

copy = """INSERT INTO items(id, red, blue, green, pending, orderdate, filldate, address)
        SELECT id, red, blue, green, pending, orderdate, filldate, address
        FROM orders WHERE id NOT IN (SELECT id FROM items)"""

cursor.execute(copy)
connection.commit()

cursor.close()
