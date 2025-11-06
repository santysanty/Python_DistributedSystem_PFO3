import json

def parse_json(data):
    """
    Intenta convertir un string JSON en un diccionario de Python.
    Devuelve None si falla.
    """
    try:
        return json.loads(data)
    except (json.JSONDecodeError, TypeError) as e:
        print(f"[UTILS] Error al parsear JSON: {e}")
        return None

def build_response(status, message, payload=None):
    """
    Construye un diccionario con estructura uniforme para las respuestas del servidor.
    """
    response = {
        "status": status,
        "message": message
    }
    if payload is not None:
        response["payload"] = payload
    return response
