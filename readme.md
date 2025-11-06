README - Sistema Distribuido Cliente–Servidor (PFO3)
1️⃣ Descripción

Este proyecto implementa un sistema distribuido simulado, con:

Servidor TCP principal.

Workers concurrentes que procesan tareas de una cola.

Almacenamiento en PostgreSQL y en un S3 simulado local (archivos JSON).

Load balancer simple (round-robin) para redirigir clientes.

Script de prueba integral (master_test.py) que valida todo el flujo.

2️⃣ Estructura del proyecto
PFO3/
│
├── server/
│   ├── config.py            # Configuración general (DB, S3, workers, logs)
│   ├── db_manager.py        # Gestión de PostgreSQL
│   ├── logger_config.py     # Configuración de logs
│   ├── queue_manager.py     # Cola de tareas
│   ├── storage_s3.py        # Simulación de S3 local
│   ├── worker.py            # Workers y procesamiento de tareas
│   ├── main_server.py       # Servidor TCP principal
│   ├── load_balancer.py     # Round-robin simple
│   └── utils_server.py      # Funciones auxiliares (parse_json, build_response)
│
├── client/
│   └── test_client_full.py  # Cliente de prueba
│
├── s3_bucket/               # Carpeta donde se guardan los JSON simulando S3
├── logs/                    # Carpeta de logs del servidor
└── master_test.py           # Script de prueba integral

3️⃣ Requisitos
3.1 Python

Python 3.13 o superior.

Instalar pip si no lo tienes.

3.2 PostgreSQL

Instalar PostgreSQL.

Crear base de datos y usuario:

-- Abrir psql como superusuario:
CREATE DATABASE pfo3db;
CREATE USER postgres WITH PASSWORD '1234';
GRANT ALL PRIVILEGES ON DATABASE pfo3db TO postgres;


Ajusta config.py si cambias usuario, contraseña o puerto.

3.3 Dependencias Python

Instalar el driver de PostgreSQL:

pip install psycopg2-binary

4️⃣ Configuración

Archivo: server/config.py

HOST = '127.0.0.1'
PORT = 5432

DB_CONFIG = {
    'dbname': 'pfo3db',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5433
}

S3_PATH = './s3_bucket/'
NUM_WORKERS = 4
LOG_FILE = './logs/server.log'


Cambia rutas o parámetros según tu entorno.

5️⃣ Ejecución paso a paso
5.1 Iniciar servidor con workers
cd PFO3
python -m server.main_server


Inicia el servidor TCP en HOST:PORT.

Lanza NUM_WORKERS threads para procesar tareas.

Resultados se guardan en PostgreSQL y en s3_bucket/.

5.2 Probar con clientes

Desde otra terminal:

python -m client.test_client_full


Envía tareas de prueba al servidor.

Recibe confirmación de recepción y procesamiento.

5.3 Ejecutar test integral
python master_test.py


Inicializa DB y workers.

Arranca servidor TCP interno.

Envía tareas de prueba automáticamente.

Valida que JSON se hayan generado y resultados sean correctos.

Al final muestra resumen ✅ / ❌.

6️⃣ Notas importantes

Carpeta s3_bucket/ se limpia automáticamente al ejecutar master_test.py.

La cola de tareas usa queue.Queue() para simular RabbitMQ.

Concurrencia y seguridad de DB se manejan con locks.

Logs centralizados en logs/server.log.

load_balancer.py permite redirigir clientes a distintos servidores (round-robin), útil si se amplía a varios workers/servidores.

7️⃣ Ejemplo de salida
[TEST] Inicializando base de datos...
[TEST] Arrancando workers...
[TEST] Arrancando servidor TCP...
[CLIENT] Tarea 1 recibida
[CLIENT] Tarea 2 recibida
[CLIENT] Tarea 3 recibida
[TEST] MASTER TEST COMPLETO ✅ Todas las tareas procesadas correctamente

8️⃣ Limpieza y reinicio

Para reiniciar todo:

rm -rf s3_bucket/*
rm logs/server.log


Esto elimina JSONs y logs previos.