from pydantic import BaseModel, Field
from datetime import datetime, timezone
from typing import Optional
from enum import Enum

fecha_actual = datetime.now(timezone.utc)

class MotivoEnum(str, Enum):
    medicina_general = "Medicina General"
    odontologia = "Odontología"
    laboratorio = "Laboratorio"

class CitaCreate(BaseModel):
    motivo: MotivoEnum = Field(..., description="Seleccione un servicio del hospital")
    fecha_hora: datetime  # ejemplo: "2025-06-12T10:30:00"

class CitaOut(BaseModel):
    id: int
    motivo: str
    fecha_hora: datetime
    paciente_id: int

    class Config:
        from_attributes = True

class CitaUpdate(BaseModel):
    motivo: Optional[MotivoEnum] = None
    fecha_hora: Optional[datetime] = None



