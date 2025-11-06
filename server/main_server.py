# server/main_server.py
import socket
import json
import threading
from server.queue_manager import enqueue_task
from server.logger_config import setup_logger
from server.worker import start_workers
from server.config import HOST, PORT, NUM_WORKERS

logger = setup_logger()

def handle_client(conn, addr):
    """Maneja la conexión con un cliente."""
    logger.info(f"Cliente conectado: {addr}")
    print(f"Cliente conectado: {addr}")
    try:
        data = conn.recv(1024).decode('utf-8')
        if not data:
            return
        task = json.loads(data)
        enqueue_task(task)
        logger.info(f"Tarea recibida de {addr}: {task}")
        print(f"Tarea recibida: {task}")
        conn.sendall(b"Tarea recibida y encolada.\n")
    except Exception as e:
        logger.error(f"Error con cliente {addr}: {e}")
        print(f"Error con cliente {addr}: {e}")
        conn.sendall(f"Error: {str(e)}".encode('utf-8'))
    finally:
        conn.close()
        logger.info(f"Cliente {addr} desconectado.")
        print(f"Cliente desconectado: {addr}")

def start_server(stop_event=None):
    """Inicia el servidor principal con posibilidad de detenerlo mediante stop_event."""
    print("🚀 Iniciando servidor distribuido...")
    logger.info("Iniciando workers...")
    start_workers(NUM_WORKERS, stop_event)
    logger.info("Iniciando servidor principal...")

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.settimeout(0.5)  # para poder chequear stop_event periódicamente
        s.bind((HOST, PORT))
        s.listen()
        logger.info(f"Servidor escuchando en {HOST}:{PORT}")
        print("🚀 Servidor iniciado y escuchando en {}:{}".format(HOST, PORT))

        try:
            while True:
                if stop_event and stop_event.is_set():
                    logger.info("Stop event detectado. Cerrando servidor principal.")
                    print("Stop event detectado. Cerrando servidor principal.")
                    break
                try:
                    conn, addr = s.accept()
                    thread = threading.Thread(target=handle_client, args=(conn, addr), daemon=True)
                    thread.start()
                except socket.timeout:
                    continue
        finally:
            s.close()
            logger.info("Servidor principal detenido.")
            print("Servidor principal detenido.")

if __name__ == "__main__":
    stop_event = threading.Event()
    start_server(stop_event)
