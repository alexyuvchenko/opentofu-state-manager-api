# OpenTofu State Manager API

A FastAPI application with basic health check endpoints.

## Getting Started

### Prerequisites

- Docker
- Docker Compose

### Running the Application

1. Clone the repository
2. Run the application using Docker Compose:

```bash
make start
```

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

## License

This project is licensed under the terms of the license included in the repository.
