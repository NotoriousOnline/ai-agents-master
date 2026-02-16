# AI Agents Master — Python environment setup (Windows)
# Run from repo root: .\scripts\setup.ps1
# Requires: Python 3.11+ on PATH (or use py -3.11)

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
if (-not (Test-Path "$RepoRoot\pyproject.toml")) {
    $RepoRoot = $PWD.Path
}
Set-Location $RepoRoot

# Prefer Python from .python-version if pyenv is available
$pythonVersion = "3.11"
if (Test-Path ".python-version") {
    $pythonVersion = (Get-Content ".python-version" -Raw).Trim()
}

Write-Host "Using Python $pythonVersion (edit .python-version to change)" -ForegroundColor Cyan

# Find Python 3.11+: try py launcher, then python
$pythonExe = $null
foreach ($try in @("py -$pythonVersion", "py -3", "python")) {
    try {
        $ver = & $try -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')" 2>$null
        if ($ver -and [int]($ver.Split('.')[0]) -ge 3 -and [int]($ver.Split('.')[1]) -ge 11) {
            $pythonExe = $try
            break
        }
    } catch {}
}

if (-not $pythonExe) {
    Write-Host "Python 3.11+ not found. Install from https://www.python.org/downloads/ or use 'py -3.11'." -ForegroundColor Red
    exit 1
}

Write-Host "Creating virtual environment in .venv ..." -ForegroundColor Green
if (Test-Path ".venv") {
    Write-Host ".venv already exists; skipping creation." -ForegroundColor Yellow
} else {
    & $pythonExe -m venv .venv
    if ($LASTEXITCODE -ne 0) {
        Write-Host "Failed to create .venv. Try: $pythonExe -m venv .venv" -ForegroundColor Red
        exit 1
    }
}

$pip = Join-Path $RepoRoot ".venv\Scripts\pip.exe"
$python = Join-Path $RepoRoot ".venv\Scripts\python.exe"
if (-not (Test-Path $pip)) {
    Write-Host "Expected $pip not found." -ForegroundColor Red
    exit 1
}

Write-Host "Installing dependencies ..." -ForegroundColor Green
& $pip install --upgrade pip -q
if (Test-Path "requirements.txt") {
    & $pip install -r requirements.txt -q
}
& $pip install -e . -q
if ($LASTEXITCODE -ne 0) {
    Write-Host "pip install failed." -ForegroundColor Red
    exit 1
}

Write-Host "Done. Activate with: .\.venv\Scripts\Activate.ps1" -ForegroundColor Green
Write-Host "Run API: .\.venv\Scripts\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000" -ForegroundColor Cyan
