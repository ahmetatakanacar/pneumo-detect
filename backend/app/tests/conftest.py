import uuid
from pathlib import Path
import pytest
from fastapi.testclient import TestClient
from core.security import hash_password
from db.database import SessionLocal
from db.models import AnalysisResult, User, UserRole
from main import app

client = TestClient(app)

@pytest.fixture
def test_client():
    return client

@pytest.fixture
def db_session():
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def register_user(test_client, db_session):
    created_emails = []

    def _create(password="TestPassword123!"):
        email = f"test_{uuid.uuid4().hex[:12]}@example.com"
        response = test_client.post(
            "/auth/register",
            json={"email": email, "password": password},
        )
        created_emails.append(email)
        return response, {"email": email, "password": password}

    yield _create

    for email in created_emails:
        user = db_session.query(User).filter(User.email == email).first()
        if user is not None:
            db_session.query(AnalysisResult).filter(
                AnalysisResult.user_id == user.id
            ).delete()
            db_session.delete(user)
    db_session.commit()

@pytest.fixture
def make_user(db_session):

    created_emails = []

    def _create(role="readonly", password="TestPassword123!"):
        email = f"test_{uuid.uuid4().hex[:12]}@example.com"
        user = User(
            email=email,
            hashed_password=hash_password(password),
            role=UserRole(role),
        )
        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)
        created_emails.append(email)
        return {"email": email, "password": password, "role": role}

    yield _create

    for email in created_emails:
        user = db_session.query(User).filter(User.email == email).first()
        if user is not None:
            db_session.query(AnalysisResult).filter(
                AnalysisResult.user_id == user.id
            ).delete()
            db_session.delete(user)
    db_session.commit()

@pytest.fixture
def auth_headers(test_client, make_user):
    def _headers(role="readonly", password="TestPassword123!"):
        creds = make_user(role=role, password=password)
        response = test_client.post(
            "/auth/login",
            json={"email": creds["email"], "password": creds["password"]},
        )
        assert response.status_code == 200, response.text
        token = response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}

    return _headers

TEST_IMAGES_DIR = Path(__file__).resolve().parents[3] / "model" / "data" / "chest_xray" / "test"

@pytest.fixture
def sample_image():
    
    if TEST_IMAGES_DIR.exists():
        for candidate in TEST_IMAGES_DIR.rglob("*.jpeg"):
            return candidate
    pytest.skip(
        "model/data/chest_xray/test altında örnek görüntü bulunamadı "
        "(dataset .gitignore'da, bu makinede indirilmemiş olabilir)"
    )