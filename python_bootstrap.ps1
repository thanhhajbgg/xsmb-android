# Shared interpreter discovery for both Run and Build. ASCII for Windows PowerShell 5.1.
function Test-XsmbPython {
    param([string]$Command, [string[]]$Prefix = @())
    $ErrorActionPreference = 'Continue'
    try {
        $output = & $Command @Prefix -c 'import sys; assert sys.version_info >= (3,11); print(sys.executable)' 2>$null
        if ($LASTEXITCODE -eq 0 -and $output) {
            $path = ([string](@($output)[-1])).Trim()
            if (Test-Path -LiteralPath $path -PathType Leaf) { return $path }
        }
    } catch { }
    return $null
}

function Get-XsmbPython {
    param([string]$ProjectDir)
    $venv = Join-Path $ProjectDir '.venv\Scripts\python.exe'
    if (Test-Path -LiteralPath $venv) {
        $found = Test-XsmbPython -Command $venv
        if ($found) { return $found }
    }
    # PATH interpreter first; py is an optional fallback, never required.
    foreach ($name in @('python.exe', 'python3.exe', 'py.exe')) {
        $cmd = Get-Command $name -CommandType Application -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($cmd) {
            # Skip Microsoft Store placeholders that open the Store instead of Python.
            if ($cmd.Source -match '\\Microsoft\\WindowsApps\\python(3)?\.exe$') { continue }
            $prefix = @()
            if ($name -eq 'py.exe') { $prefix = @('-3') }
            $found = Test-XsmbPython -Command $cmd.Source -Prefix $prefix
            if ($found) { return $found }
        }
    }
    # Official per-user, per-machine and Python install-manager locations.
    $patterns = @()
    if ($env:LOCALAPPDATA) {
        $patterns += (Join-Path $env:LOCALAPPDATA 'Programs\Python\Python*\python.exe')
        $patterns += (Join-Path $env:LOCALAPPDATA 'Python\pythoncore-*\python.exe')
    }
    if ($env:ProgramFiles) { $patterns += (Join-Path $env:ProgramFiles 'Python*\python.exe') }
    if (${env:ProgramFiles(x86)}) { $patterns += (Join-Path ${env:ProgramFiles(x86)} 'Python*\python.exe') }
    if ($env:SystemDrive) { $patterns += "$($env:SystemDrive)\Python*\python.exe" }
    foreach ($pattern in $patterns) {
        foreach ($file in @(Get-ChildItem -Path $pattern -File -ErrorAction SilentlyContinue | Sort-Object FullName -Descending)) {
            $found = Test-XsmbPython -Command $file.FullName
            if ($found) { return $found }
        }
    }
    # PEP 514 registration covers custom installation directories.
    foreach ($root in @('HKCU:\Software\Python','HKLM:\Software\Python','HKLM:\Software\WOW6432Node\Python')) {
        $versions = @(Get-ChildItem -LiteralPath $root -ErrorAction SilentlyContinue | ForEach-Object {
            Get-ChildItem -LiteralPath $_.PSPath -ErrorAction SilentlyContinue
        })
        foreach ($version in $versions) {
            $key = Get-Item -LiteralPath ($version.PSPath + '\InstallPath') -ErrorAction SilentlyContinue
            if ($key) {
                $candidate = $key.GetValue('ExecutablePath')
                if (-not $candidate) {
                    $directory = $key.GetValue('')
                    if ($directory) { $candidate = Join-Path $directory 'python.exe' }
                }
                if ($candidate) {
                    $found = Test-XsmbPython -Command $candidate
                    if ($found) { return $found }
                }
            }
        }
    }
    throw @'
Khong tim thay Python 3.11 tro len.
1. Cai Python tu https://www.python.org/downloads/windows/
2. Khi cai, chon 'Add python.exe to PATH' neu co tuy chon nay.
3. Dong cua so nay va mo lai CHAY_UNG_DUNG.bat.
Ban nay KHONG bat buoc co lenh py / Python Launcher.
Khong can chay bang quyen Administrator.
'@
}

function Initialize-XsmbEnvironment {
    param([string]$ProjectDir)
    $python = Get-XsmbPython -ProjectDir $ProjectDir
    $venv = Join-Path $ProjectDir '.venv\Scripts\python.exe'
    if ($python -ne $venv) {
        Write-Host "Python: $python"
        & $python -m venv (Join-Path $ProjectDir '.venv')
        if ($LASTEXITCODE -ne 0) { throw 'Khong tao duoc moi truong. Kiem tra quyen ghi thu muc va module venv.' }
    }
    if (-not (Test-Path -LiteralPath $venv)) { throw 'Khong tim thay Python trong .venv sau khi khoi tao.' }
    return $venv
}
