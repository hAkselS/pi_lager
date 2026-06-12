#!/bin/bash

####
# Run with <source setup_venv.sh> 
####

# Check if python3 is installed
if ! command -v python3 &> /dev/null; then
    echo "❌ Error: python3 is not installed."
    return 1 2>/dev/null || exit 1
fi

# Create the virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "📦 Creating virtual environment 'venv'..."
    python3 -m venv venv
else
    echo "ℹ️ Virtual environment 'venv' already exists."
fi

# Activate the virtual environment
echo "🚀 Activating venv..."
source venv/bin/activate

# Check for requirements.txt and install it
if [ -f "requirements.txt" ]; then
    echo "📥 Upgrading pip..."
    pip install --upgrade pip
    echo "📥 Installing dependencies from requirements.txt..."
    pip install -r requirements.txt
    echo "✅ All dependencies installed successfully!"
else
    echo "⚠️ Note: requirements.txt not found. Skipping package installation."
fi