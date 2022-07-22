from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import requests
from db import checkCache, createConnection, createTable, checkAll, insertCache

app = FastAPI()

class Vehicle(BaseModel):
    vin: str

# db connection to be used in methods
db_c = createConnection('fvd.db')
createTable(db_c)


@app.get("/")
def root():
    return {"hello": "world"}

@app.post('/lookup')
async def lookup(vehicle: Vehicle):
    v_return = {}
    print(vehicle, vehicle.vin)

    #check sqlite database
    cached = checkCache(db_c, vehicle.vin)

    if(len(cached) == 0):
        r = requests.get(f'https://vpic.nhtsa.dot.gov/api/vehicles/decodevinvalues/{vehicle.vin}?format=json')
        decodedVin = r.json()

        if(decodedVin['Results'][0]['ErrorCode'] != '0'):
            raise HTTPException(status_code=400, detail=decodedVin['Results'][0]['ErrorText'])
        else:
            v_return = {
                "vin": vehicle.vin,
                "make": decodedVin['Results'][0]['Make'],
                "model": decodedVin['Results'][0]['Model'],
                "year": decodedVin['Results'][0]['ModelYear'],
                "class": decodedVin['Results'][0]['BodyClass'],
                "result": False
            }
            v_tuple = (
                vehicle.vin, 
                decodedVin['Results'][0]['Make'], 
                decodedVin['Results'][0]['Model'], 
                decodedVin['Results'][0]['ModelYear'],
                decodedVin['Results'][0]['BodyClass']
            )
            insertCache(db_c, v_tuple)
    else:
        v_return = {
            "vin": cached[0][0],
            "make": cached[0][1],
            "model": cached[0][2],
            "year": cached[0][3],
            "class": cached[0][4],
            "result": True
        }
    checkAll(db_c)
    
    return v_return

# @app.get('/remove')


# @app.get('/export')