import httpx
import os
import mysql.connector
from dotenv import load_dotenv

load_dotenv()

# Defining the environment variables
BASE_URL = "http://localhost:8000"
DB_HOST = os.getenv("DB_HOST")
DB_USER = os.getenv("DB_USER")
DB_PASS = os.getenv("DB_PASS")
DB_NAME = os.getenv("DB_NAME")

def setup_module(module):
    """
    Testing setup
    """
    try:
        conn = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASS,
            database=DB_NAME
        )
        with conn.cursor() as cursor:
            cursor.execute("DELETE FROM jokes")
        conn.commit()
        conn.close()
    except mysql.connector.Error as err:
        print(f"TEST SETUP FAILED: {err}")


def test_health_check():
    """
    Tests the /health endpoint.
    """
    with httpx.Client() as client:
        response = client.get(f"{BASE_URL}/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
        assert data["database_connection"] == "successful"


def test_create_and_get_jokes():
    """
    Tests the POST /jokes and GET /jokes endpoints.
    """
    with httpx.Client() as client:
        # 1. Check initial state (should be 0 jokes)
        response_get1 = client.get(f"{BASE_URL}/jokes")
        assert response_get1.status_code == 200
        assert len(response_get1.json()) == 0

        # 2. Create a new joke
        response_post = client.post(f"{BASE_URL}/jokes")
        assert response_post.status_code == 201
        post_data = response_post.json()

        # 3. Check final state (should be 1 joke)
        response_get2 = client.get(f"{BASE_URL}/jokes")
        assert response_get2.status_code == 200
        get_data = response_get2.json()

        assert len(get_data) == 1
        assert get_data[0]["id"] == post_data["id"]