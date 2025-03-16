#!/bin/bash

# Exit on error
set -e

# Create virtual environment if it doesn't exist
if [ ! -d ".venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv .venv
fi

# Activate virtual environment
source .venv/bin/activate

# Install Poetry in the virtual environment
echo "Installing Poetry in virtual environment..."
pip install poetry

# Install dependencies using Poetry without installing the package
echo "Installing dependencies..."
poetry install --no-root

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "Creating .env file..."
    cp .env.example .env
    echo "Please update .env with your configuration"
fi

echo "Development environment setup complete!"
echo "To activate the virtual environment, run: source .venv/bin/activate" 
