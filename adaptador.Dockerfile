FROM python:3.12

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY sidecar-requirements.txt .
RUN pip install --no-cache-dir -r sidecar-requirements.txt

# Copy application source
COPY . .

# Set Python path
ENV PYTHONPATH=/app/src

# Run the adaptador service
CMD [ "python", "./src/adaptador/main.py" ]
