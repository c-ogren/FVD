# -----------------------------------------------------------
# Database logic code for the FASTAPI VIN Decoder
#
# Curtis Ogren
# email: ceogren@alumni.stanford.edu
# github: c-ogren
# -----------------------------------------------------------

import sqlite3
from sqlite3 import Error
import numpy as np
import os
import pyarrow as pa
import pyarrow.parquet as pq

class DBInstance:
    def __init__(self, db="fvd.db") -> None:
        super().__init__()
        self.connection = None
        self.db_name = db

    def createConnection(self):
        try:
            self.connection = sqlite3.connect(self.db_name)
            return None
        except Error as e:
            print("Could not create a Sqlite connection")
            return e
    
    def createTable(self):
        try:   
            curs = self.connection.cursor()
            curs.execute("CREATE TABLE IF NOT EXISTS Vehicles (id integer primary key, Vin varchar unique, Make varchar, Model varchar, Year varchar, Class varchar)")
            return None
        except Error as e:
            return e
    
    def checkCache(self, vin):
        """
        Checks the cached Sqlite database of vehicles and returns the unique vehicle details that match the given VIN

        Parameters:
            vin (int): Vehicle identification number
        Returns:
            [()] array of length one, containing a tuple of vehicle details
        """
        curs = self.connection.cursor()
        curs.execute("SELECT * FROM Vehicles WHERE Vin=?", (vin,))
        return curs.fetchall()

    def insertCache(self, v_tuple):
        """
        Puts vehicle details in the cached Sqlite database, pertaining to the uniqueness of the VIN.
        The vehicle information is added if and only if the db does not already contain the vehicle's VIN.

        Parameters: 
            v_tuple (tuple): Vehicle information (VIN, Make, Model, Year, Class)
        Returns:
            None. If the db transaction failed, the error is returned.
        """
        try:
            curs = self.connection.cursor()
            curs.execute("INSERT INTO Vehicles (Vin, Make, Model, Year, Class) VALUES (?,?,?,?,?)", v_tuple)
            self.connection.commit()
            return None
        except Error as e:
            return e

    def removeCache(self, vin):
        """
        Removes vehicle entry in the cached Sqlite database
        The vehicle information is deleted if and only if the db contains the vehicle's VIN.

        Parameters: 
            vin (int): Vehicle identification number
        Returns:
            rowcount (int) number of rows affected
            If the db transaction failed, the error is returned
        """
        try:
            curs = self.connection.cursor()
            curs.execute("DELETE FROM Vehicles WHERE Vin=?", (vin,))
            self.connection.commit()
            return curs.rowcount
        except Error as e:
            return e
    
    def exportCache(self):
        try:
            curs = self.connection.cursor()
            curs.execute("SELECT * FROM Vehicles")
            arr_tuples = curs.fetchall()
            for t in arr_tuples:
                t = np.asarray(t)
            ndarray = np.array(arr_tuples)
            p_table = pa.table(
                {
                    "id": ndarray[:,0],
                    "VIN": ndarray[:,1],
                    "Make": ndarray[:,2],
                    "Model": ndarray[:,3],
                    "Year": ndarray[:,4],
                    "Class": ndarray[:,5]
                }
            )
            path = os.getcwd()
            if not os.path.exists(path+'/data_files'):
                os.makedirs(path+'/data_files')
            pq.write_table(p_table, "data_files/db_cache.parquet")
            return None
        except Exception as e:
            print(e)
            return e
    
    def checkAll(self):
        """
        For debugging purposes. Prints out all of the data from the Vehicle table

        Returns array of tuples, ie:
            [(Vin1, Make1, Model1, Year1, Class1), (Vin2, Make2, Model2, Year2, Class2), ...]
        """

        curs = self.connection.cursor()
        curs.execute("SELECT * FROM Vehicles")
        resp = curs.fetchall()
        print('checking all...', resp)