# server/load_balancer.py
import socket
import threading
from server.logger_config import setup_logger

# Configuración
SERVERS = [('127.0.0.1', 5001), ('127.0.0.1', 5002)]
LISTEN_HOST = '127.0.0.1'
LISTEN_PORT = 5000

# Round-robin
current_server_index = 0
lock = threading.Lock()

logger = setup_logger("load_balancer")

# ----------------------------
# Funciones de balanceo
# ----------------------------
def get_next_server():
    global current_server_index
    with lock:
        server = SERVERS[current_server_index]
        current_server_index = (current_server_index + 1) % len(SERVERS)
        return server

def handle_client(client_socket, client_addr):
    server_host, server_port = get_next_server()
    logger.info(f"Cliente {client_addr} redirigido a {server_host}:{server_port}")

    try:
        # Conectarse al servidor destino
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
            server_socket.connect((server_host, server_port))

            # Thread para enviar datos del cliente al servidor
            def forward(src, dst):
                try:
                    while True:
                        data = src.recv(4096)
                        if not data:
                            break
                        dst.sendall(data)
                except Exception as e:
                    pass

            t1 = threading.Thread(target=forward, args=(client_socket, server_socket))
            t2 = threading.Thread(target=forward, args=(server_socket, client_socket))

            t1.start()
            t2.start()
            t1.join()
            t2.join()

    except Exception as e:
        logger.error(f"Error redirigiendo cliente {client_addr} a {server_host}:{server_port} -> {e}")
    finally:
        client_socket.close()
        logger.info(f"Conexión con cliente {client_addr} finalizada")

# ----------------------------
# Servidor principal del load balancer
# ----------------------------
def start_load_balancer():
    logger.info(f"Load Balancer escuchando en {LISTEN_HOST}:{LISTEN_PORT}")
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((LISTEN_HOST, LISTEN_PORT))
        s.listen()

        while True:
            client_socket, client_addr = s.accept()
            logger.info(f"Nuevo cliente conectado: {client_addr}")
            threading.Thread(target=handle_client, args=(client_socket, client_addr), daemon=True).start()

# ----------------------------
# Main
# ----------------------------
if __name__ == "__main__":
    start_load_balancer()
