# Use Python 3.12 slim image as base
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies for Playwright
RUN apt-get update && apt-get install -y \
    wget \
    gnupg \
    ca-certificates \
    procps \
    xvfb \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Install Playwright browsers
RUN playwright install --with-deps chromium

# Create src directory and copy application code
COPY src/ ./src/

# Create scripts directory (will be mounted)
RUN mkdir -p /app/scripts

# Set environment variables
ENV PYTHONPATH=/app

# Expose port for FastAPI
EXPOSE 8000

# Default command runs the REST API server
CMD ["python", "src/server.py"]

