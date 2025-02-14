FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    curl \
    jq \
    && rm -rf /var/lib/apt/lists/*
# Copy the current directory contents into the container at /app
COPY . /app

# Copy the script to construct the connection string
# COPY construct_connection_string.sh /app/
# RUN chmod +x /app/construct_connection_string.sh

# Copy and ensure the entrypoint script is executable
COPY entrypoint.sh /app/
RUN chmod +x /app/entrypoint.sh

# Install package dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Download AWS RDS SSL Certificate
RUN mkdir -p /etc/ssl/certs && \
    curl -o /etc/ssl/certs/rds-combined-ca-bundle.pem \
    https://s3.amazonaws.com/rds-downloads/rds-combined-ca-bundle.pem

# Switch to non-root user
RUN adduser --disabled-password ctime-user
USER ctime-user

# Expose the port Flask runs on
EXPOSE 5000

# Set environment variables (will be overridden in production)
ENV PYTHONPATH=/app
ENV FLASK_APP=app.app
ENV FLASK_ENV=production
# ENV DATABASE_URL=mysql+pymysql://ctimeuser:ctimepassword@db:3306/ctime

# Run the application
# CMD ["/bin/bash", "-c", "source /app/construct_connection_string.sh && gunicorn -b 0.0.0.0:5000 'app.app:create_app()'"]
ENTRYPOINT ["/bin/bash", "-c", "/app/entrypoint.sh"]
