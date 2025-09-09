from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.schemas.cita import CitaCreate, CitaOut, CitaUpdate
from app.utils.seguridad import obtener_usuario_actual, verificar_admin
from app.utils.respuestas import respuesta_exito, respuesta_error
from app.services.cita_service import (
    crear_cita, obtener_citas_paciente, obtener_todas_las_citas,
    eliminar_cita, eliminar_cita_paciente, editar_cita, editar_cita_paciente,
    obtener_citas_de_hoy
)

router = APIRouter(prefix="/citas", tags=["Citas"])

@router.post("/", summary="Agendar una cita médica")
def crear_cita_endpoint(cita: CitaCreate, db: Session = Depends(get_db), usuario: User = Depends(obtener_usuario_actual)):
    nueva_cita, error = crear_cita(cita.motivo, cita.fecha_hora, usuario.id, db)
    if error:
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    return respuesta_exito("Cita agendada exitosamente", {"cita": nueva_cita.id})

@router.get("/", summary="Consultar mis citas")
def obtener_mis_citas(db: Session = Depends(get_db), usuario: User = Depends(obtener_usuario_actual)):
    citas = obtener_citas_paciente(usuario.id, db)
    return respuesta_exito("Citas obtenidas exitosamente", {"citas": citas})

@router.get("/admin", summary="Ver todas las citas (admin)")
def obtener_todas_las_citas_endpoint(db: Session = Depends(get_db), admin: User = Depends(verificar_admin)):
    citas = obtener_todas_las_citas(db)
    return respuesta_exito("Todas las citas obtenidas", {"citas": citas})

@router.delete("/admin/{cita_id}", summary="Eliminar una cita (admin)")
def eliminar_cita_endpoint(cita_id: int, db: Session = Depends(get_db), admin: User = Depends(verificar_admin)):
    cita, error = eliminar_cita(cita_id, db)
    if error:
        raise HTTPException(status_code=404, detail=respuesta_error(error))
    return respuesta_exito("Cita eliminada correctamente", {"cita_id": cita_id})

@router.delete("/{cita_id}", summary="Cancelar mi propia cita")
def cancelar_mi_cita(cita_id: int, db: Session = Depends(get_db), usuario: User = Depends(obtener_usuario_actual)):
    cita, error = eliminar_cita_paciente(cita_id, usuario.id, db)
    if error:
        raise HTTPException(status_code=404, detail=respuesta_error(error))
    return respuesta_exito("Cita cancelada exitosamente", {"cita_id": cita_id})

@router.put("/{cita_id}", summary="Editar mi cita")
def editar_mi_cita_endpoint(cita_id: int, datos: CitaUpdate, db: Session = Depends(get_db), usuario: User = Depends(obtener_usuario_actual)):
    cita, error = editar_cita_paciente(cita_id, usuario.id, datos, db)
    if error:
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    return respuesta_exito("Cita editada exitosamente", {"cita": cita.id})

@router.put("/admin/{cita_id}", summary="Editar cita (admin)")
def editar_cita_admin_endpoint(cita_id: int, datos: CitaUpdate, db: Session = Depends(get_db), admin: User = Depends(verificar_admin)):
    cita, error = editar_cita(cita_id, datos, db)
    if error:
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    return respuesta_exito("Cita editada exitosamente", {"cita": cita.id})

@router.get("/hoy", summary="Ver mis citas de hoy")
def obtener_citas_de_hoy_endpoint(db: Session = Depends(get_db), usuario: User = Depends(obtener_usuario_actual)):
    citas = obtener_citas_de_hoy(usuario.id, db)
    return respuesta_exito("Citas de hoy obtenidas exitosamente", {"citas": citas})