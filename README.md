# :rocket: FVD
FastVinDecoder (ref: [Backend Challenge](https://github.com/KoffieLabs/backend-challenge))
Author: Curtis Ogren

# Get Started
Make sure to install virtual environment dependencies:
```pip install -r requirements.txt```

# Running the server
In order to run the FastAPI server in development mode, run:
```uvicorn main:app --reload```
This will by default run the applciation on port 8000

# Running in production

# :file_folder: File Structure
## /tests
For testing the parquet binary file by converting it to a CSV, run:
```py tests/readparquet.py```

I used Postman for testing the API endpoints. You can import ```FVD_Testing.postmancollection.json```
into your Postman application to see how I generated random Vins for testing the caching procedures.

## db.py
All database transactional logic, defined in a DBInstance class.

## server.py
All server-side code

# Docs
Once the application is running, you can visit:
[FVD API Docs (127.0.0.1:8000/docs)](http://127.0.0.1:8000/docs)
Fast API's built in documentation of the routes defined in server.py