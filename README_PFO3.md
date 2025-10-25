# 🧩 PFO3 – Sistema Distribuido en Python (Cliente–Servidor con RabbitMQ)

## 📘 Descripción del Proyecto
Este proyecto forma parte del **PFO 3** de la materia **Programación sobre Redes**.  
El objetivo es **rediseñar un sistema monolítico** en una **arquitectura distribuida** utilizando **sockets TCP**, **RabbitMQ** como **cola de mensajería**, y **workers** para el procesamiento asíncrono de tareas.

---

## 🎯 Objetivos
- Comprender los fundamentos de los **sistemas distribuidos**.
- Implementar una **comunicación cliente-servidor** usando sockets en Python.
- Usar **RabbitMQ** para la distribución y persistencia de tareas.
- Simular un entorno de **balanceo de carga** con múltiples workers.
- Representar la arquitectura distribuida mediante un **diagrama del sistema**.

---

## 🧠 Arquitectura General

El sistema se compone de los siguientes módulos:

1. **Cliente (`cliente_tareas.py`)**  
   Envía tareas al distribuidor mediante un socket TCP.
   
2. **Servidor Distribuidor (`servidor_distribuidor.py`)**  
   Recibe tareas desde los clientes, las encapsula en JSON y las publica en la cola `tareas` de RabbitMQ.
   
3. **Workers (`servidor_worker.py`)**  
   Procesan las tareas recibidas desde RabbitMQ de forma asíncrona y simulan almacenamiento distribuido (PostgreSQL/S3).

4. **RabbitMQ**  
   Actúa como middleware de mensajería entre el distribuidor y los workers, asegurando el desacoplamiento entre los componentes.

---

## 🖥️ Diagrama del Sistema

El siguiente diagrama muestra la arquitectura distribuida del sistema:

```
[Clientes] 
     │ (Socket TCP)
     ▼
[Servidor Distribuidor]
     │ (Publica mensajes)
     ▼
[Cola de Mensajes - RabbitMQ]
     │ (Consume mensajes)
     ▼
[Workers 1..N] → [Almacenamiento Distribuido (PostgreSQL / S3)]
```

📊 Diagrama visual (archivo adjunto):  
`/docs/diagrama_sistema_distribuido.png`

---

## ⚙️ Ejecución del Sistema

### 1️⃣ Iniciar RabbitMQ
Asegurate de tener RabbitMQ en ejecución (por defecto en `localhost`):
```bash
rabbitmq-server
```

### 2️⃣ Iniciar el Servidor Distribuidor
```bash
python servidor_distribuidor.py
```

### 3️⃣ Iniciar uno o más Workers
En diferentes terminales:
```bash
python servidor_worker.py
```

### 4️⃣ Ejecutar el Cliente
En otra consola:
```bash
python cliente_tareas.py
```

---

## 🧩 Flujo de Comunicación

1. El **cliente** envía tareas JSON al **distribuidor**.
2. El **distribuidor** las encola en **RabbitMQ**.
3. Los **workers** suscriptos a la cola procesan las tareas y confirman recepción.
4. El **cliente** recibe confirmación inmediata del distribuidor (asíncrono).

---

## 🛠️ Requisitos
- Python 3.10+
- Librerías:
  ```bash
  pip install pika
  ```
- RabbitMQ en ejecución local (`localhost:5672`)

---

## 👨‍💻 Autor
**Daniel Coria**  
📍 Escuela de Educación Secundaria Técnica N°6 – Morón  
📧 Proyecto Académico – Programación sobre Redes

---

## 🗂️ Estructura del Repositorio
```
📦 Python_DistributedSystem_PFO3
 ┣ 📜 cliente_tareas.py
 ┣ 📜 servidor_distribuidor.py
 ┣ 📜 servidor_worker.py
 ┣ 📂 docs
 ┃ ┗ diagrama_sistema_distribuido.png
 ┗ 📜 README.md
```

---

## 🧾 Licencia
Proyecto académico bajo uso educativo y libre distribución con fines formativos.
