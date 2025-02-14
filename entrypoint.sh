#!/bin/bash
set -e # Exit on error

echo "Fetching secrets from AWS SSM Parameter Store..."

#DB_SECRET=$(aws secretsmanager get-secret-value --secret-id /copilot/ctime/prod/secrets/aurora-db --query 'SecretString' --output text)
#SECRET_KEY=$(aws ssm get-parameter --name /copilot/ctime/prod/secrets/SECRET_KEY --with-decryption --query "Parameter.Value" --output text)
#SENTRY_DSN=$(aws ssm get-parameter --name /copilot/ctime/prod/secrets/SENTRY_DSN --with-decryption --query "Parameter.Value" --output text)
#SENTRY_SEND_PII=$(aws ssm get-parameter --name /copilot/ctime/prod/secrets/SENTRY_SEND_PII --with-decryption --query "Parameter.Value" --output text)
#SENTRY_TRACE_SAMPLE_RATE=$(aws ssm get-parameter --name /copilot/ctime/prod/secrets/SENTRY_TRACE_SAMPLE_RATE --with-decryption --query "Parameter.Value" --output text)
#SENTRY_PROFILE_SAMPLE_RATE=$(aws ssm get-parameter --name /copilot/ctime/prod/secrets/SENTRY_PROFILE_SAMPLE_RATE --with-decryption --query "Parameter.Value" --output text)

# Export secrets as environment variables
#export DB_SECRET="$DB_SECRET"
#export SECRET_KEY="$SECRET_KEY"
#export SENTRY_DSN="$SENTRY_DSN"
#export SENTRY_SEND_PII="$SENTRY_SEND_PII"
#export SENTRY_TRACE_SAMPLE_RATE="$SENTRY_TRACE_SAMPLE_RATE"
#export SENTRY_PROFILE_SAMPLE_RATE="$SENTRY_PROFILE_SAMPLE_RATE"

# Parse the DB_SECRET JSON and set CONNECTION_STRING
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

export CONNECTION_STRING="mysql+pymysql://$DB_USER:$DB_PASS@$DB_HOST:3306/$DB_NAME?ssl_ca=$SSL_CA_PATH"

export PYTHONPATH=/app
export FLASK_APP=app.app
export FLASK_ENV=production

echo "Secrets loaded successfully!"

# Start the Flask app
exec gunicorn -b 0.0.0.0:5000 "app.app:create_app()"
