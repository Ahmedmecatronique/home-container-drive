#!/bin/bash

# Mini-Cloud Storage Setup Script

set -e

echo "🚀 Mini-Cloud Storage Setup"
echo "============================"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    echo "Visit: https://docs.docker.com/get-docker/"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose first."
    echo "Visit: https://docs.docker.com/compose/install/"
    exit 1
fi

echo "✓ Docker found: $(docker --version)"
echo "✓ Docker Compose found: $(docker-compose --version)"
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and set your credentials!"
    echo "   Especially change API_USERNAME and API_PASSWORD"
    echo ""
fi

# Create storage directory
mkdir -p storage

echo "Starting Mini-Cloud Storage..."
docker-compose up -d

echo ""
echo "✅ Mini-Cloud Storage is running!"
echo ""
echo "🌐 Access the web interface at: http://localhost:8000"
echo "📚 API documentation at: http://localhost:8000/docs"
echo ""
echo "Default credentials:"
echo "  Username: admin"
echo "  Password: admin"
echo ""
echo "⚠️  Don't forget to change the default password in .env!"
echo ""
echo "Useful commands:"
echo "  docker-compose logs -f     # View logs"
echo "  docker-compose stop        # Stop the service"
echo "  docker-compose down        # Stop and remove containers"
echo "  docker-compose restart     # Restart the service"
