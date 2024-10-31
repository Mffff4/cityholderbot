@echo off
setlocal enabledelayedexpansion

echo Checking Docker installation...
where docker >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker is not installed! Please install Docker Desktop first.
    echo Download from: https://www.docker.com/products/docker-desktop
    pause
    exit /b 1
)

echo Checking if Docker service is running...
docker info >nul 2>nul
if %errorlevel% neq 0 (
    echo Docker service is not running! Please start Docker Desktop.
    echo If Docker Desktop is not started, please launch it and wait until it's ready.
    pause
    exit /b 1
)

echo Docker is installed and running!
echo.

echo Checking for updates...
git pull
if %errorlevel% neq 0 (
    echo Failed to pull updates. Please check your internet connection.
    pause
    exit /b 1
)

echo.
echo Checking if .env file exists...
if not exist .env (
    if exist .env-example (
        echo Creating .env file from .env-example...
        copy .env-example .env
        echo Please edit .env file and add your API_ID and API_HASH
        notepad .env
    ) else (
        echo Neither .env nor .env-example found!
        echo Please create .env file with your configuration
        pause
        exit /b 1
    )
)

echo.
echo Starting Docker containers...
docker compose up -d --build

if %errorlevel% neq 0 (
    echo Failed to start Docker containers.
    pause
    exit /b 1
)

echo.
echo Successfully started! To view logs, type 'docker compose logs -f'
echo To stop the bot, type 'docker compose down'
echo.
echo Press any key to view logs...
pause >nul

docker compose logs -f

endlocal 