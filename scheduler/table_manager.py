import mysql.connector
import pdb
def copy_table():
    connection = mysql.connector.connect(
        host = "localhost",
        user = "user",
        passwd = "hotmetal",
        database = "orderdb"
    )
    cursor = connection.cursor()
    
    cursor.execute("SET SESSION sql_mode = ''")
    copy_table = """INSERT INTO items(id, red, blue, green, filldate, address)
            SELECT id, red, blue, green, filldate, address
            FROM orders WHERE id NOT IN (SELECT id FROM items) AND pending=1"""
    cursor.execute(copy_table)
    # cursor.execute(insert_col)
    connection.commit()
    cursor.close()

def create_table():
    db = mysql.connector.connect(
        host = "localhost",
        user = "user",
        passwd = "hotmetal",
        database = "orderdb"
    )

    #create cursor
    cursor = db.cursor()
    
    cursor.execute("DROP TABLE IF EXISTS items")
    cursor.execute("SET SESSION sql_mode = ''")

    #create new table
    sql = '''CREATE TABLE items(
        id int(11) UNSIGNED AUTO_INCREMENT,
        sub_id int(11),
        red int(11),
        blue int(11),
        green int(11),
        filldate timestamp NOT NULL DEFAULT "0000-00-00 00:00:00",
        address int(3),
        PRIMARY KEY (id, sub_id)        
        )'''

    cursor.execute(sql)
    cursor.close()
    db.commit()