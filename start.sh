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

echo "🚀 Starting all services (including Prometheus & Grafana monitoring)..."
docker compose up -d

echo "⏳ Waiting for services to be ready..."
sleep 15

# Check service health
echo "🔍 Checking service health..."

# Check API
if curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "✅ API is healthy (http://localhost:8000)"
else
    echo "⚠️  API not ready yet. Check logs with: docker compose logs api"
fi

# Check PostgreSQL
if docker compose exec -T postgres pg_isready -U petuser > /dev/null 2>&1; then
    echo "✅ PostgreSQL database is ready"
else
    echo "⚠️  PostgreSQL not ready yet"
fi

# Check Redis
if docker compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo "✅ Redis cache is ready"
else
    echo "⚠️  Redis not ready yet"
fi

# Check Ollama and model
if curl -f http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo "✅ Ollama AI service is running (http://localhost:11434)"
    
    # Check if llama3.2:3b model is available
    if docker compose exec -T ollama ollama list | grep -q "llama3.2:3b"; then
        echo "✅ llama3.2:3b model is ready"
    else
        echo "📥 Downloading llama3.2:3b model (this may take 3-5 minutes for 3GB download)..."
        docker compose exec ollama ollama pull llama3.2:3b
        echo "✅ llama3.2:3b model downloaded and ready"
    fi
else
    echo "⚠️  Ollama not ready yet. Will download model when ready."
fi

# Check Prometheus (if running)
if curl -f http://localhost:9090 > /dev/null 2>&1; then
    echo "✅ Prometheus monitoring is running (http://localhost:9090)"
else
    echo "ℹ️  Prometheus monitoring not running (optional)"
fi

# Check Grafana (if running)
if curl -f http://localhost:3000 > /dev/null 2>&1; then
    echo "✅ Grafana dashboard is running (http://localhost:3000)"
else
    echo "ℹ️  Grafana dashboard not running (optional)"
fi

echo ""
echo "🎉 Pet Health API is ready!"
echo "=========================="
echo "📖 API Documentation: http://localhost:8000/docs"
echo "❤️  Health Check:     http://localhost:8000/health"
echo "� PostgreSQL:       localhost:5432 (petuser/petpass/petdb)"
echo "⚡ Redis Cache:       localhost:6379"
echo "🤖 Ollama AI:        http://localhost:11434"
echo "�📊 Grafana Dashboard: http://localhost:3000 (admin/admin) - if running"
echo "🔍 Prometheus:        http://localhost:9090 - if running"
echo ""
echo "🧪 Test the API:"
echo "curl http://localhost:8000/health"
echo "curl http://localhost:8000/docs"
echo ""
echo "🤖 Test AI functionality (requires authentication):"
echo "# Register a user first, then use the demo script:"
echo "docker compose exec api python demo_scripts/run_demo.py"
echo ""
echo "📝 View logs:"
echo "docker compose logs -f api"
echo "docker compose logs ollama"
echo ""
echo "🛑 Stop services:"
echo "docker compose down"
echo ""
echo "📈 Start with monitoring:"
echo "docker compose up -d prometheus grafana"