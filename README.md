# OpenTofu State Manager API

A FastAPI application for managing OpenTofu state files using S3-compatible storage.

## Prerequisites

- Docker
- Docker Compose

For local development:
- Python 3.13+
- Poetry (Python package manager)

## Quick Start with Docker Compose

1. Clone the repository
2. Update the `.env` file with your secure API token
3. Start all services:
```bash
make start
```

The API will be available at `http://localhost:8080`

## Authentication

Include the `X-API-Token` header in your requests:

```
X-API-Token: your-secure-api-token-here
```

## Available Make Commands

### Docker Commands
```bash
make start          # Start all services
make build          # Build services
make rebuild        # Rebuild and start services
make stop           # Stop services
make run-app        # Run API service only
make bash           # Open a shell in the API container
make clean-docker   # Remove all containers, images, and volumes
```

### Code Formatting
```bash
make format         # Run all formatters (isort and black)
make black          # Format code with Black
make isort          # Sort imports with isort
make check          # Run all formatters in check mode
make check-black    # Check code formatting with Black
make check-isort    # Check import sorting with isort
```

### Database Migrations
```bash
make migrate        # Run all pending migrations
make migrate-up     # Run next pending migration
make migrate-down   # Rollback last migration
make migrate-revision message="Description"  # Create new migration revision
```

### Local Development
```bash
make local-setup    # Setup local development environment
make local-start    # Run development server locally with required services
make local-test     # Run tests locally with required services
make local-check    # Run code quality checks locally
make local-format   # Format code locally
make local-clean    # Clean all useless data
make help          # Display available commands with descriptions
```

## Local Development Setup

1. Clone the repository
2. Set up the local environment:
```bash
make local-setup
```
3. Update the `.env` file with your secure API token
4. Start the development server with required services (PostgreSQL and MinIO):
```bash
make local-start
```

The API will be available at `http://localhost:8000`

## Running Tests

To run tests locally (automatically starts required services):
```bash
make local-test
```

## API Documentation

When running, access documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## OpenTofu Configuration

Add to your OpenTofu configuration:

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
