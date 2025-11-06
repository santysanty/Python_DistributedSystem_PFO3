# server/db_manager.py
import psycopg2
from psycopg2.extras import RealDictCursor
from server.config import DB_CONFIG
import threading
import json
import traceback

db_lock = threading.Lock()
DB_AVAILABLE = True  # Bandera global de disponibilidad


def get_connection():
    """Intenta establecer conexión con la base de datos PostgreSQL."""
    global DB_AVAILABLE
    print("[DB DEBUG] Intentando conectar con la base de datos...")
    try:
        # Se elimina 'options' que provoca errores de codificación en Windows
        conn = psycopg2.connect(
            host=DB_CONFIG['host'],
            port=DB_CONFIG['port'],
            dbname=DB_CONFIG['dbname'],
            user=DB_CONFIG['user'],
            password=DB_CONFIG['password']
        )
        # Forzar UTF-8 para la sesión
        conn.set_client_encoding('UTF8')
        print("[DB DEBUG] Conexión establecida correctamente.")
        DB_AVAILABLE = True
        return conn

    except Exception as e:
        print(f"[DB ERROR] No se pudo conectar a la base de datos: {e}")
        traceback.print_exc()
        DB_AVAILABLE = False
        raise


def inicializar_db():
    """Crea la tabla 'resultados' si no existe."""
    global DB_AVAILABLE
    with db_lock:
        if not DB_AVAILABLE:
            print("[DB WARNING] La base de datos no está disponible. Se ignora la inicialización.")
            return
        conn = None
        cursor = None
        try:
            print("[DB DEBUG] Iniciando verificación/creación de tabla 'resultados'...")
            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS resultados (
                    id SERIAL PRIMARY KEY,
                    task_id INT NOT NULL,
                    task_type VARCHAR(50) NOT NULL,
                    input_data JSON NOT NULL,
                    result JSON NOT NULL,
                    fecha TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            conn.commit()
            print("[DB INFO] Tabla 'resultados' verificada o creada correctamente.")
        except Exception as e:
            print(f"[DB WARNING] Error inicializando la base de datos: {e}")
            traceback.print_exc()
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                print("[DB DEBUG] Conexión cerrada después de inicialización.")
            except Exception as close_err:
                print(f"[DB WARNING] Error al cerrar conexión: {close_err}")


def guardar_resultado(task_id, task_type, input_data, result):
    """Guarda el resultado en la base de datos, o lo ignora si no está disponible."""
    global DB_AVAILABLE
    with db_lock:
        print(f"[DB DEBUG] Intentando guardar resultado (task_id={task_id}, tipo={task_type})...")
        if not DB_AVAILABLE:
            print(f"[DB WARNING] Resultado de tarea {task_id} no guardado (DB no disponible).")
            return

        conn = None
        cursor = None
        try:
            # Serializar datos a JSON con UTF-8
            input_data_utf8 = json.dumps(input_data, ensure_ascii=False)
            result_utf8 = json.dumps(result, ensure_ascii=False)

            conn = get_connection()
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO resultados (task_id, task_type, input_data, result)
                VALUES (%s, %s, %s, %s)
            """, (task_id, task_type, input_data_utf8, result_utf8))
            conn.commit()
            print(f"[DB INFO] Resultado de tarea {task_id} guardado correctamente.")
        except Exception as e:
            print(f"[DB ERROR] Error guardando resultado: {e}")
            print(f"[DB DEBUG] Datos que fallaron: task_id={task_id}, input_data={input_data}, result={result}")
            traceback.print_exc()
            DB_AVAILABLE = False  # Desactivar flag hasta próxima conexión exitosa
        finally:
            try:
                if cursor:
                    cursor.close()
                if conn:
                    conn.close()
                print("[DB DEBUG] Conexión cerrada después de guardar resultado.")
            except Exception as close_err:
                print(f"[DB WARNING] Error al cerrar conexión: {close_err}")
