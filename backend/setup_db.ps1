# PostgreSQL Setup Script for Nexus 2.0
# Run this in PowerShell as Administrator

Write-Host "============================================" -ForegroundColor Cyan
Write-Host "    Nexus 2.0 PostgreSQL Setup" -ForegroundColor Cyan
Write-Host "============================================" -ForegroundColor Cyan

# Check if psql is available
try {
    $psqlVersion = psql --version 2>&1
    Write-Host "✅ PostgreSQL client found: $psqlVersion" -ForegroundColor Green
} catch {
    Write-Host "❌ PostgreSQL (psql) not found in PATH" -ForegroundColor Red
    Write-Host "Please install PostgreSQL or add it to PATH" -ForegroundColor Yellow
    Write-Host "Download: https://www.postgresql.org/download/windows/" -ForegroundColor Yellow
    exit 1
}

# Create database
Write-Host "`nCreating database 'nexus'..." -ForegroundColor Cyan
try {
    $env:PGPASSWORD = "postgres"
    createdb -U postgres nexus 2>&1 | Out-Null
    Write-Host "✅ Database 'nexus' created successfully" -ForegroundColor Green
} catch {
    Write-Host "⚠️  Database may already exist or connection failed" -ForegroundColor Yellow
    Write-Host "   Error: $_" -ForegroundColor Gray
}

# Verify connection
Write-Host "`nVerifying database connection..." -ForegroundColor Cyan
try {
    $result = psql -U postgres -d nexus -c "SELECT 'Database ready!' as status;" 2>&1
    if ($result -match "Database ready") {
        Write-Host "✅ Database connection verified" -ForegroundColor Green
    }
} catch {
    Write-Host "❌ Could not connect to database" -ForegroundColor Red
    Write-Host "   Make sure PostgreSQL service is running:" -ForegroundColor Yellow
    Write-Host "   net start postgresql-x64-15" -ForegroundColor Yellow
    exit 1
}

Write-Host "`n============================================" -ForegroundColor Cyan
Write-Host "    Setup Complete!" -ForegroundColor Green
Write-Host "============================================" -ForegroundColor Cyan
Write-Host "`nConnection string:" -ForegroundColor Cyan
Write-Host "  postgresql://postgres:postgres@localhost:5432/nexus" -ForegroundColor White
Write-Host "`nNext steps:" -ForegroundColor Yellow
Write-Host "  1. Ensure this is in your .env file" -ForegroundColor White
Write-Host "  2. Restart the Nexus server" -ForegroundColor White
Write-Host "  3. Run: python test_e2e.py" -ForegroundColor White
