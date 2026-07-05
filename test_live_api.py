import httpx
from app.database import SessionLocal
from app.models import Project, Experience, Writing, Certificate, Comment

BASE_URL = "http://127.0.0.1:8000"

def test_live_api():
    print("Testing live APIs...")

    try:
        # 1. Projects
        res = httpx.post(f"{BASE_URL}/api/projects", json={
            "title": "TEST_DATA_PROJECT"
        })
        print("POST Project:", res.status_code)
        
        # 2. Experiences
        res = httpx.post(f"{BASE_URL}/api/experiences", json={
            "company": "TEST_COMPANY",
            "position": "Tester",
            "start_date": "Now"
        })
        print("POST Experience:", res.status_code)

        # 3. Writings & Comments
        res = httpx.post(f"{BASE_URL}/api/writings", json={
            "title": "TEST_DATA_WRITING"
        })
        writing_id = res.json()["id"]
        print("POST Writing:", res.status_code)
        
        res = httpx.post(f"{BASE_URL}/api/writings/{writing_id}/comments", json={
            "username": "TEST_USER",
            "content": "TEST_COMMENT"
        })
        print("POST Comment:", res.status_code)

        # 4. Certificates
        res = httpx.post(f"{BASE_URL}/api/certificates", json={
            "name": "TEST_CERTIFICATE"
        })
        print("POST Certificate:", res.status_code)

        # Verify GET endpoints
        print("GET Projects:", httpx.get(f"{BASE_URL}/api/projects").status_code)
        print("GET Experiences:", httpx.get(f"{BASE_URL}/api/experiences").status_code)
        print("GET Writings:", httpx.get(f"{BASE_URL}/api/writings").status_code)
        print("GET Comments:", httpx.get(f"{BASE_URL}/api/writings/{writing_id}/comments").status_code)
        print("GET Certificates:", httpx.get(f"{BASE_URL}/api/certificates").status_code)

    except Exception as e:
        print(f"Error making requests: {e}")
        return

    # Cleanup
    print("\nCleaning up test data from the database...")
    db = SessionLocal()
    try:
        db.query(Project).filter(Project.title == "TEST_DATA_PROJECT").delete()
        db.query(Experience).filter(Experience.company == "TEST_COMPANY").delete()
        db.query(Writing).filter(Writing.title == "TEST_DATA_WRITING").delete()
        # Comments are deleted via cascade when writing is deleted, but we can be explicit
        db.query(Comment).filter(Comment.username == "TEST_USER").delete()
        db.query(Certificate).filter(Certificate.name == "TEST_CERTIFICATE").delete()
        db.commit()
        print("Cleanup complete!")
    finally:
        db.close()

if __name__ == "__main__":
    test_live_api()
