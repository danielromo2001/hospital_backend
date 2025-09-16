# app/routers/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.utils import seguridad
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.respuestas import respuesta_exito, respuesta_error
from app.services.user_service import registrar_usuario, autenticar_usuario
from app.utils.rate_limiting import check_rate_limit, record_failed_login, clear_login_attempts
from app.utils.logging_config import get_logger

logger = get_logger("auth_routes")

router = APIRouter(tags=["Autenticación"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/registro", summary="Registrar un nuevo usuario")
def registrar_usuario_endpoint(datos: UserCreate, db: Session = Depends(get_db)):
    nuevo_usuario, error = registrar_usuario(datos, db, seguridad.obtener_hash_contraseña)
    if error:
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    return respuesta_exito("Usuario creado exitosamente")

@router.post("/login", summary="Obtener token de acceso")
def login_usuario(
    request: Request,
    form_data: OAuth2PasswordRequestForm = Depends(), 
    db: Session = Depends(get_db)
):
    # Verificar rate limiting
    check_rate_limit(request)
    
    logger.info(f"Intento de login para usuario: {form_data.username}")
    
    usuario, error = autenticar_usuario(form_data.username, form_data.password, db, seguridad.verificar_contraseña)
    if error:
        # Registrar intento fallido
        record_failed_login(request)
        logger.warning(f"Login fallido para usuario: {form_data.username}")
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    
    # Limpiar intentos fallidos en caso de éxito
    clear_login_attempts(request)
    
    token = seguridad.crear_token_acceso(data={"sub": usuario.username})
    logger.info(f"Login exitoso para usuario: {form_data.username}")
    
    return respuesta_exito("Inicio de sesión exitoso", {"access_token": token, "token_type": "bearer"})
