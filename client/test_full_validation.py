# client/test_full_validation.py
import socket
import json
import os
import threading
import time
from queue import Queue
import shutil

# ----------------------------
# Configuración
# ----------------------------
HOST = '127.0.0.1'
PORT = 5000
S3_PATH = './s3_bucket/'
os.makedirs(S3_PATH, exist_ok=True)

# Cola de tareas compartida
task_queue = Queue()

# ----------------------------
# Funciones Worker
# ----------------------------
def guardar_json(nombre_archivo, datos):
    ruta = os.path.join(S3_PATH, f"{nombre_archivo}.json")
    with open(ruta, 'w', encoding='utf-8') as f:
        json.dump(datos, f, indent=4)
    return ruta

def procesar_tarea(task):
    task_id = task.get("id")
    task_type = task.get("type")
    input_data = task.get("data")
    
    if task_type == "sumar":
        resultado = sum(input_data)
    elif task_type == "multiplicar":
        resultado = 1
        for n in input_data:
            resultado *= n
    else:
        resultado = {"info": "Tipo de tarea no implementado"}

    guardar_json(f"task_{task_id}", {"task": task, "result": resultado})
    return resultado

def worker_loop(worker_id, stop_event):
    while not stop_event.is_set():
        if not task_queue.empty():
            task = task_queue.get()
            procesar_tarea(task)
            task_queue.task_done()
        else:
            time.sleep(0.05)

def start_workers(num_workers, stop_event):
    threads = []
    for i in range(1, num_workers + 1):
        t = threading.Thread(target=worker_loop, args=(i, stop_event), daemon=True)
        t.start()
        threads.append(t)
    return threads

# ----------------------------
# Servidor TCP
# ----------------------------
def handle_client(conn, addr):
    try:
        data = conn.recv(1024)
        if data:
            task = json.loads(data.decode('utf-8'))
            task_queue.put(task)
            conn.sendall(f"Tarea {task.get('id')} recibida".encode('utf-8'))
    except Exception as e:
        print(f"[SERVER] Error con cliente {addr}: {e}")
    finally:
        conn.close()

def start_server(stop_event):
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_sock.bind((HOST, PORT))
    server_sock.listen()
    server_sock.settimeout(0.5)
    
    while not stop_event.is_set():
        try:
            conn, addr = server_sock.accept()
            threading.Thread(target=handle_client, args=(conn, addr), daemon=True).start()
        except:
            continue
    server_sock.close()

# ----------------------------
# Cliente
# ----------------------------
def enviar_tarea(task):
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.connect((HOST, PORT))
            s.sendall(json.dumps(task).encode('utf-8'))
            response = s.recv(1024).decode('utf-8')
            return response
    except Exception as e:
        return str(e)

# ----------------------------
# Main Test Unitario
# ----------------------------
if __name__ == "__main__":
    # Limpiar carpeta S3 simulada antes de test
    if os.path.exists(S3_PATH):
        shutil.rmtree(S3_PATH)
    os.makedirs(S3_PATH, exist_ok=True)

    stop_event = threading.Event()
    
    # Arrancar workers
    workers = start_workers(num_workers=2, stop_event=stop_event)

    # Arrancar servidor
    server_thread = threading.Thread(target=start_server, args=(stop_event,), daemon=True)
    server_thread.start()

    # Definir tareas de prueba
    tasks = [
        {"id": 1, "type": "sumar", "data": [5, 7]},
        {"id": 2, "type": "multiplicar", "data": [3, 4, 2]},
        {"id": 3, "type": "sumar", "data": [10, 15, 5]},
    ]

    # Enviar tareas
    for task in tasks:
        resp = enviar_tarea(task)
        print(f"[TEST CLIENT] {resp}")
        time.sleep(0.05)

    # Esperar procesamiento completo
    task_queue.join()

    # Verificar archivos JSON
    all_ok = True
    for task in tasks:
        file_path = os.path.join(S3_PATH, f"task_{task['id']}.json")
        if not os.path.exists(file_path):
            print(f"[TEST ERROR] JSON de tarea {task['id']} no generado")
            all_ok = False
            continue
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            expected_result = sum(task['data']) if task['type'] == 'sumar' else \
                              eval('*'.join(map(str, task['data'])))
            if data['result'] != expected_result:
                print(f"[TEST ERROR] Resultado incorrecto en tarea {task['id']}: esperado {expected_result}, encontrado {data['result']}")
                all_ok = False

    # Detener workers y servidor
    stop_event.set()
    time.sleep(1)

    if all_ok:
        print("[TEST] Todas las tareas procesadas correctamente y JSON validados ✅")
    else:
        print("[TEST] Fallos encontrados durante la validación ❌")
