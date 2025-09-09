from sqlalchemy.orm import Session
from app.models.user import User

def registrar_usuario(datos, db: Session, obtener_hash_contraseña):
    usuario_existente = db.query(User).filter(User.username == datos.username).first()
    if usuario_existente:
        return None, "El nombre de usuario ya existe"
    if datos.role not in ["paciente", "doctor"]:
        return None, "Solo se permite el registro como paciente o doctor."
    nuevo_usuario = User(
        username=datos.username,
        full_name=datos.full_name,
        hashed_password=obtener_hash_contraseña(datos.password),
        role=datos.role
    )
    db.add(nuevo_usuario)
    db.commit()
    db.refresh(nuevo_usuario)
    return nuevo_usuario, None

def autenticar_usuario(username, password, db: Session, verificar_contraseña):
    usuario = db.query(User).filter(User.username == username).first()
    if not usuario or not verificar_contraseña(password, usuario.hashed_password):
        return None, "Nombre de usuario o contraseña incorrectos"
    return usuario, None

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