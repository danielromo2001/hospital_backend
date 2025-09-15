from pydantic import BaseModel, Field, field_validator
from datetime import datetime, timezone, time
from typing import Optional
from enum import Enum

fecha_actual = datetime.now(timezone.utc)

class MotivoEnum(str, Enum):
    medicina_general = "Medicina General"
    odontologia = "Odontología"
    laboratorio = "Laboratorio"
    cardiologia = "Cardiología"
    dermatologia = "Dermatología"
    pediatria = "Pediatría"

class EstadoEnum(str, Enum):
    programada = "programada"
    completada = "completada"
    cancelada = "cancelada"

class CitaCreate(BaseModel):
    motivo: MotivoEnum = Field(..., description="Seleccione un servicio del hospital")
    fecha_hora: datetime = Field(..., description="Fecha y hora de la cita")
    notas: Optional[str] = Field(None, max_length=500, description="Notas adicionales")
    
    @field_validator('fecha_hora')
    @classmethod
    def validate_fecha_hora(cls, v):
        # Verificar que no sea en el pasado
        if v < datetime.now(timezone.utc):
            raise ValueError('No se puede agendar una cita en el pasado')
        
        # Verificar horarios de atención (8:00 AM - 6:00 PM)
        hora_cita = v.time()
        hora_inicio = time(8, 0)  # 8:00 AM
        hora_fin = time(18, 0)    # 6:00 PM
        
        if not (hora_inicio <= hora_cita <= hora_fin):
            raise ValueError('Las citas solo se pueden agendar entre las 8:00 AM y 6:00 PM')
        
        # Verificar que sea en días laborables (lunes a viernes)
        if v.weekday() >= 5:  # 5 = sábado, 6 = domingo
            raise ValueError('Las citas solo se pueden agendar de lunes a viernes')
        
        return v

class CitaOut(BaseModel):
    id: int
    motivo: str
    fecha_hora: datetime
    paciente_id: int
    estado: str
    notas: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class CitaUpdate(BaseModel):
    motivo: Optional[MotivoEnum] = None
    fecha_hora: Optional[datetime] = None
    estado: Optional[EstadoEnum] = None
    notas: Optional[str] = Field(None, max_length=500)
    
    @field_validator('fecha_hora')
    @classmethod
    def validate_fecha_hora(cls, v):
        if v is not None:
            # Verificar que no sea en el pasado
            if v < datetime.now(timezone.utc):
                raise ValueError('No se puede agendar una cita en el pasado')
            
            # Verificar horarios de atención (8:00 AM - 6:00 PM)
            hora_cita = v.time()
            hora_inicio = time(8, 0)  # 8:00 AM
            hora_fin = time(18, 0)    # 6:00 PM
            
            if not (hora_inicio <= hora_cita <= hora_fin):
                raise ValueError('Las citas solo se pueden agendar entre las 8:00 AM y 6:00 PM')
            
            # Verificar que sea en días laborables (lunes a viernes)
            if v.weekday() >= 5:  # 5 = sábado, 6 = domingo
                raise ValueError('Las citas solo se pueden agendar de lunes a viernes')
        
        return v



