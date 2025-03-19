# OpenTofu State Manager API

A FastAPI application for managing OpenTofu state files using S3-compatible storage.

## Prerequisites

- Docker
- Docker Compose

For local development:
- Python 3.13+
- Poetry (Python package manager)

## Running the Application

1. Clone the repository
2. Update the `.env` file with your secure API token
3. Run the application:

```bash
make start
```

## Authentication

Include the `X-API-Token` header in your requests:

```
X-API-Token: your-secure-api-token-here
```

## Available Make Commands

#### Docker Commands
```bash
make start          # Start all services
make build          # Build services
make rebuild        # Rebuild and start services
make stop           # Stop services
make run-app        # Run API service only
make bash           # Open a shell in the API container
make clean-docker   # Remove all containers, images, and volumes
```

#### Code & Database
```bash
make format         # Run all formatters
make check          # Run all formatters in check mode
make migrate        # Run all pending migrations
make migrate-up     # Run next pending migration
make migrate-down   # Rollback last migration
make migrate-revision message="Description"  # Create new migration revision
```

#### Local Development
```bash
make setup-local    # Setup local development environment
make local-server   # Run development server locally
make local-test     # Run tests locally
make local-check    # Run code quality checks locally
make local-format   # Format code locally
make local-clean    # Clean all useless data
make help           # Display available commands with descriptions
```

## Local Development Setup

```bash
# Set up environment
make setup-local

# Start database
docker-compose -f docker/docker-compose.yaml up -d

# Run server
source .venv/bin/activate
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

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
