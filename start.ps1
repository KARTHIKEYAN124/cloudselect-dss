$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
if (-not (Test-Path '.venv/Scripts/python.exe')) {
    python -m venv .venv
    if ($LASTEXITCODE -ne 0) { throw 'Python environment creation failed' }
}
& ./.venv/Scripts/python.exe -m pip install -r backend/requirements.txt
if ($LASTEXITCODE -ne 0) { throw 'Python dependency installation failed' }
Push-Location frontend
try {
    npm install
    if ($LASTEXITCODE -ne 0) { throw 'Frontend dependency installation failed' }
    npm run build
    if ($LASTEXITCODE -ne 0) { throw 'Frontend build failed' }
} finally { Pop-Location }
Write-Host 'CloudSelect is starting at http://127.0.0.1:5000'
& ./.venv/Scripts/python.exe backend/app.py
