#!/bin/bash
# Setup script for GitLab cleanup

echo "🔧 Setting up GitLab Cleanup Environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment and install dependencies
echo "📋 Installing dependencies..."
source venv/bin/activate
pip install requests

echo "✅ Setup complete!"
echo ""
echo "🚀 To run the cleanup script:"
echo "   source venv/bin/activate"
echo "   python3 run_cleanup.py"
echo ""
echo "⚠️  WARNING: This will delete ALL projects in tomerrab21-group!"