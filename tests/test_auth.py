import pytest
from fastapi import status

def test_register_user(client):
    """Test user registration."""
    response = client.post("/api/auth/register", json={
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "password123"
    })
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["username"] == "newuser"
    assert data["email"] == "newuser@example.com"
    assert "id" in data
    assert "hashed_password" not in data

def test_register_duplicate_username(client, test_user):
    """Test registration with duplicate username."""
    response = client.post("/api/auth/register", json={
        "username": "testuser",
        "email": "different@example.com",
        "password": "password123"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_register_duplicate_email(client, test_user):
    """Test registration with duplicate email."""
    response = client.post("/api/auth/register", json={
        "username": "differentuser",
        "email": "test@example.com",
        "password": "password123"
    })
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_login_success(client, test_user):
    """Test successful login."""
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"

def test_login_wrong_password(client, test_user):
    """Test login with wrong password."""
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "wrongpassword"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_login_nonexistent_user(client):
    """Test login with nonexistent user."""
    response = client.post("/api/auth/login", data={
        "username": "nonexistent",
        "password": "password123"
    })
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

def test_get_current_user(client, test_user):
    """Test getting current user info."""
    # First login
    login_response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    token = login_response.json()["access_token"]
    
    # Get current user
    response = client.get("/api/auth/me", headers={
        "Authorization": f"Bearer {token}"
    })
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["username"] == "testuser"

def test_get_current_user_no_token(client):
    """Test getting current user without token."""
    response = client.get("/api/auth/me")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

