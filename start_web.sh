#!/bin/bash

# Startup script for Lab Asset Manager Web Interface

echo "Starting Lab Asset Manager Web Interface..."

# Navigate to the web directory
cd "$(dirname "$0")/web"

# Check if Node.js is installed
if ! command -v node &> /dev/null; then
    echo "Error: Node.js is not installed. Please install Node.js first."
    exit 1
fi

# Check if npm is installed
if ! command -v npm &> /dev/null; then
    echo "Error: npm is not installed. Please install npm first."
    exit 1
fi

# Check if server dependencies are installed
if [ ! -d "node_modules" ]; then
    echo "Installing server dependencies..."
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install server dependencies."
        exit 1
    fi
fi

# Check if client dependencies are installed
if [ ! -d "client/node_modules" ]; then
    echo "Installing client dependencies..."
    cd client
    npm install
    if [ $? -ne 0 ]; then
        echo "Error: Failed to install client dependencies."
        exit 1
    fi
    cd ..
fi

# Check if client build exists, if not, build it
if [ ! -d "client/dist" ]; then
    echo "Building client..."
    cd client
    npm run build
    if [ $? -ne 0 ]; then
        echo "Error: Failed to build client."
        exit 1
    fi
    cd ..
fi

# Start the server
echo "Starting server..."
echo "The web interface will be available at http://localhost:3000"
echo "Press Ctrl+C to stop the server."
npm start