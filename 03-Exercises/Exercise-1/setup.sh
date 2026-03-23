#!/bin/bash
# Setup script for Exercise 1

echo "🚀 Setting up Exercise 1 environment..."
echo ""

# Check if running from correct directory
if [ ! -f "agent.py" ]; then
    echo "❌ Error: Please run this script from the Exercise-1 directory"
    exit 1
fi

# Activate venv
source /sessions/sleepy-clever-brown/mnt/CCA/venv/bin/activate
echo "✅ Virtual environment activated"

# Install dependencies
pip install -q anthropic
echo "✅ Anthropic SDK installed"

echo ""
echo "📝 IMPORTANT: Set your API key before running the agent"
echo ""
echo "Option 1: Export environment variable"
echo '  export ANTHROPIC_API_KEY="sk-ant-..."'
echo ""
echo "Option 2: Pass directly to Python"
echo "  ANTHROPIC_API_KEY=sk-ant-... python agent.py"
echo ""
echo "Option 3: Edit agent.py and set:"
echo '  client = anthropic.Anthropic(api_key="sk-ant-...")'
echo ""
echo "Once API key is set, run:"
echo "  python agent.py"
