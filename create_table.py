import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user = "root",
    passwd = "newroot",
    database = "orderdb"
)

#create cursor

cursor = db.cursor()

cursor.execute("DROP TABLE IF EXISTS items")

#create new table
sql = '''CREATE TABLE items(
      id int(11) UNSIGNED AUTO_INCREMENT PRIMARY KEY,
      red int(11),
      blue int(11),
      green int(11),
      pending tinyint(1),
      orderdate timestamp default current_timestamp,
      filldate timestamp NOT NULL DEFAULT "0000-00-00 00:00:00",
      address int(3))'''

cursor.execute(sql)

cursor.close()
