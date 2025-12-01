#!/bin/bash

# Pet Health API - Quick Start Script
# This script sets up the complete development environment

set -e

echo "🐾 Pet Health API - Starting Development Environment"
echo "=================================================="

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

echo "✅ Docker is running"

# Check if docker-compose.yml exists
if [ ! -f "docker-compose.yml" ]; then
    echo "❌ docker-compose.yml not found. Please run this script from the project root."
    exit 1
fi

echo "🚀 Starting all services..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 10

# Check service health
echo "🔍 Checking service health..."

# Check API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy (http://localhost:8000)"
else
    echo "⚠️  API not ready yet. Check logs with: docker-compose logs api"
fi

# Check Ollama
if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama AI service is running (http://localhost:11434)"
    
    # Check if model is available
    if docker compose exec -T ollama ollama list | grep -q "llama3.1"; then
        echo "✅ Llama 3.1 model is ready"
    else
        echo "📥 Downloading Llama 3.1 model (this may take a few minutes)..."
        docker compose exec ollama ollama pull llama3.1:latest
        echo "✅ Llama 3.1 model downloaded and ready"
    fi
else
    echo "⚠️  Ollama not ready yet. Will download model when ready."
fi

echo ""
echo "🎉 Pet Health API is ready!"
echo "=========================="
echo "📖 API Documentation: http://localhost:8000/docs"
echo "❤️  Health Check:     http://localhost:8000/health"
echo "📊 Grafana Dashboard: http://localhost:3000 (admin/admin)"
echo "🔍 Prometheus:        http://localhost:9090"
echo ""
echo "🧪 Test the API:"
echo "curl http://localhost:8000/health"
echo ""
echo "📝 View logs:"
echo "docker compose logs -f api"
echo ""
echo "🛑 Stop services:"
echo "docker compose down"