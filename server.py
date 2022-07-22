# -----------------------------------------------------------
# Main server-side code for the FASTAPI VIN Decoder
#
# Curtis Ogren
# email: ceogren@alumni.stanford.edu
# github: c-ogren
# -----------------------------------------------------------

from re import A
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

    # Check if the cached db returns any hits
    if(len(cached) == 0):
        r = requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vehicle.vin}?format=json')
        decodedVin = r.json()

        # Raise Error if not a valid VIN
        # VPIC returns a non-zero ErrorCode when a non-valid vin is inserted
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
                raise HTTPException(status_code=400, detail=insert_error) 
    else:
        # Return the cached Vehicle
        v_return = {
            "vin": cached[0][1], # primary key id is 1
            "make": cached[0][2],
            "model": cached[0][3],
            "year": cached[0][4],
            "class": cached[0][5],
            "cached": True
        }
    db.checkAll()
    return v_return

@app.post('/remove')
async def remove(vehicle: Vehicle):
    # VIN in body once again needs to be exactly 17 chars
    if(len(vehicle.vin) != 17):
        raise HTTPException(status_code=400, detail='VIN should have exactly 17 alphanumeric characters')

    r_cache = db.removeCache(vehicle.vin)
    
    if(r_cache == 1):
        return {
            "vin" : vehicle.vin,
            "deleteSuccess" : True
        }
    else:
        return {
            "vin" : vehicle.vin,
            "deleteSuccess" : False,
            "details" : r_cache
        }


@app.get('/export')
async def export():
    e_cache = db.exportCache()
    print(e_cache.args)
    if(e_cache):
        raise HTTPException(status_code=500, detail=e_cache.args[1])
    return FileResponse('data_files/db_cache.parquet')