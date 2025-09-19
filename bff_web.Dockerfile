# BFF Web Dockerfile
FROM python:3.11-slim

# Establecer directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requirements
COPY requirements-bff.txt .

# Instalar dependencias de Python
RUN pip install --no-cache-dir -r requirements-bff.txt

# Copiar código fuente
COPY src/bff_web/ ./src/bff_web/

# Crear directorio de logs
RUN mkdir -p /app/logs

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV DEBUG=false
ENV HOST=0.0.0.0
ENV PORT=8000
ENV SAGA_SERVICE_URL=http://partner-management:5000
ENV LOG_LEVEL=INFO

# Comando de inicio
CMD ["python", "-m", "uvicorn", "src.bff_web.app:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
