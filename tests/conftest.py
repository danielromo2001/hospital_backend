import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool
import os

from app.main import app
from app.database import get_db, Base
from app.models.user import User
from app.models.cita import Cita
from app.utils.seguridad import obtener_hash_contraseña

# Base de datos de prueba en memoria
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

@pytest.fixture(scope="session")
def setup_database():
    """Configura la base de datos de prueba"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)

@pytest.fixture
def client(setup_database):
    """Cliente de prueba para la API"""
    return TestClient(app)

@pytest.fixture
def db_session(setup_database):
    """Sesión de base de datos para pruebas"""
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()

@pytest.fixture
def test_user(db_session):
    """Usuario de prueba"""
    user = User(
        username="testuser",
        email="test@example.com",
        full_name="Test User",
        hashed_password=obtener_hash_contraseña("TestPass123"),
        role="paciente"
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)
    return user

@pytest.fixture
def test_admin(db_session):
    """Administrador de prueba"""
    admin = User(
        username="admin",
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=obtener_hash_contraseña("AdminPass123"),
        role="admin"
    )
    db_session.add(admin)
    db_session.commit()
    db_session.refresh(admin)
    return admin

@pytest.fixture
def auth_headers(client, test_user):
    """Headers de autenticación para el usuario de prueba"""
    response = client.post("/auth/login", data={
        "username": "testuser",
        "password": "TestPass123"
    })
    token = response.json()["datos"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

@pytest.fixture
def admin_headers(client, test_admin):
    """Headers de autenticación para el administrador de prueba"""
    response = client.post("/auth/login", data={
        "username": "admin",
        "password": "AdminPass123"
    })
    token = response.json()["datos"]["access_token"]
    return {"Authorization": f"Bearer {token}"}
