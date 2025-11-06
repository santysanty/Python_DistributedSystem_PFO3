# server/worker.py
import threading
import time
from server.queue_manager import task_queue
from server.db_manager import guardar_resultado, inicializar_db, DB_AVAILABLE
from server.storage_s3 import guardar_json
from server.logger_config import setup_logger

logger = setup_logger()

def procesar_tarea(task):
    """
    Procesa la tarea recibida y devuelve un resultado simulado.
    Guarda resultados en DB y S3 simulado.
    """
    task_id = task.get("id")
    task_type = task.get("type")
    input_data = task.get("data")

    logger.info(f"Procesando tarea {task_id}: {task_type}")
    print(f"Procesando tarea {task_id}: {task_type}")

    resultado = None
    try:
        if task_type == "sumar":
            resultado = sum(input_data)
        elif task_type == "multiplicar":
            resultado = 1
            for n in input_data:
                resultado *= n
        else:
            resultado = {"info": "Tipo de tarea no implementado"}
    except Exception as e:
        resultado = {"error": str(e)}

    # Guardar en PostgreSQL
    try:
        if DB_AVAILABLE:
            guardar_resultado(task_id, task_type, input_data, resultado)
    except Exception as e:
        logger.error(f"No se pudo guardar resultado en DB: {e}")
        print(f"[WARN] No se pudo guardar resultado en DB: {e}")

    # Guardar en S3 simulado
    try:
        guardar_json(f"task_{task_id}", {"task": task, "result": resultado})
    except Exception as e:
        logger.error(f"No se pudo guardar resultado en S3 simulado: {e}")
        print(f"[WARN] No se pudo guardar resultado en S3 simulado: {e}")

    logger.info(f"Tarea {task_id} procesada. Resultado: {resultado}")
    print(f"Tarea {task_id} procesada. Resultado: {resultado}")


def worker_loop(worker_id, stop_event=None):
    """Loop continuo de cada worker procesando tareas de la cola."""
    logger.info(f"Worker {worker_id} iniciado.")
    print(f"Worker {worker_id} iniciado.")
    while True:
        if stop_event and stop_event.is_set():
            logger.info(f"Worker {worker_id} detenido por stop_event.")
            print(f"Worker {worker_id} detenido por stop_event.")
            break
        if not task_queue.empty():
            task = task_queue.get()
            procesar_tarea(task)
            task_queue.task_done()
        else:
            time.sleep(0.1)


def start_workers(num_workers=2, stop_event=None):
    """Inicializa y arranca N workers en threads independientes."""
    try:
        inicializar_db()  # Asegurarse de que la tabla exista
    except Exception as e:
        logger.error(f"No se pudo inicializar la base de datos: {e}")
        print(f"[WARN] No se pudo inicializar la base de datos: {e}")

    threads = []
    for i in range(1, num_workers + 1):
        t = threading.Thread(target=worker_loop, args=(i, stop_event), daemon=True)
        t.start()
        threads.append(t)
        logger.info(f"Worker {i} iniciado y en ejecución.")
        print(f"Worker {i} iniciado y en ejecución.")
    return threads
