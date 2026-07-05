import pytest
import io
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.database import Base, get_db
from app import schemas

# Setup in-memory SQLite database for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
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

# --- Projects Tests ---
def test_create_project():
    response = client.post("/api/projects", json={
        "title": "My Project",
        "description": "A cool project",
        "url": "http://example.com"
    })
    assert response.status_code == 201
    assert response.json()["title"] == "My Project"

def test_get_projects():
    # Insert a project
    client.post("/api/projects", json={"title": "Test Project 1"})
    client.post("/api/projects", json={"title": "Test Project 2"})
    
    response = client.get("/api/projects")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["title"] == "Test Project 1"

# --- Experiences Tests ---
def test_create_experience():
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
    })
    assert response.status_code == 201
    assert response.json()["company"] == "Test Company"
    assert response.json()["start_date"] == "Jan 2025"

def test_get_experiences():
    client.post("/api/experiences", json={"company": "Company A", "position": "Role A", "start_date": "2020"})
    client.post("/api/experiences", json={"company": "Company B", "position": "Role B", "start_date": "2021"})
    
    response = client.get("/api/experiences")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_update_experience():
    create_response = client.post("/api/experiences", json={"company": "Old Company", "position": "Role", "start_date": "2020"})
    exp_id = create_response.json()["id"]

    update_response = client.put(f"/api/experiences/{exp_id}", json={"company": "New Company"})
    assert update_response.status_code == 200
    assert update_response.json()["company"] == "New Company"

# --- Certificates Tests ---
def test_create_certificate():
    response = client.post("/api/certificates", json={
        "name": "AWS Certified",
        "year": "2026",
        "description": "Cloud stuff",
        "img": "aws.png",
        "bg_color": "bg-orange-500",
        "link": "http://aws.com"
    })
    assert response.status_code == 201
    assert response.json()["name"] == "AWS Certified"

def test_get_certificates():
    client.post("/api/certificates", json={"name": "Cert 1"})
    client.post("/api/certificates", json={"name": "Cert 2"})
    
    response = client.get("/api/certificates")
    assert response.status_code == 200
    assert len(response.json()) == 2
    assert response.json()[0]["name"] == "Cert 1"

# --- Writings and Comments Tests ---
def test_create_writing_and_comments():
    # 1. Create a writing
    response = client.post("/api/writings", json={
        "title": "First Blog Post",
        "content": "This is the content.",
        "author": "John Doe",
        "author_img": "john.jpg",
        "image": "blog.jpg"
    })
    assert response.status_code == 201
    writing_id = response.json()["id"]
    assert response.json()["author"] == "John Doe"

    # 2. Test Get Writing by ID
    get_writing_response = client.get(f"/api/writings/{writing_id}")
    assert get_writing_response.status_code == 200
    assert get_writing_response.json()["title"] == "First Blog Post"

    # 3. Add a comment
    response = client.post(f"/api/writings/{writing_id}/comments", json={
        "username": "User1",
        "content": "Great post!",
        "profile_img": "user1.jpg",
        "likes": 10
    })
    assert response.status_code == 201
    comment1_id = response.json()["id"]
    assert response.json()["likes"] == 10

    # 4. Add a reply to the comment
    response = client.post(f"/api/writings/{writing_id}/comments", json={
        "username": "User2",
        "content": "I agree!",
        "parent_id": comment1_id
    })
    assert response.status_code == 201
    comment2_id = response.json()["id"]

    # 5. Add a reply to the reply
    response = client.post(f"/api/writings/{writing_id}/comments", json={
        "username": "User1",
        "content": "Thanks!",
        "parent_id": comment2_id
    })
    assert response.status_code == 201
    comment3_id = response.json()["id"]

    # 6. Fetch comments and verify the tree structure
    response = client.get(f"/api/writings/{writing_id}/comments")
    assert response.status_code == 200
    comments_tree = response.json()
    
    assert len(comments_tree) == 1 # Only 1 root comment
    root_comment = comments_tree[0]
    assert root_comment["id"] == comment1_id
    assert root_comment["username"] == "User1"
    
    assert len(root_comment["replies"]) == 1
    reply1 = root_comment["replies"][0]
    assert reply1["id"] == comment2_id
    assert reply1["username"] == "User2"
    
    assert len(reply1["replies"]) == 1
    reply2 = reply1["replies"][0]
    assert reply2["id"] == comment3_id
    assert reply2["username"] == "User1"
    assert len(reply2["replies"]) == 0

def test_get_writings():
    client.post("/api/writings", json={"title": "Writing 1"})
    client.post("/api/writings", json={"title": "Writing 2"})
    
    response = client.get("/api/writings")
    assert response.status_code == 200
    assert len(response.json()) == 2

def test_update_and_delete_writing():
    res = client.post("/api/writings", json={"title": "Test Title"})
    writing_id = res.json()["id"]

    update_res = client.put(f"/api/writings/{writing_id}", json={"title": "Updated Title"})
    assert update_res.status_code == 200
    assert update_res.json()["title"] == "Updated Title"

    del_res = client.delete(f"/api/writings/{writing_id}")
    assert del_res.status_code == 204

    get_res = client.get(f"/api/writings/{writing_id}")
    assert get_res.status_code == 404

def test_like_and_delete_comment():
    # 1. Create a writing
    w_res = client.post("/api/writings", json={"title": "Post for comment tests"})
    writing_id = w_res.json()["id"]

    # 2. Add comment
    c_res = client.post(f"/api/writings/{writing_id}/comments", json={"username": "User", "content": "Hello"})
    comment_id = c_res.json()["id"]
    likes_before = c_res.json()["likes"]

    # 3. Like comment
    like_res = client.put(f"/api/comments/{comment_id}/like")
    assert like_res.status_code == 200
    assert like_res.json()["likes"] == likes_before + 1

    # 4. Delete comment
    del_res = client.delete(f"/api/comments/{comment_id}")
    assert del_res.status_code == 204

# --- Upload Test ---
def test_upload_image():
    # We use a dummy file
    file_content = b"fake image content"
    response = client.post("/api/upload", files={"file": ("test.jpg", io.BytesIO(file_content), "image/jpeg")})
    assert response.status_code == 200
    assert "url" in response.json()
    assert response.json()["url"] == "/static/img/uploads/test.jpg"
