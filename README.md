# :rocket: FVD
FastVinDecoder (ref: [Backend Challenge](https://github.com/KoffieLabs/backend-challenge))

Author: Curtis Ogren

# :green_circle: Get Started
Make sure to install virtual environment dependencies:
```
pip install -r requirements.txt
```

# :gear: Running the server
In order to run the FastAPI server in development mode, run:
```
uvicorn main:app --reload
```
This will by default run the applciation on port 8000

TODO: PRODUCTION?

# :file_folder: File Structure
## /tests
For testing the parquet binary file by converting it to a CSV, run:
```
py tests/readparquet.py
```

I used Postman for testing the API endpoints. You can import ```FVD_Testing.postmancollection.json```
into your Postman application to see how I generated random Vins for testing the caching procedures.

## /data_files
Produced upon a GET request of ```/export```. Stores the parquet data as ```db_cache.parquet```.
and ```vehicle_cache.csv``` if the parquet is checked.

## db.py
All database transactional logic, defined in a DBInstance class.

## server.py
All server-side routes and logic, importing the DBInstance class in db.py.

## fvd.db
The Sqlite database cache produced upon running the server and triggering multiple transactions.
The data is committed after every transaction so the database is retained upon SIGINT of the server.

# :page_facing_up: Docs
Once the application is running, you can visit:
[FVD API Docs (127.0.0.1:8000/docs)](http://127.0.0.1:8000/docs)
Fast API's built in documentation of the routes defined in server.py