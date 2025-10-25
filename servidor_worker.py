# servidor_worker.py
import pika
import time
import json
import os # Para identificar el worker si tienes múltiples instancias

WORKER_ID = os.getpid() # Usa el PID como identificador

def callback(ch, method, properties, body):
    tarea_data = json.loads(body)
    tarea_id = tarea_data.get('id', 'N/A')
    print(f"\n[Worker {WORKER_ID}] Tarea {tarea_id} recibida de RabbitMQ.")
    
    # SIMULACIÓN: Procesamiento (Pool de Hilos implícito en el diseño de RabbitMQ)
    time.sleep(2) # Simular procesamiento y latencia de DB/S3
    
    # SIMULACIÓN: Almacenamiento Distribuido (PostgreSQL/S3)
    print(f"[{time.strftime('%H:%M:%S')}] [Worker {WORKER_ID}] Tarea {tarea_id} PROCESADA Y ALMACENADA.")
    
    # Confirmar a RabbitMQ que el mensaje fue procesado
    ch.basic_ack(delivery_tag=method.delivery_tag)

def iniciar_worker():
    # Establecer conexión (asumiendo RabbitMQ en localhost)
    connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
    channel = connection.channel()

    # Declarar la cola (si no existe)
    channel.queue_declare(queue='tareas', durable=True) 
    print(f'[{WORKER_ID}] Esperando mensajes. Para salir presione CTRL+C')

    # Establecer QoS: solo tomar 1 mensaje a la vez para evitar sobrecarga (Control de Flujo)
    channel.basic_qos(prefetch_count=1) 
    
    # Suscribirse a la cola
    channel.basic_consume(queue='tareas', on_message_callback=callback)

    try:
        channel.start_consuming()
    except KeyboardInterrupt:
        print("Worker detenido.")
        channel.close()
        connection.close()

if __name__ == '__main__':
    iniciar_worker()