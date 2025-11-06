# client/test_client_full.py
import socket
import json
import os
import time
import threading

from server.queue_manager import task_queue, enqueue_task
from server.worker import worker_loop

HOST = '127.0.0.1'
PORT = 5000

# Carpeta simulando S3 local
S3_PATH = './s3_bucket/'
os.makedirs(S3_PATH, exist_ok=True)

# Lista de tareas de prueba
tasks = [
    {"id": 1, "type": "sumar", "data": [5, 7]},
    {"id": 2, "type": "multiplicar", "data": [3, 4, 2]},
    {"id": 3, "type": "sumar", "data": [10, 15, 5]},
]

# Evento global para detener los workers al final
stop_event = threading.Event()

def start_test_workers(num_workers=2):
    """Arranca los workers en threads daemon."""
    threads = []
    for i in range(1, num_workers + 1):
        t = threading.Thread(target=worker_loop_with_stop, args=(i, stop_event), daemon=True)
        t.start()
        threads.append(t)
    return threads

def worker_loop_with_stop(worker_id, stop_event):
    """Loop de worker modificado para poder detenerlo con evento."""
    print(f"[WORKER] Worker {worker_id} iniciado.")
    while not stop_event.is_set():
        if not task_queue.empty():
            task = task_queue.get()
            # Importamos procesar_tarea dentro del loop para evitar problemas de import circular
            from server.worker import procesar_tarea
            procesar_tarea(task)
            task_queue.task_done()
        else:
            time.sleep(0.05)
    print(f"[WORKER] Worker {worker_id} detenido.")

def guardar_task_json_local(task_id, task_type, input_data, result):
    """Guarda un JSON local para referencia del cliente."""
    timestamp = int(time.time())
    file_path = os.path.join(S3_PATH, f"task_{task_id}_{timestamp}.json")
    data = {
        "task": {
            "id": task_id,
            "type": task_type,
            "data": input_data
        },
        "result": result
    }
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)
    return file_path

def calcular_resultado(task):
    """Calcula el resultado esperado de la tarea."""
    if task["type"] == "sumar":
        return sum(task["data"])
    elif task["type"] == "multiplicar":
        result = 1
        for n in task["data"]:
            result *= n
        return result
    else:
        return {"info": "Tipo de tarea no implementado"}

def esperar_json_worker(task_id, timeout=5):
    """Espera a que el worker genere el JSON correspondiente a la tarea."""
    ruta = os.path.join(S3_PATH, f"task_{task_id}.json")
    start = time.time()
    while not os.path.exists(ruta):
        if time.time() - start > timeout:
            return None
        time.sleep(0.05)
    with open(ruta, 'r', encoding='utf-8') as f:
        return json.load(f)

if __name__ == "__main__":
    # 1️⃣ Arrancar workers
    threads = start_test_workers(num_workers=2)

    # 2️⃣ Enviar tareas
    for task in tasks:
        enqueue_task(task)  # Poner tarea en la cola
        resultado_esperado = calcular_resultado(task)
        guardar_task_json_local(task["id"], task["type"], task["data"], resultado_esperado)

    # 3️⃣ Esperar que todas las tareas se procesen
    task_queue.join()  # Bloquea hasta que todas las tareas sean procesadas

    # 4️⃣ Validar resultados
    for task in tasks:
        resultado_real = esperar_json_worker(task["id"])
        if resultado_real and resultado_real.get("result") == calcular_resultado(task):
            print(f"[TEST OK] Tarea {task['id']} procesada correctamente por el worker.")
        else:
            print(f"[TEST FAIL] Tarea {task['id']} resultado incorrecto o no generado.")

    # 5️⃣ Detener workers
    stop_event.set()
    time.sleep(0.5)  # Dar tiempo a que los workers terminen
    print("[TEST] Todos los workers detenidos.")
