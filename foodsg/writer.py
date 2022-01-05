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

db = getConnection("/home/lazyboy4943/mysite/feelathomesg.db")
query = """
CREATE TABLE IF NOT EXISTS listings (
    listing_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    seller varchar(300) NOT NULL,
    prodname varchar(100) NOT NULL,
    description varchar(300) NOT NULL,
    category varchar(100) NOT NULL,
    usage varchar(3) NOT NULL,
    phone_num varchar(150),
    latitude DECIMAL(20, 17),
    longitude DECIMAL(20, 17),
    location varchar(300),
    email varchar(255),
    availability BOOL NOT NULL
);
"""

print(executeWriteQuery(db, query))

query = """CREATE TABLE IF NOT EXISTS mentors (
    mentor_id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
    mentor varchar(300) NOT NULL,
    description varchar(300) NOT NULL,
    area varchar(100) NOT NULL,
    phone_num varchar(150),
    latitude DECIMAL(20, 17),
    longitude DECIMAL(20, 17),
    location varchar(300),
    email varchar(255)
);
"""

print(executeWriteQuery(db, query))

# LISTINGS
# listing_id | seller | description | availability | rating | cuisine | veg | phone_num | latitude | longitude | location | email

# MENTORS
# mentor_id | mentor | description | area | phone_num | latitude | longitude | location | email
