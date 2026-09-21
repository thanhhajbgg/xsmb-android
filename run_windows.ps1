$ErrorActionPreference = 'Stop'
Set-Location $PSScriptRoot
try {
    . (Join-Path $PSScriptRoot 'python_bootstrap.ps1')
    $python = Initialize-XsmbEnvironment -ProjectDir $PSScriptRoot
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'Continue'
    & $python -c 'import numpy,bs4,openpyxl,reportlab' 2>$null
    $dependenciesReady = ($LASTEXITCODE -eq 0)
    $ErrorActionPreference = $oldPreference
    if (-not $dependenciesReady) {
        Write-Host 'Dang cai thu vien. Lan dau can ket noi Internet...'
        & $python -m pip install -r requirements.txt
        if ($LASTEXITCODE -ne 0) { throw 'Cai thu vien that bai. Xem loi mang/pip o phia tren.' }
    }
    Write-Host 'Dang mo XSMB V2.1 PRO. Giu cua so nay mo trong khi su dung.'
    & $python run_desktop.py
    if ($LASTEXITCODE -ne 0) { throw 'Ung dung dung do loi. Xem thong bao Python o phia tren.' }
    exit 0
} catch {
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}
