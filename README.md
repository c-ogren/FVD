# :rocket: FVD
FastVinDecoder API

Author: Curtis Ogren

# :green_circle: Get Started
Make sure to install virtual environment dependencies:
```
git clone https://github.com/c-ogren/FVD.git
cd FVD
py -m venv .venv
.\.venv\Scripts\activate
pip install -r requirements.txt
```

# :gear: Running the server
In order to run the FastAPI server in development mode, run:
```
uvicorn server:app --reload
```
This will by default run the applciation on port 8000

### Production
If you want to run the application in production, it is suggested have nginx proxy the FVD server.
This is because nginx is good at handling load. You will need to create a custom http block for the server
to forward the nginx port to the running FVD port. 

In addition, you will have to set up GUnicorn to run and manage running Uvicorn in a production setting.

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