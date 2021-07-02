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
    print(query, placeholders)
    cursor.execute(query, placeholders)
    return cursor.fetchall()

db = getConnection("feelathomesg.db")
query = """
DELETE FROM listings;
"""

print(executeWriteQuery(db, query))

# LISTINGS
# listing_id | seller | description | availability | rating | cuisine | veg | phone_num | latitude | longitude | location

# store latitude and longitude in a tuple