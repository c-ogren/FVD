# -----------------------------------------------------------
# Main server-side code for the FASTAPI VIN Decoder
#
# Curtis Ogren
# email: ceogren@alumni.stanford.edu
# github: c-ogren
# -----------------------------------------------------------

from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
import requests
from db import DBInstance

app = FastAPI()

# Object for body data
class Vehicle(BaseModel):
    vin: str

# Db connection declaration
db = DBInstance('fvd.db')
db.createConnection()
db.createTable()


@app.post('/lookup')
async def lookup(vehicle: Vehicle):
    # VIN needs to have EXACTLY 17 alphanumeric chars
    if(len(vehicle.vin) != 17):
        raise HTTPException(status_code=400, detail='VIN should have exactly 17 alphanumeric characters')

    v_return = {}

    # Check sqlite3 db if the VIN exists
    cached = db.checkCache(vehicle.vin)
    # Check if database error returned from checkCache
    if not isinstance(cached, list):
        raise HTTPException(status_code=500, detail=' '.join(cached.args))
    # Check if the cached db returns any hits
    if(len(cached) == 0):
        r = requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vehicle.vin}?format=json')
        decodedVin = r.json()

        # Raise Error if not a valid VIN
        # VPIC returns a non-zero ErrorCode when a non-valid vin is inserted
        # Returns a 400 since this is a client error
        if(decodedVin['Results'][0]['ErrorCode'] != '0'):
            raise HTTPException(status_code=400, detail=decodedVin['Results'][0]['ErrorText'])
        else:
            v_return = {
                "vin": vehicle.vin,
                "make": decodedVin['Results'][0]['Make'],
                "model": decodedVin['Results'][0]['Model'],
                "year": decodedVin['Results'][0]['ModelYear'],
                "class": decodedVin['Results'][0]['BodyClass'],
                "cached": False
            }
            v_tuple = (
                vehicle.vin, 
                decodedVin['Results'][0]['Make'], 
                decodedVin['Results'][0]['Model'], 
                decodedVin['Results'][0]['ModelYear'],
                decodedVin['Results'][0]['BodyClass']
            )
            insert_error = db.insertCache(v_tuple)
            if(insert_error):
                # Return 500 since this is a serverside error, not a client error.
                raise HTTPException(status_code=500, detail=' '.join(insert_error.args)) 
    else:
        # Return the cached Vehicle
        v_return = {
            "vin": cached[0][1], # primary key id is cached[0][0]
            "make": cached[0][2],
            "model": cached[0][3],
            "year": cached[0][4],
            "class": cached[0][5],
            "cached": True
        }

    # db.checkAll() # Check database rows
    return v_return


@app.post('/remove')
async def remove(vehicle: Vehicle):
    # VIN in body once again needs to be exactly 17 chars
    if(len(vehicle.vin) != 17):
        raise HTTPException(status_code=400, detail='VIN should have exactly 17 alphanumeric characters')

    r_cache = db.removeCache(vehicle.vin)
    
    # r_cache is the number of rows affected after the removeCache function.
    # if there was an error, r_cache is an error. Append details to the response for more information
    if(r_cache == 1):
        return {
            "vin" : vehicle.vin,
            "deleteSuccess" : True
        }
    else:
        if not isinstance(r_cache, int):
            return {
                "vin" : vehicle.vin,
                "deleteSuccess" : False,
                "details" : ' '.join(r_cache.args) # r_cache is an error, so we need to join the array of strings
            }
        else:
            return {
                "vin" : vehicle.vin,
                "deleteSuccess" : False,
                "details" : 'VIN not found'
            }


@app.get('/export')
async def export():
    # Return the file to the client.
    # If you visit http://localhost:{port}/export in any browser, you can download the parquet.
    e_cache = db.exportCache()
    if(e_cache):
        # Return 500 since this is a serverside error, not a client error.
        raise HTTPException(status_code=500, detail=' '.join(e_cache.args))
    return FileResponse('data_files/db_cache.parquet')