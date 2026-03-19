# Dockerfile for Google Cloud Run deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Set environment variables for production
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PORT=8080 \
    ENVIRONMENT=production

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better Docker layer caching
COPY requirements.txt .

# Install Python dependencies with optimizations
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code (excluding files in .dockerignore)
COPY . .

# Create directory for SQLite database and ensure permissions
RUN mkdir -p /app/data && \
    chmod -R 755 /app

# Health check (Cloud Run will use /health endpoint)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')" || exit 1

# Expose port (Cloud Run standard is 8080)
EXPOSE 8080

# Use exec form for better signal handling
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8080", "--workers", "1"]

