# master_test.py
import os
import shutil
import threading
import time
import json
import socket
from queue import Empty

from server.queue_manager import task_queue, enqueue_task
from server.worker import worker_loop, procesar_tarea
from server.db_manager import inicializar_db, DB_AVAILABLE
from server.storage_s3 import S3_PATH

# ----------------------------
# Configuración
# ----------------------------
HOST = '127.0.0.1'
PORT = 5000
LOG_PATH = './logs/server.log'

# Asegurarse de que las carpetas existan
os.makedirs(S3_PATH, exist_ok=True)
os.makedirs('./logs', exist_ok=True)

# ----------------------------
# Limpieza inicial segura
# ----------------------------
if os.path.exists(S3_PATH):
    shutil.rmtree(S3_PATH)
os.makedirs(S3_PATH, exist_ok=True)

# Intentar eliminar log, ignorar errores si está en uso
try:
    if os.path.exists(LOG_PATH):
        os.remove(LOG_PATH)
except PermissionError:
    print(f"[WARN] No se pudo borrar {LOG_PATH} porque está en uso. Se continuará igualmente.")

# ----------------------------
# Funciones auxiliares
# ----------------------------
stop_event = threading.Event()

def start_workers(num_workers=2):
    threads = []
    for i in range(1, num_workers+1):
        t = threading.Thread(target=worker_loop_with_stop, args=(i,), daemon=True)
        t.start()
        threads.append(t)
    return threads

def worker_loop_with_stop(worker_id):
    print(f"[WORKER] Worker {worker_id} iniciado.")
    while not stop_event.is_set():
        try:
            task = task_queue.get(timeout=0.1)
            procesar_tarea(task)  # ya guarda en DB y S3
            task_queue.task_done()
        except Empty:
            continue
        except Exception as e:
            print(f"[WORKER ERROR] {worker_id}: {e}")
    print(f"[WORKER] Worker {worker_id} detenido.")

def calcular_resultado(task):
    if task["type"] == "sumar":
        return sum(task["data"])
    elif task["type"] == "multiplicar":
        result = 1
        for n in task["data"]:
            result *= n
        return result
    else:
        return {"info": "Tipo de tarea no implementado"}

# ----------------------------
# Servidor TCP simple
# ----------------------------
def handle_client(conn, addr):
    try:
        data = conn.recv(1024)
        if data:
            task = json.loads(data.decode('utf-8'))
            enqueue_task(task)
            conn.sendall(f"Tarea {task.get('id')} recibida".encode('utf-8'))
    except Exception as e:
        print(f"[SERVER] Error con cliente {addr}: {e}")
    finally:
        conn.close()

def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    server_sock.settimeout(0.5)
    print("[SERVER] Servidor TCP iniciado en", HOST, PORT)
    while not stop_event.is_set():
        try:
            conn, addr = server_sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except socket.timeout:
            continue
    server_sock.close()
    print("[SERVER] Servidor detenido")

# ----------------------------
# Main Master Test
# ----------------------------
if __name__ == "__main__":
    print("[TEST] Inicializando base de datos...")
    inicializar_db()

    print("[TEST] Arrancando workers...")
    workers = start_workers(num_workers=2)

    print("[TEST] Arrancando servidor TCP...")
    server_thread = threading.Thread(target=start_server, daemon=True)
    server_thread.start()

    # Tareas de prueba
    tasks = [
        {"id": 1, "type": "sumar", "data": [5, 7]},
        {"id": 2, "type": "multiplicar", "data": [3, 4, 2]},
        {"id": 3, "type": "sumar", "data": [10, 15, 5]},
    ]

    # Enviar tareas
    for task in tasks:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((HOST, PORT))
                s.sendall(json.dumps(task).encode('utf-8'))
                response = s.recv(1024).decode('utf-8')
                print(f"[CLIENT] {response}")
        except Exception as e:
            print(f"[CLIENT ERROR] {e}")
        time.sleep(0.05)

    # Esperar procesamiento completo
    task_queue.join()
    time.sleep(0.5)

    # Validar archivos JSON
    all_ok = True
    for task in tasks:
        file_path = os.path.join(S3_PATH, f"task_{task['id']}.json")
        if not os.path.exists(file_path):
            print(f"[TEST ERROR] JSON de tarea {task['id']} no generado")
            all_ok = False
            continue
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            expected_result = calcular_resultado(task)
            if data['result'] != expected_result:
                print(f"[TEST ERROR] Resultado incorrecto en tarea {task['id']}: esperado {expected_result}, encontrado {data['result']}")
                all_ok = False

    # Detener todo
    stop_event.set()
    time.sleep(1)

    if all_ok:
        print("[TEST] MASTER TEST COMPLETO ✅ Todas las tareas procesadas correctamente")
    else:
        print("[TEST] MASTER TEST COMPLETO ❌ Fallos encontrados")
