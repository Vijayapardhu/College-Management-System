<#
setup_windows_deps.ps1

This script automates installing Visual Studio Build Tools (C++), PostgreSQL, vcpkg and imaging libs,
then attempts to install Python packages in the project's venv.

Run PowerShell as Administrator.
Usage:
    powershell -ExecutionPolicy Bypass -File .\scripts\setup_windows_deps.ps1

Notes:
- The Visual Studio Build Tools installer may open a GUI to select workloads; choose "C++ build tools".
- Reopen the shell or run the Developer Command Prompt (VsDevCmd.bat) before running pip installs that compile extensions.
- This script attempts best-effort automation; interactive steps may still require your confirmation.
#>

function Ensure-Admin {
    $isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)
    if (-not $isAdmin) {
        Write-Host "This script must be run as Administrator. Please re-open PowerShell as Administrator and re-run the script." -ForegroundColor Yellow
        exit 1
    }
}

function Exec-Log($cmd, $failMessage = $null) {
    Write-Host "--> $cmd" -ForegroundColor Cyan
    try {
        & cmd /c "$cmd"
        if ($LASTEXITCODE -ne 0) {
            Write-Host "Command failed with exit code $LASTEXITCODE" -ForegroundColor Red
            if ($failMessage) { Write-Host $failMessage -ForegroundColor Red }
        }
    } catch {
        Write-Host "Error running: $cmd`n$_" -ForegroundColor Red
    }
}

Ensure-Admin

$projRoot = Split-Path -Parent $MyInvocation.MyCommand.Definition
Write-Host "Project root detected as: $projRoot"

