import sqlite3

# connect database with sqlite3
def getConnection(db):
    connection = sqlite3.connect(db, check_same_thread=False)
    return connection


# execute a write query into database
def executeWriteQuery(connection, query, placeholders=()):
    cursor = connection.cursor()
    print(query, placeholders)
    cursor.execute(query, placeholders)
    connection.commit()
    return True


# execute a read query from database
def executeReadQuery(connection, query, placeholders=()):
    cursor = connection.cursor()
    #print(query, placeholders)
    cursor.execute(query, placeholders)
    return cursor.fetchall()

db = getConnection("foodsellers.db")
query = """
SELECT * FROM sellers;
"""

x = executeReadQuery(db, query)
print(x)

# seller_id | name | description | availability | rating | location | cuisine | veg | email | phone_num
# DO NOT CHANGE ANYTHING IN foodsellers.db PLEASE