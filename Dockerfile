FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Create a non-root user
RUN useradd -m -u 1000 appuser

# Install system dependencies if needed
RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first for better layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY *.py ./
COPY templates/ ./templates/

# Copy config.yaml (will be created at runtime if missing, but prefer to include initial config)
COPY config.yaml ./

# Ensure appuser owns all files and can write to config.yaml
# This must be done after all COPY commands and before switching to appuser
RUN chown -R appuser:appuser /app && \
    chmod 664 /app/config.yaml 2>/dev/null || true

# Expose web port
EXPOSE 5000

# Switch to non-root user
USER appuser

# Run the application
CMD ["python", "main.py"]