# Check for winget
if (-not (Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "winget not found on this system. Please install App Installer from the Microsoft Store or use Chocolatey/conda alternative." -ForegroundColor Yellow
    Write-Host "Continuing but winget steps will be skipped." -ForegroundColor Yellow
} else {
    Write-Host "Installing Visual Studio Build Tools (may open installer UI). Please ensure you select the 'C++ build tools' workload when the installer appears." -ForegroundColor Green
    # Launch the installer (it may open an interactive UI)
    Exec-Log "winget install --id Microsoft.VisualStudio.2022.BuildTools -e --source winget" "Visual Studio Build Tools install failed. You may need to run the installer manually."

    Write-Host "Installing PostgreSQL (interactive installer)." -ForegroundColor Green
    Exec-Log "winget install --id PostgreSQL.Postgres -e --source winget" "PostgreSQL install failed. You can install manually from https://www.postgresql.org/download/windows/"
}

# Install vcpkg (if git available)
if (-not (Get-Command git -ErrorAction SilentlyContinue)) {
    Write-Host "git not found. Please install git and re-run to allow vcpkg installation. Skipping vcpkg steps." -ForegroundColor Yellow
} else {
    $vcpkgRoot = 'C:\vcpkg'
    if (-not (Test-Path $vcpkgRoot)) {
        Write-Host "Cloning vcpkg to $vcpkgRoot" -ForegroundColor Green
        Exec-Log "git clone https://github.com/microsoft/vcpkg.git $vcpkgRoot" "Failed to clone vcpkg."
    } else {
        Write-Host "vcpkg already present at $vcpkgRoot" -ForegroundColor Green
    }

    if (Test-Path (Join-Path $vcpkgRoot 'bootstrap-vcpkg.bat')) {
        Write-Host "Bootstrapping vcpkg (this may take a few minutes)..." -ForegroundColor Green
        Exec-Log "$vcpkgRoot\bootstrap-vcpkg.bat" "vcpkg bootstrap failed."

        Write-Host "Installing libjpeg-turbo, zlib, libpng for x64 via vcpkg" -ForegroundColor Green
        Exec-Log "$vcpkgRoot\vcpkg.exe install libjpeg-turbo:x64-windows zlib:x64-windows libpng:x64-windows" "vcpkg install failed for imaging libs."

        Write-Host "Integrating vcpkg with MSBuild (optional)" -ForegroundColor Green
        Exec-Log "$vcpkgRoot\vcpkg.exe integrate install" "vcpkg integrate failed."
    } else {
        Write-Host "vcpkg bootstrap script not found; ensure git clone succeeded." -ForegroundColor Yellow
    }
}

# Add PostgreSQL bin to PATH if standard location exists
$possiblePgBins = @(
    'C:\Program Files\PostgreSQL\15\bin',
    'C:\Program Files\PostgreSQL\14\bin',
    'C:\Program Files\PostgreSQL\13\bin'
)
$addedPg = $false
foreach ($p in $possiblePgBins) {
    if (Test-Path $p) {
        Write-Host "Adding PostgreSQL bin ($p) to system PATH" -ForegroundColor Green
        $newPath = [Environment]::GetEnvironmentVariable('PATH',[EnvironmentVariableTarget]::Machine) + ";" + $p
        [Environment]::SetEnvironmentVariable('PATH', $newPath, [EnvironmentVariableTarget]::Machine)
        Write-Host "Added $p to machine PATH. Reopen shells to pick it up." -ForegroundColor Green
        $addedPg = $true
        break
    }
}
if (-not $addedPg) { Write-Host "PostgreSQL bin folder not found in common locations; you may need to update PATH to include pg_config manually." -ForegroundColor Yellow }

# Optionally run Developer Command Prompt if present
$vsDevCmdCandidates = @("C:\Program Files\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat", "C:\Program Files (x86)\Microsoft Visual Studio\2022\BuildTools\Common7\Tools\VsDevCmd.bat")
$vsDevFound = $false
foreach ($cand in $vsDevCmdCandidates) {
    if (Test-Path $cand) {
        Write-Host "Found Visual Studio developer command script: $cand" -ForegroundColor Green
        Write-Host "Running VsDevCmd.bat in the current shell to enable MSVC toolchain for subsequent pip builds..." -ForegroundColor Green
        & $cand -arch=amd64
        $vsDevFound = $true
        break
    }
}
if (-not $vsDevFound) { Write-Host "VsDevCmd.bat not found; you may need to open the 'x64 Native Tools Command Prompt for VS' or reboot after VS Build Tools install." -ForegroundColor Yellow }

# Prepare venv python path (update if your venv is elsewhere)
$venvPython = Join-Path $projRoot 'venv\Scripts\python.exe'
if (-not (Test-Path $venvPython)) {
    Write-Host "WARNING: venv Python not found at $venvPython. If your venv is elsewhere, update the script or activate the venv and run pip manually." -ForegroundColor Yellow
} else {
    Write-Host "Upgrading pip/setuptools/wheel in venv..." -ForegroundColor Green
    & $venvPython -m pip install --upgrade pip setuptools wheel build setuptools_scm

    Write-Host "Installing bulk requirements from requirements.installable.txt (this may take a while)..." -ForegroundColor Green
    $reqFile = Join-Path $projRoot 'requirements.installable.txt'
    if (Test-Path $reqFile) {
        & $venvPython -m pip install -r $reqFile
    } else {
        Write-Host "requirements.installable.txt not found at $reqFile. Make sure the file exists or install packages manually." -ForegroundColor Yellow
    }

    Write-Host "Attempting to install psycopg2-binary, Pillow, python-magic (may still require system libs)..." -ForegroundColor Green
    & $venvPython -m pip install psycopg2-binary Pillow python-magic

    Write-Host "Installation step finished. Run the verification commands described in the repository README or run the verify snippet manually." -ForegroundColor Green
}

Write-Host "
Important: If any pip install that builds C extensions still fails, ensure you opened a shell with the MSVC toolchain active (Developer Command Prompt) and that libjpeg/libpng/zlib headers/libs are discoverable (via vcpkg integration or MSYS2)." -ForegroundColor Yellow

Write-Host "Script finished. If you need a Chocolatey or conda variant, run the appropriate commands or ask for that script." -ForegroundColor Cyan
