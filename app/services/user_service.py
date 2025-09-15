from sqlalchemy.orm import Session
from app.models.user import User
from app.utils.logging_config import get_logger

logger = get_logger("user_service")

def registrar_usuario(datos, db: Session, obtener_hash_contraseña):
    try:
        logger.info(f"Intentando registrar usuario: {datos.username}")
        
        # Verificar si el usuario ya existe
        usuario_existente = db.query(User).filter(
            (User.username == datos.username) | (User.email == datos.email)
        ).first()
        
        if usuario_existente:
            if usuario_existente.username == datos.username:
                logger.warning(f"Intento de registro con username existente: {datos.username}")
                return None, "El nombre de usuario ya existe"
            else:
                logger.warning(f"Intento de registro con email existente: {datos.email}")
                return None, "El email ya está registrado"
        
        if datos.role not in ["paciente", "doctor", "admin"]:
            logger.warning(f"Intento de registro con rol inválido: {datos.role}")
            return None, "Solo se permite el registro como paciente, doctor o admin."
        
        nuevo_usuario = User(
            username=datos.username,
            email=datos.email,
            full_name=datos.full_name,
            hashed_password=obtener_hash_contraseña(datos.password),
            role=datos.role
        )
        
        db.add(nuevo_usuario)
        db.commit()
        db.refresh(nuevo_usuario)
        
        logger.info(f"Usuario registrado exitosamente: {datos.username} (ID: {nuevo_usuario.id})")
        return nuevo_usuario, None
        
    except Exception as e:
        logger.error(f"Error al registrar usuario {datos.username}: {str(e)}")
        db.rollback()
        return None, f"Error interno del servidor: {str(e)}"

def autenticar_usuario(username, password, db: Session, verificar_contraseña):
    try:
        logger.info(f"Intento de autenticación para usuario: {username}")
        
        usuario = db.query(User).filter(User.username == username).first()
        if not usuario:
            logger.warning(f"Intento de login con usuario inexistente: {username}")
            return None, "Nombre de usuario o contraseña incorrectos"
        
        if not verificar_contraseña(password, usuario.hashed_password):
            logger.warning(f"Contraseña incorrecta para usuario: {username}")
            return None, "Nombre de usuario o contraseña incorrectos"
        
        if not usuario.is_active:
            logger.warning(f"Intento de login con usuario inactivo: {username}")
            return None, "Usuario inactivo"
        
        logger.info(f"Autenticación exitosa para usuario: {username}")
        return usuario, None
        
    except Exception as e:
        logger.error(f"Error al autenticar usuario {username}: {str(e)}")
        return None, "Error interno del servidor"

def crear_usuario_por_admin(datos, db: Session, obtener_hash_contraseña):
    usuario_existente = db.query(User).filter(User.username == datos.username).first()
    if usuario_existente:
        return None, "El nombre de usuario ya existe"
    nuevo_usuario = User(
        username=datos.username,
        full_name=datos.full_name,
        role=datos.role,
        hashed_password=obtener_hash_contraseña(datos.password)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario, None

def crear_usuario_admin(datos, db: Session, obtener_hash_contraseña):
    usuario_existente = db.query(User).filter(User.username == datos.username).first()
    if usuario_existente:
        return None, "El nombre de usuario ya existe"
    if datos.role != "admin":
        return None, "Solo se puede crear usuarios con rol admin en esta ruta."
    nuevo_usuario = User(
        username=datos.username,
        full_name=datos.full_name,
        role="admin",
        hashed_password=obtener_hash_contraseña(datos.password)
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario, None