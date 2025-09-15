from sqlalchemy.orm import Session
from sqlalchemy.exc import SQLAlchemyError
from app.utils.logging_config import get_logger
from typing import Callable, Any, Tuple

logger = get_logger("database_utils")

def with_transaction(db: Session, operation: Callable, *args, **kwargs) -> Tuple[Any, str]:
    """
    Ejecuta una operación dentro de una transacción con manejo de errores
    
    Args:
        db: Sesión de base de datos
        operation: Función a ejecutar
        *args, **kwargs: Argumentos para la función
    
    Returns:
        Tuple[resultado, error]: (resultado si exitoso, mensaje de error si falla)
    """
    try:
        result = operation(db, *args, **kwargs)
        db.commit()
        return result, None
    except SQLAlchemyError as e:
        db.rollback()
        logger.error(f"Error de base de datos: {str(e)}")
        return None, f"Error de base de datos: {str(e)}"
    except Exception as e:
        db.rollback()
        logger.error(f"Error inesperado: {str(e)}")
        return None, f"Error interno del servidor: {str(e)}"

def safe_db_operation(operation: Callable):
    """
    Decorador para operaciones seguras de base de datos
    """
    def wrapper(*args, **kwargs):
        db = None
        for arg in args:
            if isinstance(arg, Session):
                db = arg
                break
        
        if not db:
            return None, "Sesión de base de datos no encontrada"
        
        return with_transaction(db, operation, *args, **kwargs)
    
    return wrapper
