FROM python:3.11-slim

# Set the working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    default-libmysqlclient-dev \
    && rm -rf /var/lib/apt/lists/*
# Copy the current directory contents into the container at /app
COPY . /app

# Install package dependencies
RUN pip install --no-cache-dir --upgrade pip && pip install --no-cache-dir -r requirements.txt

# Switch to non-root user
RUN adduser --disabled-password ctime-user
USER ctime-user

# Expose the port Flask runs on
EXPOSE 5000

# Set environment variables (will be overridden in production)
ENV PYTHONPATH=/app
ENV FLASK_APP=app.app
ENV FLASK_ENV=production
ENV DATABASE_URL=mysql+pymysql://ctimeuser:ctimepassword@db:3306/ctime

# Run the application
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app.app:create_app()"]
