from queue import Queue, Empty
from server.logger_config import setup_logger

logger = setup_logger()

# Cola compartida que simula RabbitMQ
task_queue = Queue()

def enqueue_task(task):
    """Agrega una tarea a la cola de manera segura."""
    try:
        task_queue.put(task)
        logger.debug(f"Tarea encolada: {task}")
    except Exception as e:
        logger.error(f"No se pudo encolar la tarea: {e}")

def dequeue_task(timeout=0.1):
    """Obtiene una tarea de la cola. Devuelve None si la cola está vacía."""
    try:
        return task_queue.get(timeout=timeout)
    except Empty:
        return None
    except Exception as e:
        logger.error(f"No se pudo obtener tarea de la cola: {e}")
        return None

def queue_size():
    """Retorna la cantidad de tareas en la cola."""
    try:
        return task_queue.qsize()
    except Exception as e:
        logger.error(f"No se pudo obtener el tamaño de la cola: {e}")
        return 0
