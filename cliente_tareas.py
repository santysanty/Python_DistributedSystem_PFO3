# cliente_tareas.py
import socket
import json
import uuid
import time

SERVER_HOST = "localhost"
SERVER_PORT = 5000

def enviar_tarea(accion, datos):
    tarea = {
        "id": str(uuid.uuid4())[:8],
        "accion": accion,
        "datos": datos
    }
    return json.dumps(tarea)

# Conectar al servidor distribuidor
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client_socket.connect((SERVER_HOST, SERVER_PORT))
print(f"Conectado al Distribuidor en {SERVER_HOST}:{SERVER_PORT}\n")

try:
    for i in range(1, 4):
        tarea_msg = enviar_tarea(f"CREATE_TASK_{i}", {"description": f"Tarea de prueba {i}"})
        
        print(f"\n[CLIENTE] Enviando Tarea {i}...")
        client_socket.sendall(tarea_msg.encode())

        # Recibir confirmación ASÍNCRONA del Distribuidor
        respuesta = client_socket.recv(1024)
        print(f"[CLIENTE] Distribuidor -> {respuesta.decode()}")
        time.sleep(1)

except Exception as e:
    print(f"Error de conexión: {e}")
finally:
    client_socket.close()
    print("Cerrando conexión.")