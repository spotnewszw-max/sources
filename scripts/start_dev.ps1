# Start Development Server for News Aggregator
# This script runs the FastAPI development server

$projectRoot = Split-Path -Parent $MyInvocation.MyCommand.Path | Split-Path -Parent

Write-Host "🚀 Starting News Aggregator Development Server..." -ForegroundColor Green
Write-Host "Project Root: $projectRoot" -ForegroundColor Cyan

# Change to project directory
Set-Location $projectRoot

# Activate virtual environment
Write-Host "📦 Activating virtual environment..." -ForegroundColor Yellow
& ".\venv\Scripts\Activate.ps1"

# Load environment
Write-Host "⚙️  Loading development environment..." -ForegroundColor Yellow
if (Test-Path ".\.env.development") {
    Write-Host "✅ Found .env.development file" -ForegroundColor Green
    $envContent = Get-Content ".\.env.development"
    foreach ($line in $envContent) {
        if ($line -and !$line.StartsWith("#")) {
            $parts = $line.Split("=", 2)
            if ($parts.Count -eq 2) {
                [Environment]::SetEnvironmentVariable($parts[0].Trim(), $parts[1].Trim())
            }
        }
    }
} elseif (Test-Path ".\.env") {
    Write-Host "✅ Found .env file" -ForegroundColor Green
} else {
    Write-Host "⚠️  No .env or .env.development file found!" -ForegroundColor Yellow
    Write-Host "Creating .env from .env.development..." -ForegroundColor Yellow
    if (Test-Path ".\.env.development") {
        Copy-Item ".\.env.development" ".\.env" -Force
    }
}

# Copy env file to main directory if it doesn't exist
if (!(Test-Path ".\.env")) {
    Write-Host "Creating .env file..." -ForegroundColor Yellow
    Copy-Item ".\.env.development" ".\.env" -Force -ErrorAction SilentlyContinue
}

# Check if database exists, if not initialize
Write-Host "🗄️  Checking database..." -ForegroundColor Yellow
if (!(Test-Path ".\news_aggregator.db")) {
    Write-Host "Database not found. Initializing..." -ForegroundColor Cyan
    python "scripts/init_db.py"
    if ($LASTEXITCODE -eq 0) {
        Write-Host "✅ Database initialized" -ForegroundColor Green
    } else {
        Write-Host "⚠️  Database initialization had issues, continuing anyway..." -ForegroundColor Yellow
    }
}

# Start the server
Write-Host "`n✨ Starting uvicorn server on http://localhost:8000" -ForegroundColor Green
Write-Host "📖 API Documentation: http://localhost:8000/docs" -ForegroundColor Green
Write-Host "📘 Alternative Docs: http://localhost:8000/redoc" -ForegroundColor Green
Write-Host "Press Ctrl+C to stop the server`n" -ForegroundColor Yellow

uvicorn main:app --reload --host 0.0.0.0 --port 8000