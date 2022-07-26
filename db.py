# -----------------------------------------------------------
# Database logic code for the FASTAPI VIN Decoder
# Note: All DB transactions are wrapped in a try/catch block 
# to catch any sqlite errors.
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
        """Take the filename of the db, initialize connection variables"""
        super().__init__()
        self.connection = None
        self.db_name = db

    def createConnection(self):
        """Open a file for db writing, create a connection property within the DBInstance class"""
        try:
            self.connection = sqlite3.connect(self.db_name)
            return None
        except Error as e:
            print("Could not create a Sqlite connection", e)
            return e
    
    def createTable(self):
        """
        Create the Vehicles table witin the FVD db if there is none.

        First row is id (primary key). ID's are a nice-to-have in database design.
        Vin's are the second data column. They are a unique to prevent any duplicate insertions from any developer.
        Any duplicate insertions of a VIN will return a unique violation error.
        The rest pertain to the decoded VIN.
        """
        try:   
            curs = self.connection.cursor()
            curs.execute("CREATE TABLE IF NOT EXISTS Vehicles (id integer primary key, Vin varchar unique, Make varchar, Model varchar, Year varchar, Class varchar)")
            self.connection.commit()
            return None
        except Error as e:
            print("Could not create Vehicle table", e)
            return e
    
    def checkCache(self, vin):
        """
        Checks the cached Sqlite database of vehicles and returns the unique vehicle details that match the given VIN

        Parameters:
            vin (int): Vehicle identification number
        Returns:
            [()] array of length one, containing a tuple of vehicle details
        """
        try:    
            curs = self.connection.cursor()
            curs.execute("SELECT * FROM Vehicles WHERE Vin=?", (vin,))
            return curs.fetchall()
        except Error as e:
            return e

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
        Returns the row count, because if the requested vin was not deleted, the delete was unsuccessful for the requested VIN.

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
        """
        Writes the existing cache as parquet format to /data_files/db_cache.parquet.
        Upon fetching from the cache, convert the array of tuples to numpy arrays. The numpy array will then
        need to be converted to a parquet table. Lastly, write the parquet table to a file.

        Returns:
            None. If there was any error related to the Sqlite transaction or the parquet conversion, return the error
        """
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