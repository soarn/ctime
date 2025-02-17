#!/bin/bash
set -e # Exit on error

# Check if MYSQL_USER, MYSQL_DATABASE, and MYSQL_PASSWORD are defined
if [ -n "$MYSQL_USER" ] && [ -n "$MYSQL_DATABASE" ] && [ -n "$MYSQL_PASSWORD" ]; then
    echo "Using environment variables for database connection"
    DB_USER=$MYSQL_USER
    DB_PASS=$MYSQL_PASSWORD
    DB_HOST=${MYSQL_HOST:-db} # Default to local database name if MYSQL_HOST is not set
    DB_NAME=$MYSQL_DATABASE
    SSL_CA_PATH=""
else
    echo "Fetching secrets from AWS SSM Parameter Store..."
    # Parse the DB_SECRET JSON and set CONNECTION_STRING
    if [ -z "$DB_SECRET" ]; then
        echo "ERROR: DB_SECRET is not set"
        exit 1
    fi
    DB_USER=$(echo $DB_SECRET | jq -r '.username')
    DB_PASS=$(echo $DB_SECRET | jq -r '.password')
    DB_HOST=$(echo $DB_SECRET | jq -r '.host')
    DB_NAME=$(echo $DB_SECRET | jq -r '.dbname')

    # AWS RDS requires SSL for production
    SSL_CA_PATH="/etc/ssl/certs/rds-combined-ca-bundle.pem"

    if [ ! -f "$SSL_CA_PATH" ]; then
        echo "ERROR: SSL certificate file not found at $SSL_CA_PATH"
        exit 1
    fi
    echo "OKAY: SSL certificate file found at $SSL_CA_PATH"
fi

if [ -n "$SSL_CA_PATH" ]; then
    export CONNECTION_STRING="mysql+mysqlconnector://$DB_USER:$DB_PASS@$DB_HOST:3306/$DB_NAME?ssl_ca=$SSL_CA_PATH"
else
    export CONNECTION_STRING="mysql+mysqlconnector://$DB_USER:$DB_PASS@$DB_HOST:3306/$DB_NAME"
fi

echo "CONNECTION_STRING=$CONNECTION_STRING"

export PYTHONPATH=/app
export FLASK_APP=app.app
export FLASK_ENV=$FLASK_ENV

echo "Secrets loaded successfully!"

# Start the Flask app
exec gunicorn -b 0.0.0.0:5000 "app.app:create_app()"
