#!/bin/bash

# Multi-Database Agent Setup Script
# This script sets up the development environment for the multi-database agent

set -e

echo "🚀 Setting up Multi-Database Agent..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python 3.13+ is installed
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
        if [[ $(echo "$PYTHON_VERSION >= 3.13" | bc -l) -eq 1 ]]; then
            print_success "Python $PYTHON_VERSION is installed"
        else
            print_error "Python 3.13+ is required. Found: $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 is not installed"
        exit 1
    fi
}

# Check if Node.js is installed
check_nodejs() {
    print_status "Checking Node.js version..."
    if command -v node &> /dev/null; then
        NODE_VERSION=$(node --version | cut -d'v' -f2)
        if [[ $(echo "$NODE_VERSION >= 18.0" | bc -l) -eq 1 ]]; then
            print_success "Node.js $NODE_VERSION is installed"
        else
            print_error "Node.js 18+ is required. Found: $NODE_VERSION"
            exit 1
        fi
    else
        print_error "Node.js is not installed"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install uv if not present (for faster dependency management)
    if ! command -v uv &> /dev/null; then
        print_status "Installing uv for faster dependency management..."
        pip install uv
    fi
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    if [ ! -f ".env" ]; then
        if [ -f "example.env" ]; then
            cp example.env .env
            print_success "Environment file created from example.env"
            print_warning "Please edit .env file with your actual configuration"
        else
            print_error "example.env not found"
            exit 1
        fi
    else
        print_warning "Environment file already exists"
    fi
}

# Create necessary directories
create_directories() {
    print_status "Creating necessary directories..."
    mkdir -p logs
    mkdir -p data
    mkdir -p ssl
    print_success "Directories created"
}

# Install Oracle Instant Client (Linux only)
install_oracle_client() {
    if [[ "$OSTYPE" == "linux-gnu"* ]]; then
        print_status "Checking Oracle Instant Client..."
        if [ ! -d "/opt/oracle/instantclient_21_1" ]; then
            print_warning "Oracle Instant Client not found"
            print_status "To install Oracle Instant Client:"
            echo "1. Download from: https://www.oracle.com/database/technologies/instant-client/linux-x86-64-downloads.html"
            echo "2. Extract to /opt/oracle/"
            echo "3. Run: sudo ldconfig"
        else
            print_success "Oracle Instant Client found"
        fi
    else
        print_warning "Oracle Instant Client setup not supported on this OS"
    fi
}

# Test database connections
test_connections() {
    print_status "Testing database connections..."
    source venv/bin/activate
    
    # Test MongoDB connection
    if [ -n "$MDB_MCP_CONNECTION_STRING" ]; then
        print_status "Testing MongoDB connection..."
        python -c "
import os
from dotenv import load_dotenv
load_dotenv()
try:
    import pymongo
    client = pymongo.MongoClient(os.getenv('MDB_MCP_CONNECTION_STRING'))
    client.admin.command('ping')
    print('✅ MongoDB connection successful')
except Exception as e:
    print(f'❌ MongoDB connection failed: {e}')
"
    else
        print_warning "MongoDB connection string not configured"
    fi
    
    # Test Oracle connection
    if [ -n "$ORACLE_MCP_CONNECTION_STRING" ]; then
        print_status "Testing Oracle connection..."
        python -c "
import os
from dotenv import load_dotenv
load_dotenv()
try:
    import oracledb
    conn = oracledb.connect(os.getenv('ORACLE_MCP_CONNECTION_STRING'))
    conn.close()
    print('✅ Oracle connection successful')
except Exception as e:
    print(f'❌ Oracle connection failed: {e}')
"
    else
        print_warning "Oracle connection string not configured"
    fi
}

# Main setup function
main() {
    echo "=========================================="
    echo "Multi-Database Agent Setup"
    echo "=========================================="
    
    # Load environment variables
    if [ -f ".env" ]; then
        source .env
    fi
    
    # Run setup steps
    check_python
    check_nodejs
    create_venv
    install_dependencies
    setup_env
    create_directories
    install_oracle_client
    
    echo ""
    echo "=========================================="
    print_success "Setup completed successfully!"
    echo "=========================================="
    echo ""
    echo "Next steps:"
    echo "1. Edit .env file with your database connection strings"
    echo "2. Run: source venv/bin/activate"
    echo "3. Test connections: python scripts/test_connections.py"
    echo "4. Start the agent: adk web"
    echo "5. Or start the API server: python api_server.py"
    echo "6. Or start the web UI: streamlit run chat_ui.py"
    echo ""
    echo "For more information, see README.md"
}

# Run main function
main "$@"
