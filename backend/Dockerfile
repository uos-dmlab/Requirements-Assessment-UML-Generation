# Multi-stage build for optimized production image
FROM python:3.12-slim as builder

# Set working directory
WORKDIR /app

# Set environment variables for builder stage
ENV PATH=/root/.local/bin:$PATH \
    PIP_USER=1

# Install system dependencies required for building Python packages
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Download spaCy language model (will install to /root/.local due to PIP_USER=1)
RUN python -m spacy download en_core_web_sm


# Production stage
FROM python:3.12-slim

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH=/root/.local/bin:$PATH

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    openjdk-21-jre-headless \
    graphviz \
    curl \
 && rm -rf /var/lib/apt/lists/*

# PlantUML needs to know where Graphviz dot binary is
ENV GRAPHVIZ_DOT=/usr/bin/dot

# Create non-root user for security
RUN useradd -m -u 1000 appuser && \
    mkdir -p /app && \
    chown -R appuser:appuser /app

# Set working directory
WORKDIR /app

# Copy Python dependencies from builder
COPY --from=builder --chown=appuser:appuser /root/.local /home/appuser/.local

# Update PATH for non-root user
ENV PATH=/home/appuser/.local/bin:$PATH

# Copy application code
COPY --chown=appuser:appuser . .

# Copy PlantUML jar file
COPY --chown=appuser:appuser plantuml.jar /app/plantuml.jar

# Switch to non-root user
USER appuser

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Expose port
EXPOSE 8000

# Run database migrations and start application
CMD ["sh", "-c", "alembic upgrade head && uvicorn app.main:app --host 0.0.0.0 --port 8000"]
