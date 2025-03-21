.PHONY: \
	# Docker commands
	start build rebuild stop run-app docker-run bash clean-docker \
	# Code formatting
	format black isort check check-black check-isort \
	# Local development
	setup-local local-server local-test local-check local-format \
	# Database migrations
	migrate migrate-up migrate-down migrate-revision \
	# Help
	help

PROJECT_NAME=opentofu-state-manager-api
PROJECT_CONTAINER_NAME=api
POSTGRES_CONTAINER_NAME=postgres
MINIO_CONTAINER_NAME=minio
DOCKER_COMPOSE=docker/docker-compose.yaml

# Default target
all: help

start: ## Start services
	@printf "\n=> Start services...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) up

build: ## Build services
	@printf "\n=> Build services...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) build

rebuild: ## Rebuild and start services
	@printf "\n=> Rebuild services...\n\n"
	# remove containers
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) down --remove-orphans
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) build --no-cache --force-rm
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) up -d

stop: ## Stop services
	@printf "\n=> Stop services...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) down --remove-orphans

run-app: ## Run api service
	@printf "\n=> Run api service...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) up -d $(PROJECT_CONTAINER_NAME)

bash:
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) sh

format: isort black ## Run all formatters

black: ## Format code with Black
	@printf "\n=> Formatting code with Black...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) black src tests

isort: ## Sort imports with isort
	@printf "\n=> Sorting imports with isort...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) isort src tests

check: check-black check-isort ## Run all formatters in check mode

check-black: ## Check code formatting with Black (no changes)
	@printf "\n=> Checking code formatting with Black...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) black --check src tests

check-isort: ## Check import sorting with isort (no changes)
	@printf "\n=> Checking import sorting with isort...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) isort --check src tests

clean-docker: ## Removing all: containers, images and volumes
	@printf "\n=> Removing containers and images...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) down --remove-orphans
	@docker compose -f $(DOCKER_COMPOSE) rm --stop --force -v $(PROJECT_CONTAINER_NAME)
	@docker rmi $(PROJECT_NAME) || printf=""
	@docker image prune -af
	@docker system prune --volumes

# Database migrations
migrate: ## Run all pending migrations
	@printf "\n=> Running database migrations...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) alembic upgrade head

migrate-up: ## Run next pending migration
	@printf "\n=> Running next pending migration...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) alembic upgrade +1

migrate-down: ## Rollback last migration
	@printf "\n=> Rolling back last migration...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) alembic downgrade -1

migrate-revision: ## Create new migration revision
	@printf "\n=> Creating new migration revision...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) exec $(PROJECT_CONTAINER_NAME) alembic revision --autogenerate -m "$(message)"

# Local development commands
local-setup: ## Setup local development environment
	@printf "\n=> Setting up local development environment...\n\n"
	@chmod +x scripts/setup_local.sh
	@./scripts/setup_local.sh

local-start: ## Start development server locally
	@printf "\n=> Starting development server...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) up -d $(POSTGRES_CONTAINER_NAME) $(MINIO_CONTAINER_NAME)
	@source .venv/bin/activate && uvicorn src.main:app --reload --host 0.0.0.0 --port 8000

local-test: ## Run tests locally
	@printf "\n=> Running tests locally...\n\n"
	@docker compose -f $(DOCKER_COMPOSE) -p $(PROJECT_NAME) up -d $(POSTGRES_CONTAINER_NAME) $(MINIO_CONTAINER_NAME)
	@source .venv/bin/activate && pytest

local-check: ## Run code quality checks locally
	@printf "\n=> Running code quality checks locally...\n\n"
	@source .venv/bin/activate && black --check src tests
	@source .venv/bin/activate && isort --check src tests
	@source .venv/bin/activate && flake8 src tests
	@source .venv/bin/activate && mypy src

local-format: ## Format code locally
	@printf "\n=> Formatting code locally...\n\n"
	@source .venv/bin/activate && black src tests
	@source .venv/bin/activate && isort src tests

local-clean: ## Clean all useless data
	rm -rf `find . -name __pycache__`
	rm -f `find . -type f -name '*.py[co]' `
	rm -f `find . -type f -name '*~' `
	rm -f `find . -type f -name '.*~' `
	rm -f `find . -type f -name '@*' `
	rm -f `find . -type f -name '#*#' `
	rm -f `find . -type f -name '*.orig' `
	rm -f `find . -type f -name '*.rej' `
	rm -f .coverage
	rm -rf htmlcov
	rm -rf docs/_build/
	rm -rf coverage.xml
	rm -rf dist

help:
	@egrep -h '\s##\s' $(MAKEFILE_LIST) \
	| awk 'BEGIN {FS = ":.*?## "}; {printf "\033[36m  %-30s\033[0m %s\n", $$1, $$2}'
