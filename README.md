# OpenTofu State Manager API

A FastAPI application with basic health check endpoints.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone the repository
2. Update the `.env` file with your secure API token
3. Run the application using Docker Compose:

```bash
make start
```

### Authentication

The API uses token-based authentication. To access protected endpoints, include the `X-API-Token` header in your requests:

```
X-API-Token: your-secure-api-token-here
```

The token value must match the `API_TOKEN` set in your environment variables.

### Development

To build the application:

```bash
make build
```

To rebuild the application:

```bash
make rebuild
```

To stop the application:

```bash
make stop
```

## Local Development Setup

### Prerequisites
- Python 3.13+
- Poetry (Python package manager)
- Docker and Docker Compose (for running PostgreSQL)

### Setup Instructions

1. Clone the repository:
```bash
git clone <repository-url>
cd opentofu-state-manager-api
```

2. Make the setup script executable and run it:
```bash
chmod +x scripts/setup_local.sh
./scripts/setup_local.sh
```

3. Start the PostgreSQL database using Docker Compose:
```bash
docker-compose -f docker/docker-compose.yaml up -d
```

4. Activate the virtual environment:
```bash
source .venv/bin/activate
```

5. Run the development server:
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

### Development Workflow

- The virtual environment is automatically created and activated by the setup script
- Dependencies are managed using Poetry
- Environment variables can be configured in the `.env` file
- The development server supports hot-reload for automatic updates

### Running Tests

```bash
pytest
```

### Code Quality

The project uses several tools to maintain code quality:
- Black for code formatting
- isort for import sorting

You can run these tools using:
```bash
black .
isort .
```

## API Documentation

Once the application is running, you can access the API documentation at:

- Swagger UI: http://localhost:8080/api/docs
- ReDoc: http://localhost:8080/api/redoc

## API Endpoints

### Health and Status

- `GET /api/health` - Health check endpoint for service availability monitoring
- `GET /api/info` - Detailed information about the application and its environment

For complete API documentation including request and response schemas, refer to the Swagger UI or ReDoc documentation.

## OpenTofu State Manager API

This API allows you to store and retrieve OpenTofu state files using S3-compatible storage (MinIO) with aiobotocore.

### Configuration

To use this API with OpenTofu, add the following to your OpenTofu configuration:

```hcl
terraform {
  backend "http" {
    address = "http://localhost:8080/api/states/state_identifier"
    lock_address = "http://localhost:8080/api/states/state_identifier/lock"
    unlock_address = "http://localhost:8080/api/states/state_identifier/unlock"
    headers = {
      X-API-Token = "your-secure-api-token-here"
    }
  }
}
```

### API Endpoints

- `GET /api/states/state_identifier` - Retrieve state
- `POST /api/states/state_identifier` - Store state
- `LOCK /api/states/state_identifier/lock` - Lock state
- `UNLOCK /api/states/state_identifier/unlock` - Unlock state

These endpoints are designed to be compatible with OpenTofu's HTTP backend.

## License

This project is licensed under the terms of the license included in the repository.
