import pytest
from fastapi.testclient import TestClient

def test_create_user_by_admin(client, admin_headers):
    """Prueba que un admin pueda crear usuarios"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewPass123",
        "full_name": "New User",
        "role": "doctor"
    }
    
    response = client.post("/users/admin/crear", json=user_data, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_patient_cannot_create_users(client, auth_headers):
    """Prueba que un paciente no pueda crear usuarios"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewPass123",
        "full_name": "New User",
        "role": "doctor"
    }
    
    response = client.post("/users/admin/crear", json=user_data, headers=auth_headers)
    assert response.status_code == 403

def test_create_admin_user(client, admin_headers):
    """Prueba crear un usuario administrador"""
    admin_data = {
        "username": "newadmin",
        "email": "newadmin@example.com",
        "password": "AdminPass123",
        "full_name": "New Admin",
        "role": "admin"
    }
    
    response = client.post("/users/crear_admin", json=admin_data, headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_create_user_duplicate_email(client, admin_headers, test_user):
    """Prueba crear usuario con email duplicado"""
    user_data = {
        "username": "differentuser",
        "email": "test@example.com",  # Email ya existe
        "password": "NewPass123",
        "full_name": "Different User",
        "role": "doctor"
    }
    
    response = client.post("/users/admin/crear", json=user_data, headers=admin_headers)
    assert response.status_code == 400
    assert "email ya está registrado" in response.json()["mensaje"]

def test_create_user_invalid_role(client, admin_headers):
    """Prueba crear usuario con rol inválido"""
    user_data = {
        "username": "invalidrole",
        "email": "invalid@example.com",
        "password": "NewPass123",
        "full_name": "Invalid User",
        "role": "invalid_role"
    }
    
    response = client.post("/users/admin/crear", json=user_data, headers=admin_headers)
    assert response.status_code == 422  # Validation error
