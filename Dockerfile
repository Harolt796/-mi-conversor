# Usamos una imagen oficial de Python como base
FROM python:3.10-slim

# Instalamos FFmpeg usando el gestor de paquetes de la imagen (Debian)
RUN apt-get update && apt-get install -y --no-install-recommends ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Creamos un directorio de trabajo y nos movemos ahí
WORKDIR /app

# Copiamos los archivos de tu proyecto al contenedor
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Exponemos el puerto que usará Streamlit
EXPOSE 8501

# Comando para iniciar la aplicación
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
