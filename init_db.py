#!/usr/bin/env python3
"""
Script para inicializar la base de datos con datos de prueba
"""
import os
import sys
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# Agregar el directorio raíz al path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.database import Base
from app.models.user import User
from app.models.cita import Cita
from app.utils.seguridad import obtener_hash_contraseña
from datetime import datetime, timezone, timedelta

def init_database():
    """Inicializa la base de datos con datos de prueba"""
    
    # URL de la base de datos
    database_url = os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/hospital_db")
    
    # Crear engine y sesión
    engine = create_engine(database_url)
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    # Crear todas las tablas
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    
    try:
        # Verificar si ya existen usuarios
        existing_admin = db.query(User).filter(User.role == "admin").first()
        if existing_admin:
            print("La base de datos ya está inicializada.")
            return
        
        # Crear usuario administrador por defecto
        admin_user = User(
            username="admin",
            email="admin@hospital.com",
            full_name="Administrador del Sistema",
            hashed_password=obtener_hash_contraseña("Admin123"),
            role="admin",
            is_active=True
        )
        
        # Crear usuario doctor de prueba
        doctor_user = User(
            username="doctor",
            email="doctor@hospital.com",
            full_name="Dr. Juan Pérez",
            hashed_password=obtener_hash_contraseña("Doctor123"),
            role="doctor",
            is_active=True
        )
        
        # Crear usuario paciente de prueba
        patient_user = User(
            username="paciente",
            email="paciente@hospital.com",
            full_name="María García",
            hashed_password=obtener_hash_contraseña("Paciente123"),
            role="paciente",
            is_active=True
        )
        
        db.add_all([admin_user, doctor_user, patient_user])
        db.commit()
        
        # Crear algunas citas de prueba
        future_date1 = datetime.now(timezone.utc) + timedelta(days=1)
        future_date1 = future_date1.replace(hour=10, minute=0, second=0, microsecond=0)
        
        future_date2 = datetime.now(timezone.utc) + timedelta(days=2)
        future_date2 = future_date2.replace(hour=14, minute=30, second=0, microsecond=0)
        
        appointment1 = Cita(
            motivo="Medicina General",
            fecha_hora=future_date1,
            paciente_id=patient_user.id,
            estado="programada",
            notas="Consulta de rutina"
        )
        
        appointment2 = Cita(
            motivo="Odontología",
            fecha_hora=future_date2,
            paciente_id=patient_user.id,
            estado="programada",
            notas="Revisión dental"
        )
        
        db.add_all([appointment1, appointment2])
        db.commit()
        
        print("✅ Base de datos inicializada exitosamente!")
        print("\n👥 Usuarios creados:")
        print("   Admin: admin / Admin123")
        print("   Doctor: doctor / Doctor123")
        print("   Paciente: paciente / Paciente123")
        print("\n📅 Citas de prueba creadas para el paciente")
        
    except Exception as e:
        print(f"❌ Error al inicializar la base de datos: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    init_database()
