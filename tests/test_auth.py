import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

def test_register_user(client):
    """Prueba el registro de un nuevo usuario"""
    user_data = {
        "username": "newuser",
        "email": "newuser@example.com",
        "password": "NewPass123",
        "full_name": "New User",
        "role": "paciente"
    }
    
    response = client.post("/auth/registro", json=user_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "Usuario creado exitosamente" in response.json()["mensaje"]

def test_register_duplicate_username(client, test_user):
    """Prueba el registro con username duplicado"""
    user_data = {
        "username": "testuser",  # Usuario ya existe
        "email": "different@example.com",
        "password": "NewPass123",
        "full_name": "Different User",
        "role": "paciente"
    }
    
    response = client.post("/auth/registro", json=user_data)
    assert response.status_code == 400
    assert "El nombre de usuario ya existe" in response.json()["mensaje"]

def test_register_invalid_email(client):
    """Prueba el registro con email inválido"""
    user_data = {
        "username": "invalidemail",
        "email": "invalid-email",
        "password": "NewPass123",
        "full_name": "Invalid User",
        "role": "paciente"
    }
    
    response = client.post("/auth/registro", json=user_data)
    assert response.status_code == 422  # Validation error

def test_register_weak_password(client):
    """Prueba el registro con contraseña débil"""
    user_data = {
        "username": "weakpass",
        "email": "weak@example.com",
        "password": "123",  # Contraseña muy débil
        "full_name": "Weak User",
        "role": "paciente"
    }
    
    response = client.post("/auth/registro", json=user_data)
    assert response.status_code == 422  # Validation error

def test_login_success(client, test_user):
    """Prueba el login exitoso"""
    login_data = {
        "username": "testuser",
        "password": "TestPass123"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "access_token" in response.json()["datos"]

def test_login_invalid_credentials(client):
    """Prueba el login con credenciales inválidas"""
    login_data = {
        "username": "nonexistent",
        "password": "wrongpassword"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 400
    assert "incorrectos" in response.json()["mensaje"]

def test_login_inactive_user(client, db_session):
    """Prueba el login con usuario inactivo"""
    # Crear usuario inactivo
    from app.models.user import User
    from app.utils.seguridad import obtener_hash_contraseña
    
    inactive_user = User(
        username="inactive",
        email="inactive@example.com",
        full_name="Inactive User",
        hashed_password=obtener_hash_contraseña("InactivePass123"),
        role="paciente",
        is_active=False
    )
    db_session.add(inactive_user)
    db_session.commit()
    
    login_data = {
        "username": "inactive",
        "password": "InactivePass123"
    }
    
    response = client.post("/auth/login", data=login_data)
    assert response.status_code == 400
    assert "inactivo" in response.json()["mensaje"]
