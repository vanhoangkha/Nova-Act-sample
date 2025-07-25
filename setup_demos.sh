#!/bin/bash

# Nova Act Demo Setup Script
# ==========================

echo "🚀 Nova Act Demo Setup"
echo "======================"

# Check if Python is available
if ! command -v python3 &> /dev/null; then
    echo "❌ Python 3 is required but not installed"
    exit 1
fi

echo "✅ Python 3 found: $(python3 --version)"

# Check if pip is available
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 is required but not installed"
    exit 1
fi

echo "✅ pip3 found"

# Install requirements
echo "📦 Installing demo requirements..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Requirements installed successfully"
else
    echo "❌ Failed to install requirements"
    exit 1
fi

# Install Google Chrome (optional)
echo "🌐 Checking for Google Chrome..."
if command -v google-chrome &> /dev/null; then
    echo "✅ Google Chrome found"
else
    echo "⚠️ Google Chrome not found"
    echo "📥 Installing Chrome via Playwright..."
    playwright install chrome
    
    if [ $? -eq 0 ]; then
        echo "✅ Chrome installed successfully"
    else
        echo "⚠️ Chrome installation failed, but demos can still run with Chromium"
    fi
fi

# Create necessary directories
echo "📁 Creating demo directories..."
mkdir -p demo/logs
mkdir -p demo/results
mkdir -p demo/downloads
mkdir -p demo/saved_content
mkdir -p demo/sample_files
mkdir -p demo/user_data

echo "✅ Directories created"

# Check for API key
echo "🔑 Checking Nova Act API key..."
if [ -z "$NOVA_ACT_API_KEY" ]; then
    echo "⚠️ NOVA_ACT_API_KEY environment variable not set"
    echo "📝 Please set your API key:"
    echo "   export NOVA_ACT_API_KEY='your_api_key_here'"
    echo ""
    echo "🌐 Get your API key from: https://nova.amazon.com/act"
else
    echo "✅ API key found"
fi

# Make demo scripts executable
echo "🔧 Making demo scripts executable..."
chmod +x *.py
chmod +x run_all_demos.py

echo ""
echo "🎉 Setup completed successfully!"
echo ""
echo "📋 Available demos:"
echo "   01_basic_ecommerce.py      - Basic e-commerce operations"
echo "   02_information_extraction.py - Data extraction with schemas"
echo "   03_parallel_processing.py  - Parallel browser sessions"
echo "   04_authentication_demo.py  - Login and session management"
echo "   05_file_operations.py      - File upload/download"
echo "   06_form_filling.py         - Form automation"
echo "   07_search_filter.py        - Search and filtering"
echo "   08_real_estate.py          - Real estate analysis"
echo "   09_interactive_demo.py     - Interactive mode usage"
echo "   10_advanced_features.py    - Advanced features"
echo ""
echo "🚀 To run a specific demo:"
echo "   python3 01_basic_ecommerce.py"
echo ""
echo "🎯 To run all demos:"
echo "   python3 run_all_demos.py"
echo ""
echo "📚 For more information, see README.md"
