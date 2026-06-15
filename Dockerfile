# ============================================================================
# MeshClean Debugger - Production Dockerfile
# ============================================================================
# Optimized for: Local Docker, AWS/Azure/GCP, Hugging Face Spaces
# Base: Lightweight Python 3.11 slim image

FROM python:3.11-slim

# Set metadata
LABEL maintainer="MeshClean Team"
LABEL description="MeshClean Debugger - AI-powered pipeline debugging"

# Set working directory
WORKDIR /app

# Install system dependencies (minimal for production)
RUN apt-get update && apt-get install -y --no-install-recommends \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Set Python environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1

# Copy requirements first (for Docker layer caching)
COPY requirements.txt .

# Install Python dependencies
RUN pip install --upgrade pip setuptools && \
    pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY pipeline_debug_env/ ./pipeline_debug_env/
COPY start_ui.py .
COPY ui_minimal.py .
COPY inference.py .

# Expose port for UI
EXPOSE 7860

# Set environment for server
ENV FLASK_APP=start_ui.py \
    FLASK_ENV=production \
    HOST=0.0.0.0 \
    PORT=7860

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:7860/ || exit 1

# Run the application
CMD ["python", "start_ui.py"]
