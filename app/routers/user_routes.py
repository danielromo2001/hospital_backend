from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.utils.seguridad import verificar_admin, obtener_hash_contraseña
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate, UserOut
from app.utils.respuestas import respuesta_exito, respuesta_error
from app.services.user_service import crear_usuario_por_admin, crear_usuario_admin

router = APIRouter(prefix="/usuarios", tags=["Usuarios"])

##@router.get("/perfil", summary="Obtener perfil del usuario autenticado")
##def obtener_perfil(usuario: User = Depends(obtener_usuario_actual)):
##    return {
##        "id": usuario.id,
##        "username": usuario.username,
##        "nombre_completo": usuario.full_name,
##        "rol": usuario.role,
##        "activo": usuario.is_active
##    }

@router.post("/admin/crear", response_model=UserOut, summary="Crear usuario (solo admin)")
def crear_usuario_por_admin_endpoint(usuario: UserCreate, db: Session = Depends(get_db), admin: User = Depends(verificar_admin)):
    nuevo_usuario, error = crear_usuario_por_admin(usuario, db, obtener_hash_contraseña)
    if error:
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    return respuesta_exito("Usuario creado exitosamente", {"usuario": nuevo_usuario.username})

@router.post("/crear_admin", summary="Crear usuario administrador", dependencies=[Depends(verificar_admin)])
def crear_usuario_admin_endpoint(datos: UserCreate, db: Session = Depends(get_db)):
    nuevo_usuario, error = crear_usuario_admin(datos, db, obtener_hash_contraseña)
    if error:
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    return respuesta_exito("Usuario administrador creado exitosamente", {"usuario": nuevo_usuario.username})