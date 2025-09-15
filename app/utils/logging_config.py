import logging
import sys
from datetime import datetime
import os

def setup_logging():
    """Configura el sistema de logging para la aplicación"""
    
    # Crear directorio de logs si no existe
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configurar el formato de los logs
    log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    date_format = "%Y-%m-%d %H:%M:%S"
    
    # Configurar el logger principal
    logger = logging.getLogger("hospital_api")
    logger.setLevel(logging.INFO)
    
    # Evitar duplicación de logs
    if logger.handlers:
        return logger
    
    # Handler para archivo
    file_handler = logging.FileHandler(
        f"{log_dir}/hospital_api_{datetime.now().strftime('%Y%m%d')}.log"
    )
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(file_formatter)
    
    # Handler para consola
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter(log_format, date_format)
    console_handler.setFormatter(console_formatter)
    
    # Agregar handlers al logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger

# Crear instancia global del logger
app_logger = setup_logging()

def get_logger(name: str = None):
    """Obtiene un logger específico para un módulo"""
    if name:
        return logging.getLogger(f"hospital_api.{name}")
    return app_logger
