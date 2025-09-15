# app/models/cita.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    motivo = Column(String(100), nullable=False)
    fecha_hora = Column(DateTime, nullable=False, index=True)
    paciente_id = Column(Integer, ForeignKey("users.id"), index=True)
    estado = Column(String(20), default="programada")  # programada, completada, cancelada
    notas = Column(String(500), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    paciente = relationship("User", back_populates="citas")
