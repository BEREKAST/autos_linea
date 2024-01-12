# Define la imagen base
FROM python:3.9-slim

# Actualiza los paquetes y instala las dependencias necesarias para pyodbc
RUN apt-get update && apt-get install -y g++ unixodbc-dev && rm -rf /var/lib/apt/lists/*

# Establece el directorio de trabajo en el contenedor
WORKDIR /app

# Copia los archivos del proyecto al contenedor
COPY . /app

# Instala las dependencias del proyecto
RUN pip install --no-cache-dir -r requirements.txt

# Expone el puerto en el que se ejecutará la aplicación
EXPOSE 8000

# Define el comando para ejecutar la aplicación
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:8000", "main:app"]
