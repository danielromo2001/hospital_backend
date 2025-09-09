# app/routers/auth_routes.py

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm, OAuth2PasswordBearer
from sqlalchemy.orm import Session
from app.utils import seguridad
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserCreate
from app.utils.respuestas import respuesta_exito, respuesta_error
from app.services.user_service import registrar_usuario, autenticar_usuario

router = APIRouter(prefix="/auth", tags=["Autenticación"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

@router.post("/registro", summary="Registrar un nuevo usuario")
def registrar_usuario_endpoint(datos: UserCreate, db: Session = Depends(get_db)):
    nuevo_usuario, error = registrar_usuario(datos, db, seguridad.obtener_hash_contraseña)
    if error:
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    return respuesta_exito("Usuario creado exitosamente")

@router.post("/login", summary="Obtener token de acceso")
def login_usuario(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    usuario, error = autenticar_usuario(form_data.username, form_data.password, db, seguridad.verificar_contraseña)
    if error:
        raise HTTPException(status_code=400, detail=respuesta_error(error))
    token = seguridad.crear_token_acceso(data={"sub": usuario.username})
    return respuesta_exito("Inicio de sesión exitoso", {"access_token": token, "token_type": "bearer"})
