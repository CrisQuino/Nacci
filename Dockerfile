# Dockerfile

FROM python:3.10-slim

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos al contenedor
COPY . /app

# Instalar dependencias
RUN pip install --no-cache-dir -r requirements.txt

# Comando por defecto
CMD ["python", "main.py"]
