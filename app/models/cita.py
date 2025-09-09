# app/models/cita.py

from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base
from datetime import datetime

class Cita(Base):
    __tablename__ = "citas"

    id = Column(Integer, primary_key=True, index=True)
    motivo = Column(String, nullable=False)
    fecha_hora = Column(DateTime, nullable=False)
    paciente_id = Column(Integer, ForeignKey("users.id"))

    paciente = relationship("User", back_populates="citas")
