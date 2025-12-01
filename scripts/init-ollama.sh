#!/bin/bash

# Ollama Model Initialization Script
# This script pulls the required AI model for veterinary symptom analysis

set -e

echo "🤖 Initializing Ollama AI Model for Pet Health Assistant..."

# Wait for Ollama service to be ready
echo "⏳ Waiting for Ollama service..."
while ! curl -s http://localhost:11434/api/tags > /dev/null; do
    echo "   Waiting for Ollama to start..."
    sleep 5
done

echo "✅ Ollama service is ready!"

# Check if model is already installed
echo "📋 Checking for existing models..."
MODELS=$(curl -s http://localhost:11434/api/tags | jq -r '.models[].name' 2>/dev/null || echo "")

if echo "$MODELS" | grep -q "llama3.2:3b"; then
    echo "✅ Model llama3.2:3b is already installed!"
else
    echo "📥 Pulling llama3.2:3b model (this may take several minutes)..."
    curl -X POST http://localhost:11434/api/pull \
         -H "Content-Type: application/json" \
         -d '{"name": "llama3.2:3b"}' \
         --no-buffer
    echo
    echo "✅ Model llama3.2:3b successfully installed!"
fi

# Test the model with a simple veterinary prompt
echo "🧪 Testing AI model with sample veterinary prompt..."
TEST_RESPONSE=$(curl -s -X POST http://localhost:11434/api/generate \
    -H "Content-Type: application/json" \
    -d '{
        "model": "llama3.2:3b",
        "prompt": "You are a veterinary assistant. A dog is showing lethargy and loss of appetite. Respond with JSON: {\"urgency_level\": \"medium\", \"analysis\": \"test\", \"recommendations\": \"test\"}",
        "stream": false,
        "options": {"temperature": 0.3, "num_predict": 100}
    }' | jq -r '.response' 2>/dev/null || echo "Error testing model")

if [[ "$TEST_RESPONSE" != "Error testing model" ]] && [[ -n "$TEST_RESPONSE" ]]; then
    echo "✅ AI model test successful!"
    echo "   Sample response: ${TEST_RESPONSE:0:100}..."
else
    echo "⚠️  AI model test failed, but model is installed"
fi

echo
echo "🎉 Ollama setup complete!"
echo "   Available models:"
curl -s http://localhost:11434/api/tags | jq -r '.models[]?.name' 2>/dev/null | sed 's/^/   - /' || echo "   - llama3.2:3b (expected)"
echo
echo "💡 The Pet Health API can now use AI-powered symptom analysis!"