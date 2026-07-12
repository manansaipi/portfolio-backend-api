import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.models.user import User

client = TestClient(app)

def test():
    # 1. Test Admin Login (which should work since we seeded it)
    admin_username = os.getenv("ADMIN_USERNAME", "admin")
    admin_password = os.getenv("ADMIN_PASSWORD", "123456") # Assume we don't know the plain password, so let's skip admin auth test if we don't know it. Actually, wait, .env doesn't have plain password, just hash. We can't login without plain text password. But we can test standard user register!
    
    # 2. Test Register
    test_user = {"user_name": "test_netflix_user", "password": "password123"}
    response = client.post("/api/users/register", json=test_user)
    if response.status_code == 201:
        print("Register: SUCCESS")
    elif response.status_code == 400 and "already registered" in response.text:
        print("Register: ALREADY REGISTERED")
    else:
        print(f"Register: FAILED - {response.text}")

    # 3. Test Login
    response = client.post("/api/users/token", json=test_user)
    if response.status_code == 200 and "access_token" in response.json():
        print("Login: SUCCESS")
        token = response.json()["access_token"]
    else:
        print(f"Login: FAILED - {response.text}")
        return

    # 4. Test Add Favorite
    headers = {"Authorization": f"Bearer {token}"}
    fav_data = {"user_id": "test_netflix_user", "movie_id": 123, "title": "Inception", "poster_path": "/path.jpg"}
    response = client.post("/api/favorites/add-favorite", json=fav_data, headers=headers)
    if response.status_code == 201:
        print("Add Favorite: SUCCESS")
    elif response.status_code == 400 and "already in favorites" in response.text:
        print("Add Favorite: ALREADY ADDED")
    else:
        print(f"Add Favorite: FAILED - {response.text}")

    # 5. Test List Favorites
    response = client.get("/api/favorites", headers=headers)
    if response.status_code == 200 and len(response.json()) > 0:
        print("List Favorites: SUCCESS")
    else:
        print(f"List Favorites: FAILED - {response.text}")

if __name__ == "__main__":
    test()
