# ctime

## Overview

ctime is a scheduling and availability management application designed to help organizations streamline time-off requests, user schedules, and administrative approvals.

## Features

### Users

- [x] Create schedule/availability
- [x] Request days off
- [x] Allow for comments/brief descriptions of why
- [ ] Pending: Admin-controlled approval rules (blockout dates, notice periods, etc.)
- [x] Edit profile
- [x] Dashboard with:
- [x] Next shift info
- [x] Requested days off status
- [x] Full schedule view

### Admins

- [x] Create schedules for users
- [x] Approve/Reject time-off requests
- [x] Edit user profiles
- [x] Full schedule view

### Security

- [x] Password validation & strength enforcement
- [x] Rate limiting for registration
- [ ] Email verification (Planned)
- [ ] CAPTCHA for bot protection (Planned)

### Deployment & Infrastructure

- [x] Dockerized for local development
- [x] AWS Copilot deployment (Fargate + Aurora)
- [x] SSL-secured MySQL connections
- [x] CI/CD pipeline with GitHub Actions
- [x] Sentry integration for monitoring and error tracking

## Deployment

### Option 1: Running Locally (Docker)

1. Copy `.env.example` to `.env` and populate the necessary values.
2. Build the containers: `docker compose build`
3. Start the containers: `docker compose up`
4. The app should now be running on <http://localhost:5000>.

### Option 2: AWS Copilot Deployment Guide

This guide walks through deploying ctime using AWS Copilot CLI.

#### 1. Initial Setup

Run the following commands to initialize the AWS Copilot project:

```bash
git clone https://github.com/soarn/ctime.git
cd ctime
copilot init
ctime # What would you like to name the application?
"Load Balanced Web Service" # What type of service would you like?
ctime # What would you like to name this service?
./Dockerfile # Would you like to use an existing Dockerfile or create another?
y # Would you like to deploy an environment?
prod # What is your environment's name?
```

Note: The application will attempt to deploy automatically but will fail because secrets are not yet stored in AWS Parameter Store.

#### 2. Set Secrets

We need to store secrets in AWS Parameter Store:

```bash
copilot secret init
SECRET_KEY # Secret name
<random string to be used as your Flask secret key> # Prod secret value

copilot secret init
FLASK_ENV # Secret name
production # Prod secret value
```

#### 3. Set Up Storage

To set up an Aurora Serverless v2 database, run:

```bash
copilot storage init
"Aurora Serverless (SQL)" # Storage type
<enter name or press Enter to accept the default> # Storage resource name
"No, the storage should be created and deleted at the environment level" # Lifecycle
MySQL # Database engine
db # Initial database name
```

After running this command, follow the recommended follow-up actions:

1. Deploy the storage resources:
  
    `copilot env deploy`

2. Update the environment manifest:

    ```yaml
    network:
      vpc:
        security_groups:
          - from_cfn: ${COPILOT_APPLICATION_NAME}-${COPILOT_ENVIRONMENT_NAME}-ctimeSecurityGroup
    secrets:
      DB_SECRET:
        from_cfn: ${COPILOT_APPLICATION_NAME}-${COPILOT_ENVIRONMENT_NAME}-ctimeAuroraSecret
    ```

#### 4. Set Up Health Check & Secrets in Service Manifest

Edit the app manifest to include the health check and secrets:

1. Retrieve the ARN of Your Aurora Secret

    - Run the following command

      ```bash
      aws secretsmanager list-secrets --query "SecretList[?Name | contains(@, 'Aurora')].{Name:Name, ARN:ARN}" | awk 'BEGIN{ FS=OFS="\t" }{ print $1 }'
      ```

    - Copy the ARN for your Aurora DB_SECRET and use it in your manifest.

2. Add Health Check & Secrets

    ```yaml
    http:
      path: '/'
      healthcheck: '/health'

    secrets:
      DB_SECRET: <your auroraSecret ARN here>
      SECRET_KEY: /copilot/ctime/prod/secrets/SECRET_KEY
      FLASK_ENV: /copilot/ctime/prod/secrets/FLASK_ENV
    ```

#### 5. Deploy Your Service

Now, deploy your service:

```bash
copilot svc deploy --name ctime-east-alb
```

### Option 3: Local Development

To run locally without Docker:

```bash
pip install -r requirements.txt
export FLASK_ENV=development
flask run
```

Then open <http://localhost:5000> in your browser.

## Resources

- [AWS Copilot Docs](https://aws.github.io/copilot-cli/)
- [Bootstrap](https://getbootstrap./com)

## License

MIT License. See [LICENSE](/LICENSE) for details.
