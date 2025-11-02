import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.database import Base, get_db
from app.main import app
from app import models

# Use in-memory SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()
    Base.metadata.drop_all(bind=engine)

@pytest.fixture(scope="function")
def client(db):
    return TestClient(app)

@pytest.fixture
def test_user(db):
    from app import auth
    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password": "testpass123"
    }
    user = models.User(
        username=user_data["username"],
        email=user_data["email"],
        hashed_password=auth.get_password_hash(user_data["password"])
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user, user_data

@pytest.fixture
def admin_user(db):
    from app import auth
    user = models.User(
        username="admin",
        email="admin@example.com",
        hashed_password=auth.get_password_hash("adminpass123"),
        is_admin=True
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user

