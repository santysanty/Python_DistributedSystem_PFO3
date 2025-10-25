# servidor_distribuidor.py
import socket
import threading
import json
import pika
import uuid # Para generar IDs de tarea

DIST_HOST = 'localhost'
DIST_PORT = 5000

# Conexión Global a RabbitMQ (se recomienda usar un canal por hilo en producción, pero simplificaremos)
connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()
channel.queue_declare(queue='tareas', durable=True) 

def manejar_cliente(client_socket, client_address):
    try:
        data = client_socket.recv(1024)
        if not data:
            return

        # 1. Recibir y preparar la Tarea
        tarea_data = json.loads(data.decode())
        tarea_id = tarea_data.get('id', str(uuid.uuid4())[:8])

        # 2. Publicar la Tarea en RabbitMQ (Desacoplamiento)
        channel.basic_publish(
            exchange='',
            routing_key='tareas',
            body=json.dumps(tarea_data).encode(),
            properties=pika.BasicProperties(delivery_mode=2) # Mensaje persistente
        )
        print(f"Distribuidor: Tarea {tarea_id} de {client_address[0]} enviada a RabbitMQ.")

        # 3. Responder al Cliente (Confirmación de recepción ASÍNCRONA)
        respuesta = f"Tarea {tarea_id} recibida y encolada. El procesamiento es asíncrono."
        client_socket.send(respuesta.encode())

    except Exception as e:
        print(f"Error procesando cliente {client_address}: {e}")
    finally:
        client_socket.close()

def iniciar_distribuidor():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((DIST_HOST, DIST_PORT))
    server_socket.listen(10)
    print(f"Servidor Distribuidor escuchando en {DIST_HOST}:{DIST_PORT}...")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Conexión Cliente {client_address} recibida.")
        # Usar un hilo para manejar la conexión y liberar el socket principal
        thread = threading.Thread(target=manejar_cliente, args=(client_socket, client_address))
        thread.start()

if __name__ == '__main__':
    iniciar_distribuidor()