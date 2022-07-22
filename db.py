import sqlite3
from sqlite3 import Cursor, Error

def createConnection(db):
    connection = None
    try:
        connection = sqlite3.connect(db)
    except Error as e:
        print(e)
    
    return connection

def createTable(c):
    curs = c.cursor()
    curs.execute("CREATE TABLE IF NOT EXISTS Vehicles (Vin TEXT, Make TEXT, Model TEXT, Year TEXT, Class TEXT)")
    resp = curs.fetchall()

def checkCache(c, vin):
    curs = c.cursor()
    curs.execute("SELECT * FROM Vehicles where Vin=?", (vin,))
    resp = curs.fetchall()
    return(resp)

def insertCache(c, v_tuple):
    curs = c.cursor()
    curs.execute("INSERT INTO Vehicles (Vin, Make, Model, Year, Class) VALUES (?,?,?,?,?)", v_tuple)
    resp = curs.fetchall()

def checkAll(c):
    curs = c.cursor()
    curs.execute("SELECT * FROM Vehicles")
    resp = curs.fetchall()
    print('checking all...', resp)
