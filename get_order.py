import mysql.connector as mysql
import pdb
db = mysql.connect(
    host = "localhost",
    user = "root",
    passwd = "",
    database = "orderdb"
)

cursor = db.cursor()

cursor.execute("SHOW TABLES")
tables = cursor.fetchall()

query = "SELECT * FROM ORDERS WHERE pending=1 ORDER BY address, orderdate asc"

cursor.execute(query)
# db.commit()
a = cursor.fetchall()
pdb.set_trace()
# cursor.execute("SELECT * FROM ORDERS")
print(a[0])
