$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
try {
    . (Join-Path $PSScriptRoot 'python_bootstrap.ps1')
    $python = Initialize-XsmbEnvironment -ProjectDir $PSScriptRoot
    & $python -m pip install -r requirements-dev.txt
    if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed. Check Internet/pip output above.' }
    & $python -m pytest -q
    if ($LASTEXITCODE -ne 0) { throw 'Tests failed. Build stopped.' }
    & $python -m PyInstaller --clean --noconfirm XSMB_AI_Indicator.spec
    if ($LASTEXITCODE -ne 0) { throw 'EXE build failed.' }
    if (-not (Test-Path 'dist\XSMB_AI_Indicator_V2_2_PRO.exe')) { throw 'EXE not found.' }
    Write-Host 'SUCCESS: dist\XSMB_AI_Indicator_V2_2_PRO.exe'
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
