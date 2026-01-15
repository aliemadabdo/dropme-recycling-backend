FROM python:3.11-slim

# Prevent Python from buffering stdout/stderr
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app/staticfiles && \
    chown -R appuser:appuser /app

# Install Python dependencies first (better caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY --chown=appuser:appuser . .

# Copy production environment file to .env if it exists
# This allows prod_env.txt to be version controlled while .env is ignored
RUN if [ -f prod_env.txt ]; then \
        cp prod_env.txt .env && \
        chown appuser:appuser .env; \
    fi

# Copy entrypoint script
COPY entrypoint.sh /entrypoint.sh
RUN chmod +x /entrypoint.sh

# Switch to non-root user
USER appuser

# Expose app port
EXPOSE 8080

# Health check (can be overridden in docker-compose)
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/api/schema/').read()" || exit 1

# Start application
ENTRYPOINT ["/entrypoint.sh"]
