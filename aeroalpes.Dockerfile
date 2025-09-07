FROM python:3.12

# Expose port
EXPOSE 5000/tcp

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY . .

# Set Python path
ENV PYTHONPATH=/app/src

# Run the application
CMD [ "flask", "--app", "./src/partner_management/api", "run", "--host=0.0.0.0"]
