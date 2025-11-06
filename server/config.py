# server/config.py

HOST = '127.0.0.1'
PORT = 5432

# Configuración de base de datos (PostgreSQL)
DB_CONFIG = {
    'dbname': 'pfo3db',
    'user': 'postgres',
    'password': '1234',
    'host': 'localhost',
    'port': 5433
}

# Simulación de S3 local
S3_PATH = './s3_bucket/'

# Número de workers simultáneos
NUM_WORKERS = 4

# Archivo de logs
LOG_FILE = './logs/server.log'

