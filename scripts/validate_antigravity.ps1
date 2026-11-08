$ErrorActionPreference = "Stop"
$Root = Split-Path -Parent $PSScriptRoot
if (-not (Get-Command agy -ErrorAction SilentlyContinue)) { throw "agy CLI not found." }
Write-Host "Validating the single AI Agent Ecosystem plugin..."
agy plugin validate $Root
if ($LASTEXITCODE -ne 0) { throw "Validation failed: $Root" }
Write-Host "The root AI Agent Ecosystem plugin passed Antigravity validation."
