from sqlalchemy.orm import Session
from datetime import datetime, timezone
from app.models.cita import Cita

def crear_cita(motivo, fecha_hora, paciente_id, db: Session):
    fecha_actual = datetime.now(timezone.utc)
    if fecha_hora < fecha_actual:
        return None, "No se puede agendar una cita en el pasado."
    nueva_cita = Cita(
        motivo=motivo,
        fecha_hora=fecha_hora,
        paciente_id=paciente_id
    )
    db.add(nueva_cita)
    db.commit()
    db.refresh(nueva_cita)
    return nueva_cita, None

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