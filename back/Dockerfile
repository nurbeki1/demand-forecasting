FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create data directory if not exists
RUN mkdir -p data/amazon data/ecommerce

# Expose port
EXPOSE 8000

# Run the application
CMD sh -c "uvicorn backend:app --host 0.0.0.0 --port ${PORT:-8000}"
