import pytest
import io
import os
from dotenv import load_dotenv

load_dotenv()
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import schemas

# Setup database for testing (WARNING: This will drop tables in defaultdb!)
# To avoid data loss, ideally use a separate test database on the server.
SQLALCHEMY_DATABASE_URL = os.getenv("DATABASE_URL")
if not SQLALCHEMY_DATABASE_URL:
    raise ValueError("DATABASE_URL environment variable is not set")
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, 
    connect_args={"ssl": {}},
    pool_pre_ping=True,
    pool_recycle=1800
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db
client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_database():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def auth_headers():
    response = client.post("/api/auth/login", data={"username": "admin", "password": "adminboben2026"})
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}

# --- Auth Tests ---
def test_login_success():
    response = client.post("/api/auth/login", data={"username": "admin", "password": "adminboben2026"})
    assert response.status_code == 200
    assert "access_token" in response.json()

def test_login_fail():
    response = client.post("/api/auth/login", data={"username": "admin", "password": "wrong"})
    assert response.status_code == 401

def test_protected_route_without_token():
    response = client.post("/api/projects", json={"title": "Test", "url": "test"})
    assert response.status_code == 401

# --- Projects Tests ---
def test_create_project(auth_headers):
    response = client.post("/api/projects", json={
        "title": "My Project",
        "description": "A cool project",
        "url": "http://example.com"
    }, headers=auth_headers)
    assert response.status_code == 201
    assert response.json()["title"] == "My Project"

def test_get_projects(auth_headers):
    client.post("/api/projects", json={"title": "Test Project 1"}, headers=auth_headers)
    client.post("/api/projects", json={"title": "Test Project 2"}, headers=auth_headers)
    
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert len(response.json()) == 2

# --- Experiences Tests ---
def test_create_experience(auth_headers):
    response = client.post("/api/experiences", json={
        "company": "Test Company",
        "position": "Software Engineer",
        "start_date": "Jan 2025",
        "end_date": "Present",
        "description": "Building cool stuff",
        "img": "test.jpg",
        "points": '["Point 1", "Point 2"]',
        "images": '["img1.jpg", "img2.jpg"]',
        "bg_color": "bg-red-500",
        "url": "http://test.com"
    }, headers=auth_headers)
    assert response.status_code == 201

def test_get_experiences(auth_headers):
    client.post("/api/experiences", json={"company": "Company A", "position": "Role A", "start_date": "2020"}, headers=auth_headers)
    client.post("/api/experiences", json={"company": "Company B", "position": "Role B", "start_date": "2021"}, headers=auth_headers)
    
    response = client.get("/api/experiences")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_update_experience(auth_headers):
    create_response = client.post("/api/experiences", json={"company": "Old Company", "position": "Role", "start_date": "2020"}, headers=auth_headers)
    exp_id = create_response.json()["id"]

    update_response = client.put(f"/api/experiences/{exp_id}", json={"company": "New Company"}, headers=auth_headers)
    assert update_response.status_code == 200
    assert update_response.json()["company"] == "New Company"

def test_delete_experience(auth_headers):
    create_response = client.post("/api/experiences", json={"company": "To Delete", "position": "Role", "start_date": "2020"}, headers=auth_headers)
    exp_id = create_response.json()["id"]

    del_response = client.delete(f"/api/experiences/{exp_id}", headers=auth_headers)
    assert del_response.status_code == 204

# --- Certificates Tests ---
def test_create_certificate(auth_headers):
    response = client.post("/api/certificates", json={
        "name": "AWS Certified",
        "year": "2026",
        "description": "Cloud stuff",
        "img": "aws.png",
        "bg_color": "bg-orange-500",
        "link": "http://aws.com"
    }, headers=auth_headers)
    assert response.status_code == 201

def test_get_certificates(auth_headers):
    client.post("/api/certificates", json={"name": "Cert 1"}, headers=auth_headers)
    client.post("/api/certificates", json={"name": "Cert 2"}, headers=auth_headers)
    
    response = client.get("/api/certificates")
    assert response.status_code == 200
    assert len(response.json()) == 2

# --- Writings and Comments Tests ---
def test_create_writing_and_comments(auth_headers):
    # 1. Create a writing
    response = client.post("/api/writings", json={"title": "First Blog Post", "content": "This is the content.", "author": "John Doe", "author_img": "john.jpg", "image": "blog.jpg"}, headers=auth_headers)
    assert response.status_code == 201
    writing_id = response.json()["id"]

    # 3. Add a comment (Public route, no auth headers needed)
    response = client.post(f"/api/writings/{writing_id}/comments", json={"username": "User1", "content": "Great post!", "profile_img": "user1.jpg", "likes": 10})
    assert response.status_code == 201
    
def test_rate_limit_comments(auth_headers):
    # Create writing
    res = client.post("/api/writings", json={"title": "Test limit"}, headers=auth_headers)
    writing_id = res.json()["id"]
    
    # Hit comment endpoint 6 times. 6th should be 429 Too Many Requests
    for i in range(5):
        res = client.post(f"/api/writings/{writing_id}/comments", json={"username": f"User{i}", "content": "Spam!"})
        assert res.status_code == 201
        
    res = client.post(f"/api/writings/{writing_id}/comments", json={"username": "User6", "content": "Spam!"})
    assert res.status_code == 429

def test_get_writings(auth_headers):
    client.post("/api/writings", json={"title": "Writing 1"}, headers=auth_headers)
    client.post("/api/writings", json={"title": "Writing 2"}, headers=auth_headers)
    response = client.get("/api/writings")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_update_and_delete_writing(auth_headers):
    res = client.post("/api/writings", json={"title": "Test Title"}, headers=auth_headers)
    writing_id = res.json()["id"]

    update_res = client.put(f"/api/writings/{writing_id}", json={"title": "Updated Title"}, headers=auth_headers)
    assert update_res.status_code == 200

    del_res = client.delete(f"/api/writings/{writing_id}", headers=auth_headers)
    assert del_res.status_code == 204

def test_like_and_delete_comment(auth_headers):
    w_res = client.post("/api/writings", json={"title": "Post for comment tests"}, headers=auth_headers)
    writing_id = w_res.json()["id"]

    c_res = client.post(f"/api/writings/{writing_id}/comments", json={"username": "User", "content": "Hello"})
    comment_id = c_res.json()["id"]

    like_res = client.put(f"/api/comments/{comment_id}/like")
    assert like_res.status_code == 200

    del_res = client.delete(f"/api/comments/{comment_id}", headers=auth_headers)
    assert del_res.status_code == 204

# --- Upload Test ---
def test_upload_image(auth_headers):
    file_content = b"fake image content"
    response = client.post("/api/upload", files={"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")}, headers=auth_headers)
    assert response.status_code == 200
