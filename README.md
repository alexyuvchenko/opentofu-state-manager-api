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
