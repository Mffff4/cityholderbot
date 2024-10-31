#!/bin/bash

# Make script executable
chmod +x runDocker.sh

# Text colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
echo -e "${YELLOW}Checking Docker installation...${NC}"
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Docker is not installed!${NC}"
    echo "Please install Docker first:"
    echo "- For Ubuntu: sudo apt install docker.io"
    echo "- For macOS: Install Docker Desktop from https://www.docker.com/products/docker-desktop"
    exit 1
fi

# Check if Docker service is running
echo -e "${YELLOW}Checking if Docker service is running...${NC}"
if ! docker info &> /dev/null; then
    echo -e "${RED}Docker service is not running!${NC}"
    echo "Please start Docker service:"
    echo "- For Linux: sudo systemctl start docker"
    echo "- For macOS: Start Docker Desktop application"
    exit 1
fi

echo -e "${GREEN}Docker is installed and running!${NC}"
echo

# Check for updates
echo -e "${YELLOW}Checking for updates...${NC}"
if ! git pull; then
    echo -e "${RED}Failed to pull updates. Please check your internet connection.${NC}"
    exit 1
fi

echo
# Check if .env exists
echo -e "${YELLOW}Checking if .env file exists...${NC}"
if [ ! -f .env ]; then
    if [ -f .env-example ]; then
        echo "Creating .env file from .env-example..."
        cp .env-example .env
        echo "Please edit .env file and add your API_ID and API_HASH"
        if command -v nano &> /dev/null; then
            nano .env
        elif command -v vim &> /dev/null; then
            vim .env
        else
            echo -e "${RED}Please edit .env file manually${NC}"
        fi
    else
        echo -e "${RED}Neither .env nor .env-example found!${NC}"
        echo "Please create .env file with your configuration"
        exit 1
    fi
fi

echo
# Start Docker containers
echo -e "${YELLOW}Starting Docker containers...${NC}"
if ! docker compose up -d --build; then
    echo -e "${RED}Failed to start Docker containers.${NC}"
    exit 1
fi

echo
echo -e "${GREEN}Successfully started!${NC}"
echo "To view logs, type 'docker compose logs -f'"
echo "To stop the bot, type 'docker compose down'"
echo
echo -e "${YELLOW}Showing logs...${NC}"
echo "Press Ctrl+C to exit logs (bot will continue running)"
echo
sleep 2
docker compose logs -f 