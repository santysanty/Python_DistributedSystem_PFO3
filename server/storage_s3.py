import json
import os
from server.config import S3_PATH
from server.logger_config import setup_logger

logger = setup_logger()

def ensure_s3_path():
    """Crea la carpeta S3_PATH si no existe."""
    try:
        os.makedirs(S3_PATH, exist_ok=True)
        logger.debug(f"Carpeta S3_PATH verificada/creada: {S3_PATH}")
    except Exception as e:
        logger.error(f"No se pudo crear la carpeta S3_PATH: {e}")

def guardar_json(nombre_archivo, datos):
    """
    Guarda un diccionario como archivo JSON en la carpeta simulada S3.
    Devuelve la ruta completa del archivo guardado.
    """
    ensure_s3_path()
    ruta = os.path.join(S3_PATH, f"{nombre_archivo}.json")
    try:
        with open(ruta, "w", encoding="utf-8") as f:
            json.dump(datos, f, ensure_ascii=False, indent=4)
        logger.info(f"Archivo JSON guardado correctamente: {ruta}")
        return ruta
    except (TypeError, ValueError) as e:
        logger.error(f"Error serializando datos para {ruta}: {e}")
        return None
    except Exception as e:
        logger.error(f"No se pudo guardar el archivo {ruta}: {e}")
        return None
