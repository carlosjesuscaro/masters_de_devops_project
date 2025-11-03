# main.py
import os
import mysql.connector
from fastapi import FastAPI, HTTPException
from contextlib import contextmanager
from dotenv import load_dotenv

load_dotenv()
app = FastAPI()

# Loading the environment variables
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")
JOKE_API_URL = os.getenv("JOKE_API_URL")

# Database connection manager
@contextmanager
def get_db_connection():
    """
    Provides a database connection using a context manager.
    """
    conn = None
    try:
        # 1. Open the connection
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        # 2. "Yield" (give) the connection to the code that asked for it
        yield conn
    except mysql.connector.Error as err:
        # 3. If an error happens, raise it as an HTTP error
        print(f"Database connection error: {err}")
        raise HTTPException(status_code=503, detail=f"Database connection error: {err}")
    finally:
        # 4. This *always* runs, whether it worked or failed
        if conn and conn.is_connected():
            conn.close()

@app.get("/")
def read_root():
    return {"message": "Hello, World! My Jokes API is running."}