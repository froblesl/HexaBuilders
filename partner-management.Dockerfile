FROM python:3.11-slim

# Expose port
EXPOSE 5000/tcp

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better caching
COPY requirements.txt pulsar-requirements.txt ./

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r pulsar-requirements.txt

# Copy source code
COPY src/ ./src/

# Set Python path
ENV PYTHONPATH=/app/src

# Run the application
CMD [ "flask", "--app", "partner_management.seedwork.presentacion.api:create_app", "run", "--host=0.0.0.0", "--port=5000"]
