# app/auth.py
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import HTTPException, status, Depends
from sqlalchemy.orm import Session
from app.models.user import User
from app.database import get_db
from fastapi.security import OAuth2PasswordBearer

# Configuración de JWT
load_dotenv()
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Contexto para hashing de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Funciones de seguridad
def verificar_contraseña(contraseña_plana: str, contraseña_hash: str) -> bool:
    return pwd_context.verify(contraseña_plana, contraseña_hash)

def obtener_hash_contraseña(contraseña: str) -> str:
    return pwd_context.hash(contraseña)

def crear_token_acceso(data: dict, expiración: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expiración or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

def obtener_usuario_actual(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    cred_excep = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise cred_excep
    except JWTError:
        raise cred_excep

    usuario = db.query(User).filter(User.username == username).first()
    if usuario is None:
        raise cred_excep
    return usuario

def verificar_admin(usuario: User = Depends(obtener_usuario_actual)):
    if usuario.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Solo los administradores pueden acceder a esta ruta."
        )
    return usuario
