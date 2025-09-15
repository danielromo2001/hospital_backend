from sqlalchemy.orm import Session
from datetime import datetime, timezone, timedelta
from app.models.cita import Cita
from app.utils.logging_config import get_logger

logger = get_logger("cita_service")

def crear_cita(motivo, fecha_hora, paciente_id, notas=None, db: Session = None):
    try:
        logger.info(f"Creando cita para paciente {paciente_id} en {fecha_hora}")
        
        fecha_actual = datetime.now(timezone.utc)
        if fecha_hora < fecha_actual:
            logger.warning(f"Intento de agendar cita en el pasado: {fecha_hora}")
            return None, "No se puede agendar una cita en el pasado."
        
        # Verificar conflictos de horario (30 minutos de diferencia)
        inicio_ventana = fecha_hora - timedelta(minutes=30)
        fin_ventana = fecha_hora + timedelta(minutes=30)
        
        cita_conflicto = db.query(Cita).filter(
            Cita.fecha_hora.between(inicio_ventana, fin_ventana),
            Cita.estado == "programada"
        ).first()
        
        if cita_conflicto:
            logger.warning(f"Conflicto de horario detectado: {fecha_hora}")
            return None, f"Ya existe una cita programada cerca de este horario. Hora sugerida: {cita_conflicto.fecha_hora + timedelta(hours=1)}"
        
        # Verificar si el paciente ya tiene una cita en el mismo día
        inicio_dia = fecha_hora.replace(hour=0, minute=0, second=0, microsecond=0)
        fin_dia = fecha_hora.replace(hour=23, minute=59, second=59, microsecond=999999)
        
        cita_mismo_dia = db.query(Cita).filter(
            Cita.paciente_id == paciente_id,
            Cita.fecha_hora.between(inicio_dia, fin_dia),
            Cita.estado == "programada"
        ).first()
        
        if cita_mismo_dia:
            logger.warning(f"Paciente {paciente_id} ya tiene cita en el mismo día")
            return None, "Ya tienes una cita programada para este día"
        
        nueva_cita = Cita(
            motivo=motivo,
            fecha_hora=fecha_hora,
            paciente_id=paciente_id,
            notas=notas,
            estado="programada"
        )
        
        db.add(nueva_cita)
        db.commit()
        db.refresh(nueva_cita)
        
        logger.info(f"Cita creada exitosamente: ID {nueva_cita.id} para paciente {paciente_id}")
        return nueva_cita, None
        
    except Exception as e:
        logger.error(f"Error al crear cita para paciente {paciente_id}: {str(e)}")
        db.rollback()
        return None, f"Error interno del servidor: {str(e)}"

def obtener_citas_paciente(paciente_id, db: Session):
    return db.query(Cita).filter(Cita.paciente_id == paciente_id).all()

def obtener_todas_las_citas(db: Session):
    return db.query(Cita).all()

def eliminar_cita(cita_id, db: Session):
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        return None, "Cita no encontrada"
    db.delete(cita)
    db.commit()
    return cita, None

def eliminar_cita_paciente(cita_id, paciente_id, db: Session):
    cita = db.query(Cita).filter(Cita.id == cita_id, Cita.paciente_id == paciente_id).first()
    if not cita:
        return None, "Cita no encontrada o no te pertenece"
    db.delete(cita)
    db.commit()
    return cita, None

def editar_cita(cita_id, datos, db: Session):
    fecha_actual = datetime.now(timezone.utc)
    cita = db.query(Cita).filter(Cita.id == cita_id).first()
    if not cita:
        return None, "Cita no encontrada"
    if datos.fecha_hora and datos.fecha_hora < fecha_actual:
        return None, "No puedes poner una cita con fecha pasada."
    if datos.motivo is not None:
        cita.motivo = datos.motivo
    if datos.fecha_hora is not None:
        cita.fecha_hora = datos.fecha_hora
    db.commit()
    db.refresh(cita)
    return cita, None

def editar_cita_paciente(cita_id, paciente_id, datos, db: Session):
    fecha_actual = datetime.now(timezone.utc)
    cita = db.query(Cita).filter(Cita.id == cita_id, Cita.paciente_id == paciente_id).first()
    if not cita:
        return None, "Cita no encontrada o no te pertenece"
    if datos.fecha_hora and datos.fecha_hora < fecha_actual:
        return None, "No puedes poner una cita con fecha pasada."
    if datos.motivo is not None:
        cita.motivo = datos.motivo
    if datos.fecha_hora is not None:
        cita.fecha_hora = datos.fecha_hora
    db.commit()
    db.refresh(cita)
    return cita, None

def obtener_citas_de_hoy(paciente_id, db: Session):
    hoy = datetime.now(timezone.utc).date()
    citas = db.query(Cita).filter(
        Cita.paciente_id == paciente_id,
        Cita.fecha_hora >= datetime.combine(hoy, datetime.min.time(), tzinfo=timezone.utc),
        Cita.fecha_hora <= datetime.combine(hoy, datetime.max.time(), tzinfo=timezone.utc)
    ).all()
    return citas