# main.py
import os
import httpx
import mysql.connector
import asyncio
from fastapi import FastAPI, HTTPException
from contextlib import contextmanager, asynccontextmanager
from dotenv import load_dotenv

load_dotenv()

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
        # 2. "Yield" the connection to the code that asked for it
        yield conn
    except mysql.connector.Error as err:
        # 3. If an error happens, raise it as an HTTP error
        print(f"Database connection error: {err}")
        raise HTTPException(status_code=503, detail=f"Database connection error: {err}")
    finally:
        # 4. Closing the connection regardless of whether it worked or failed
        if conn and conn.is_connected():
            conn.close()


def _run_startup_logic():
    """
    A synchronous function containing the startup logic for setting up the joke's database.
    """
    print("Running application startup logic...")
    try:
        # This is our original, synchronous code
        with get_db_connection() as conn:
            with conn.cursor() as cursor:
                cursor.execute("""
                CREATE TABLE IF NOT EXISTS jokes (
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    setup VARCHAR(512),
                    punchline VARCHAR(512)
                )
                """)
            conn.commit()
            print("Database table 'jokes' is ready.")
    except HTTPException:
        print("FATAL: Could not connect to database on startup.")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manages the application startup and shutdown lifecycle.
    """
    await asyncio.to_thread(_run_startup_logic)
    # Waiting to receive requests
    yield
    print("Running application shutdown logic...")


app = FastAPI(lifespan=lifespan)


@app.get("/health")
def health_check():
    """
    Health check endpoint. Ensures the app is running and can connect to the database.
    """
    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT 1")
            cursor.fetchone()
            return {"status": "ok", "database_connection": "successful"}

@app.get("/jokes")
def get_jokes():
    """
    Retrieves all jokes stored in the Jokes database.
    """
    with get_db_connection() as conn:
        with conn.cursor(dictionary=True) as cursor:
            cursor.execute("SELECT id, setup, punchline FROM jokes")
            jokes = cursor.fetchall()
            return jokes


def _fetch_and_store_joke(conn):
    """
    Fetches a random joke from an external API and stores it in the database.
    """
    # Part 1: Fetch from Jokes API
    try:
        with httpx.Client() as client:
            response = client.get(JOKE_API_URL)
            response.raise_for_status() # Raise error for bad responses
            joke_data = response.json()
    except httpx.RequestError as err:
        raise HTTPException(status_code=502, detail=f"External API request failed: {err}")

    # Part 2: Stores the joke in the database
    setup = joke_data.get("setup")
    punchline = joke_data.get("punchline")

    with get_db_connection() as conn:
        with conn.cursor() as cursor:
            sql = "INSERT INTO jokes (setup, punchline) VALUES (%s, %s)"
            val = (setup, punchline)
            cursor.execute(sql, val)
            conn.commit()
            new_joke_id = cursor.lastrowid
            return {
                "message": "Joke stored successfully!",
                "id": new_joke_id,
                "setup": setup,
                "punchline": punchline
            }


@app.post("/jokes", status_code=201)
def create_joke():
    """
    Fetches and stores a single random joke.
    """
    with get_db_connection() as conn:
        new_joke = _fetch_and_store_joke(conn)

        # Now we commit the transaction
        conn.commit()

        return {
            "message": "Joke stored successfully!",
            "joke": new_joke
        }


@app.post("/jokes/collect", status_code=201)
def collect_jokes(count: int = 10):
    """
    Collects a specified number of jokes.
    """
    if count < 1:
        raise HTTPException(status_code=400, detail="Count must be 1 or greater.")

    print(f"Collecting {count} jokes...")

    new_jokes = []
    with get_db_connection() as conn:
        try:
            for _ in range(count):
                new_joke = _fetch_and_store_joke(conn)
                new_jokes.append(new_joke)
            conn.commit()

        except HTTPException as e:
            conn.rollback()
            raise e

    return {
        "message": f"Successfully stored {count} jokes.",
        "jokes_added": new_jokes
    }


@app.get("/")
def read_root():
    return {"message": "Hello, World! My Jokes API is running."}
