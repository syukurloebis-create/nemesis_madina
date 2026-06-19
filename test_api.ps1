# test_api.ps1
# Script untuk testing API endpoints

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  NEMESIS MADINA API TEST" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "1. Health Check:" -ForegroundColor Yellow
curl -s http://localhost/health | ConvertFrom-Json | ConvertTo-Json
Write-Host ""

Write-Host "2. Root Endpoint:" -ForegroundColor Yellow
curl -s http://localhost/ | ConvertFrom-Json | ConvertTo-Json
Write-Host ""

Write-Host "3. List Cases:" -ForegroundColor Yellow
curl -s http://localhost/cases | ConvertFrom-Json | ConvertTo-Json
Write-Host ""

Write-Host "4. Create New Case:" -ForegroundColor Yellow
$timestamp = Get-Date -Format "yyyyMMdd_HHmmss"
$body = @{
    title = "Test Case $timestamp"
    description = "Created by PowerShell test script"
    priority = "HIGH"
} | ConvertTo-Json

curl -s -X POST http://localhost/cases/ `
    -H "Content-Type: application/json" `
    -d $body | ConvertFrom-Json | ConvertTo-Json
Write-Host ""

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  TEST COMPLETE" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan