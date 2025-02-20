# --- Builder Stage ---
FROM python:3.11-slim AS builder

# Set the working directory
WORKDIR /ctime-app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libmariadb-dev \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Create a virtual environment
RUN python3 -m venv /venv

# Activate the virtual environment (for subsequent commands in this stage)
ENV PATH="/venv/bin:$PATH"

# Download AWS RDS SSL Certificate
RUN mkdir -p /build-output/certs && \
    curl -o /build-output/certs/rds-combined-ca-bundle.pem \
    https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . /ctime-app

# --- Final Stage ---
FROM python:3.11-slim

WORKDIR /ctime-app

# Install runtime system dependencies (minimal)
RUN apt-get update && apt-get install -y --no-install-recommends \
    libmariadb3 \
    jq \
    && rm -rf /var/lib/apt/lists/*

# Copy SSL certificates from builder stage
COPY --from=builder /build-output/certs /etc/ssl/certs/
# Copy virtual environment from builder stage
COPY --from=builder /venv /venv/
ENV PATH="/venv/bin:$PATH"
# Copy only necessary files from builder stage
COPY --from=builder /ctime-app/app /ctime-app/app/
COPY --from=builder /ctime-app/entrypoint.sh /ctime-app/entrypoint.sh

# Make entrypoint script executable
RUN chmod +x /ctime-app/entrypoint.sh

# Switch to non-root user
RUN adduser --disabled-password ctime-user
USER ctime-user

# Expose the port Flask runs on
EXPOSE 5000

# Set environment variables
ENV FLASK_APP=app.app
# ENV FLASK_ENV=production

# Run the application
ENTRYPOINT ["/bin/bash", "-c", "/ctime-app/entrypoint.sh"]
