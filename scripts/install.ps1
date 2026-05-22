# hookglot installation helper for Windows (PowerShell)
# This is for users who clone the repo on Windows.
# After running this, use `hookglot install` for interactive setup.

$ErrorActionPreference = "Stop"

$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Definition
$RepoRoot = Split-Path -Parent $ScriptDir

Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host "  🌐 hookglot installation (Windows)" -ForegroundColor Cyan
Write-Host "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━" -ForegroundColor Cyan
Write-Host ""

# Check Python
$pythonCmd = $null
foreach ($cmd in @("python", "python3", "py")) {
    if (Get-Command $cmd -ErrorAction SilentlyContinue) {
        $pythonCmd = $cmd
        break
    }
}

if (-not $pythonCmd) {
    Write-Host "❌ Python not found. Install Python 3.10+ from https://python.org" -ForegroundColor Red
    exit 1
}

$pyVersion = & $pythonCmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')"
Write-Host "✅ Python $pyVersion found ($pythonCmd)" -ForegroundColor Green

# Check pip
& $pythonCmd -m pip --version | Out-Null
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ pip not found. Install pip first." -ForegroundColor Red
    exit 1
}
Write-Host "✅ pip found" -ForegroundColor Green

# Install package
Set-Location $RepoRoot
Write-Host ""
Write-Host "📦 Installing hookglot Python package..."
& $pythonCmd -m pip install -e . --user

if (Get-Command hookglot -ErrorAction SilentlyContinue) {
    Write-Host "✅ hookglot CLI available" -ForegroundColor Green
    Write-Host ""
    Write-Host "Next step:"
    Write-Host "  hookglot install" -ForegroundColor Cyan
} else {
    $userBase = & $pythonCmd -m site --user-base
    $userBin = Join-Path $userBase "Scripts"
    Write-Host ""
    Write-Host "⚠️  hookglot installed but not in PATH" -ForegroundColor Yellow
    Write-Host "   Add to your PATH:"
    Write-Host "   `$env:Path += ';$userBin'" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "   Or run directly:"
    Write-Host "   $pythonCmd -m hookglot install" -ForegroundColor Cyan
}
