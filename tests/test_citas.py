import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timezone, timedelta

def test_create_appointment_success(client, auth_headers):
    """Prueba la creación exitosa de una cita"""
    # Fecha futura (mañana a las 10:00 AM)
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    future_date = future_date.replace(hour=10, minute=0, second=0, microsecond=0)
    
    appointment_data = {
        "motivo": "Medicina General",
        "fecha_hora": future_date.isoformat(),
        "notas": "Consulta de rutina"
    }
    
    response = client.post("/citas/", json=appointment_data, headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "cita" in response.json()["datos"]

def test_create_appointment_past_date(client, auth_headers):
    """Prueba la creación de cita con fecha pasada"""
    past_date = datetime.now(timezone.utc) - timedelta(days=1)
    
    appointment_data = {
        "motivo": "Medicina General",
        "fecha_hora": past_date.isoformat()
    }
    
    response = client.post("/citas/", json=appointment_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error

def test_create_appointment_weekend(client, auth_headers):
    """Prueba la creación de cita en fin de semana"""
    # Calcular el próximo sábado
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    days_until_saturday = (5 - future_date.weekday()) % 7
    if days_until_saturday == 0:
        days_until_saturday = 7
    saturday = future_date + timedelta(days=days_until_saturday)
    saturday = saturday.replace(hour=10, minute=0, second=0, microsecond=0)
    
    appointment_data = {
        "motivo": "Medicina General",
        "fecha_hora": saturday.isoformat()
    }
    
    response = client.post("/citas/", json=appointment_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error

def test_create_appointment_outside_hours(client, auth_headers):
    """Prueba la creación de cita fuera del horario de atención"""
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    future_date = future_date.replace(hour=20, minute=0, second=0, microsecond=0)  # 8:00 PM
    
    appointment_data = {
        "motivo": "Medicina General",
        "fecha_hora": future_date.isoformat()
    }
    
    response = client.post("/citas/", json=appointment_data, headers=auth_headers)
    assert response.status_code == 422  # Validation error

def test_get_my_appointments(client, auth_headers):
    """Prueba obtener las citas del usuario autenticado"""
    response = client.get("/citas/", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert "citas" in response.json()["datos"]

def test_get_appointments_unauthorized(client):
    """Prueba obtener citas sin autenticación"""
    response = client.get("/citas/")
    assert response.status_code == 401

def test_get_today_appointments(client, auth_headers):
    """Prueba obtener las citas de hoy"""
    response = client.get("/citas/hoy", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_admin_get_all_appointments(client, admin_headers):
    """Prueba que el admin pueda ver todas las citas"""
    response = client.get("/citas/admin", headers=admin_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True

def test_patient_cannot_access_admin_endpoint(client, auth_headers):
    """Prueba que un paciente no pueda acceder a endpoints de admin"""
    response = client.get("/citas/admin", headers=auth_headers)
    assert response.status_code == 403

def test_cancel_my_appointment(client, auth_headers, db_session):
    """Prueba cancelar una cita propia"""
    from app.models.cita import Cita
    from app.models.user import User
    
    # Crear una cita de prueba
    user = db_session.query(User).filter(User.username == "testuser").first()
    future_date = datetime.now(timezone.utc) + timedelta(days=1)
    
    appointment = Cita(
        motivo="Medicina General",
        fecha_hora=future_date,
        paciente_id=user.id,
        estado="programada"
    )
    db_session.add(appointment)
    db_session.commit()
    db_session.refresh(appointment)
    
    response = client.delete(f"/citas/{appointment.id}", headers=auth_headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
