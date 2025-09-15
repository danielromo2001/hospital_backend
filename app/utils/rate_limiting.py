from fastapi import HTTPException, Request, status
from datetime import datetime, timedelta
from typing import Dict, Optional
import time
from collections import defaultdict
from app.utils.logging_config import get_logger

logger = get_logger("rate_limiting")

class RateLimiter:
    def __init__(self):
        # Almacenar intentos por IP
        self.attempts: Dict[str, list] = defaultdict(list)
        # Configuración de límites
        self.max_attempts = 5  # Máximo 5 intentos
        self.window_minutes = 15  # En 15 minutos
        self.lockout_minutes = 30  # Bloqueo por 30 minutos
        
    def is_rate_limited(self, ip: str) -> tuple[bool, Optional[str]]:
        """
        Verifica si una IP está rate limited
        Retorna: (is_limited, message)
        """
        now = datetime.now()
        window_start = now - timedelta(minutes=self.window_minutes)
        
        # Limpiar intentos antiguos
        self.attempts[ip] = [
            attempt_time for attempt_time in self.attempts[ip] 
            if attempt_time > window_start
        ]
        
        # Verificar si está en período de bloqueo
        if self.attempts[ip]:
            last_attempt = max(self.attempts[ip])
            if now - last_attempt < timedelta(minutes=self.lockout_minutes):
                remaining_time = self.lockout_minutes - (now - last_attempt).total_seconds() / 60
                return True, f"Demasiados intentos fallidos. Intenta nuevamente en {int(remaining_time)} minutos"
        
        # Verificar límite de intentos
        if len(self.attempts[ip]) >= self.max_attempts:
            logger.warning(f"Rate limit excedido para IP: {ip}")
            return True, f"Demasiados intentos fallidos. Intenta nuevamente en {self.lockout_minutes} minutos"
        
        return False, None
    
    def record_failed_attempt(self, ip: str):
        """Registra un intento fallido"""
        self.attempts[ip].append(datetime.now())
        logger.info(f"Intento fallido registrado para IP: {ip}")
    
    def clear_attempts(self, ip: str):
        """Limpia los intentos fallidos (para login exitoso)"""
        if ip in self.attempts:
            del self.attempts[ip]
            logger.info(f"Intentos limpiados para IP: {ip}")

# Instancia global del rate limiter
rate_limiter = RateLimiter()

def check_rate_limit(request: Request) -> None:
    """Middleware para verificar rate limiting"""
    client_ip = request.client.host
    
    is_limited, message = rate_limiter.is_rate_limited(client_ip)
    if is_limited:
        raise HTTPException(
            status_code=status.HTTP_429_TOO_MANY_REQUESTS,
            detail=message,
            headers={"Retry-After": str(rate_limiter.lockout_minutes * 60)}
        )

def record_failed_login(request: Request):
    """Registra un intento de login fallido"""
    client_ip = request.client.host
    rate_limiter.record_failed_attempt(client_ip)

def clear_login_attempts(request: Request):
    """Limpia los intentos de login (para login exitoso)"""
    client_ip = request.client.host
    rate_limiter.clear_attempts(client_ip)
