def respuesta_exito(mensaje: str, datos: dict = None):
    return {"success": True, "mensaje": mensaje, "datos": datos or {}}

def respuesta_error(mensaje: str, detalles: dict = None):
    return {"success": False, "mensaje": mensaje, "detalles": detalles or {}}