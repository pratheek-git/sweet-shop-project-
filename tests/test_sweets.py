import pytest
from fastapi import status

@pytest.fixture
def auth_token(client, test_user):
    """Get authentication token."""
    response = client.post("/api/auth/login", data={
        "username": "testuser",
        "password": "testpass123"
    })
    return response.json()["access_token"]

@pytest.fixture
def admin_token(client, admin_user):
    """Get admin authentication token."""
    response = client.post("/api/auth/login", data={
        "username": "admin",
        "password": "adminpass123"
    })
    return response.json()["access_token"]

@pytest.fixture
def test_sweet(client, admin_token):
    """Create a test sweet."""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Chocolate Bar",
            "category": "Chocolate",
            "price": 2.50,
            "quantity": 100
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    return response.json()

def test_create_sweet_admin(client, admin_token):
    """Test creating a sweet as admin."""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Gummy Bears",
            "category": "Candy",
            "price": 1.50,
            "quantity": 50
        },
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_201_CREATED
    data = response.json()
    assert data["name"] == "Gummy Bears"
    assert data["category"] == "Candy"
    assert data["price"] == 1.50
    assert data["quantity"] == 50

def test_create_sweet_non_admin(client, auth_token):
    """Test creating a sweet as non-admin (should fail)."""
    response = client.post(
        "/api/sweets",
        json={
            "name": "Lollipop",
            "category": "Candy",
            "price": 0.50,
            "quantity": 200
        },
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_get_all_sweets(client, auth_token, test_sweet):
    """Test getting all sweets."""
    response = client.get(
        "/api/sweets",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert any(sweet["name"] == "Chocolate Bar" for sweet in data)

def test_get_sweet_by_id(client, auth_token, test_sweet):
    """Test getting a sweet by ID."""
    sweet_id = test_sweet["id"]
    response = client.get(
        f"/api/sweets/{sweet_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["name"] == "Chocolate Bar"

def test_search_sweets_by_name(client, auth_token, test_sweet):
    """Test searching sweets by name."""
    response = client.get(
        "/api/sweets/search",
        params={"name": "Chocolate"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any("Chocolate" in sweet["name"] for sweet in data)

def test_search_sweets_by_category(client, auth_token, test_sweet):
    """Test searching sweets by category."""
    response = client.get(
        "/api/sweets/search",
        params={"category": "Chocolate"},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert len(data) >= 1
    assert any(sweet["category"] == "Chocolate" for sweet in data)

def test_search_sweets_by_price_range(client, auth_token, test_sweet):
    """Test searching sweets by price range."""
    response = client.get(
        "/api/sweets/search",
        params={"min_price": 2.0, "max_price": 3.0},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    for sweet in data:
        assert 2.0 <= sweet["price"] <= 3.0

def test_update_sweet_admin(client, admin_token, test_sweet):
    """Test updating a sweet as admin."""
    sweet_id = test_sweet["id"]
    response = client.put(
        f"/api/sweets/{sweet_id}",
        json={"price": 3.00},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["price"] == 3.00

def test_update_sweet_non_admin(client, auth_token, test_sweet):
    """Test updating a sweet as non-admin (should fail)."""
    sweet_id = test_sweet["id"]
    response = client.put(
        f"/api/sweets/{sweet_id}",
        json={"price": 3.00},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_delete_sweet_admin(client, admin_token, test_sweet):
    """Test deleting a sweet as admin."""
    sweet_id = test_sweet["id"]
    response = client.delete(
        f"/api/sweets/{sweet_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_204_NO_CONTENT
    
    # Verify it's deleted
    get_response = client.get(
        f"/api/sweets/{sweet_id}",
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert get_response.status_code == status.HTTP_404_NOT_FOUND

def test_delete_sweet_non_admin(client, auth_token, test_sweet):
    """Test deleting a sweet as non-admin (should fail)."""
    sweet_id = test_sweet["id"]
    response = client.delete(
        f"/api/sweets/{sweet_id}",
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_purchase_sweet(client, auth_token, test_sweet):
    """Test purchasing a sweet."""
    sweet_id = test_sweet["id"]
    initial_quantity = test_sweet["quantity"]
    
    response = client.post(
        f"/api/sweets/{sweet_id}/purchase",
        json={"quantity": 5},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["quantity"] == initial_quantity - 5

def test_purchase_sweet_insufficient_quantity(client, auth_token, test_sweet):
    """Test purchasing more sweets than available."""
    sweet_id = test_sweet["id"]
    
    response = client.post(
        f"/api/sweets/{sweet_id}/purchase",
        json={"quantity": 1000},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST

def test_restock_sweet_admin(client, admin_token, test_sweet):
    """Test restocking a sweet as admin."""
    sweet_id = test_sweet["id"]
    initial_quantity = test_sweet["quantity"]
    
    response = client.post(
        f"/api/sweets/{sweet_id}/restock",
        json={"quantity": 50},
        headers={"Authorization": f"Bearer {admin_token}"}
    )
    assert response.status_code == status.HTTP_200_OK
    data = response.json()
    assert data["quantity"] == initial_quantity + 50

def test_restock_sweet_non_admin(client, auth_token, test_sweet):
    """Test restocking a sweet as non-admin (should fail)."""
    sweet_id = test_sweet["id"]
    
    response = client.post(
        f"/api/sweets/{sweet_id}/restock",
        json={"quantity": 50},
        headers={"Authorization": f"Bearer {auth_token}"}
    )
    assert response.status_code == status.HTTP_403_FORBIDDEN

def test_access_protected_endpoint_without_token(client):
    """Test accessing protected endpoint without token."""
    response = client.get("/api/sweets")
    assert response.status_code == status.HTTP_401_UNAUTHORIZED

