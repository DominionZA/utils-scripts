# Ensure script is run as Administrator
if (-not ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole] "Administrator")) {
    Write-Host "Please run this script as an Administrator." -ForegroundColor Red
    exit
}

# Hide the taskbar search
Set-ItemProperty -Path "HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Search" -Name "SearchboxTaskbarMode" -Value 0 -Type DWord
Stop-Process -Name explorer -Force
Start-Process explorer

# Function to check if a command exists
function Test-CommandExists {
    param ($command)
    $oldPreference = $ErrorActionPreference
    $ErrorActionPreference = 'stop'
    try { if (Get-Command $command) { return $true } }
    catch { return $false }
    finally { $ErrorActionPreference = $oldPreference }
}

# Initialize package managers
Write-Host "Initializing package managers..." -ForegroundColor Green

# Check and install Chocolatey if needed
if (-not (Test-CommandExists choco)) {
    Write-Host "Installing Chocolatey..."
    Set-ExecutionPolicy Bypass -Scope Process -Force
    [System.Net.ServicePointManager]::SecurityProtocol = [System.Net.ServicePointManager]::SecurityProtocol -bor 3072
    Invoke-Expression ((New-Object System.Net.WebClient).DownloadString('https://chocolatey.org/install.ps1'))
    refreshenv
}

# Check and install Winget if needed (for Windows 10 users who might not have it)
if (-not (Test-CommandExists winget)) {
    Write-Host "Winget not found. Please install it from the Microsoft Store or GitHub."
    Write-Host "Microsoft Store link: https://www.microsoft.com/en-us/p/app-installer/9nblggh4nns1"
    Read-Host "Press Enter to continue after installing Winget"
}

# Install Chocolatey extensions
Write-Host "Installing Chocolatey extensions..." -ForegroundColor Green
choco install -y chocolatey-core.extension
choco install -y chocolatey-fastanswers.extension
choco install -y chocolatey-misc-helpers.extension
choco install -y chocolatey-windowsupdate.extension

# Configure keyboard settings
Write-Host "Configuring keyboard settings..." -ForegroundColor Green
Add-Type -TypeDefinition @"
using System;
using System.Runtime.InteropServices;
public class KeyboardSettings {
    [DllImport("user32.dll", SetLastError = true)]
    public static extern bool SystemParametersInfo(uint uiAction, uint uiParam, IntPtr pvParam, uint fWinIni);
    public const uint SPI_SETKEYBOARDDELAY = 0x0017;
    public const uint SPI_SETKEYBOARDSPEED = 0x000B;
    public const uint SPIF_UPDATEINIFILE = 0x01;
    public const uint SPIF_SENDCHANGE = 0x02;
}
"@
[KeyboardSettings]::SystemParametersInfo([KeyboardSettings]::SPI_SETKEYBOARDDELAY, 0, [IntPtr]::Zero, ([KeyboardSettings]::SPIF_UPDATEINIFILE -bor [KeyboardSettings]::SPIF_SENDCHANGE))
[KeyboardSettings]::SystemParametersInfo([KeyboardSettings]::SPI_SETKEYBOARDSPEED, 31, [IntPtr]::Zero, ([KeyboardSettings]::SPIF_UPDATEINIFILE -bor [KeyboardSettings]::SPIF_SENDCHANGE))

# Enable and configure WSL with error handling                        
Write-Host "Checking and configuring WSL..." -ForegroundColor Green   

try {                                                                 
    # Check if WSL is already enabled                                 
    $wslStatus = Get-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux
    
    if ($wslStatus.State -ne "Enabled") {                             
        Write-Host "Enabling WSL..."
        Enable-WindowsOptionalFeature -Online -FeatureName Microsoft-Windows-Subsystem-Linux -NoRestart
    } else {
        Write-Host "WSL is already enabled."
    }

    # Update WSL
    Write-Host "Updating WSL..."
    wsl --update                                                      

    # Check if Ubuntu is installed
    $ubuntuInstalled = wsl -l | Select-String "Ubuntu"
    if (-not $ubuntuInstalled) {
        Write-Host "Installing Ubuntu distribution..."
        wsl --install -d Ubuntu --no-launch
    } else {
        Write-Host "Ubuntu distribution is already installed."
    }
} catch {
    Write-Host "Error configuring WSL: $_" -ForegroundColor Red
    Write-Host "Continuing with rest of the setup..." -ForegroundColor Yellow
}

# Install applications using Winget (preferred for Microsoft and common applications)
Write-Host "Installing applications via Winget..." -ForegroundColor Green
$wingetApps = @(
    "seerge.g-helper",
    "Microsoft.PowerToys",
    "9NKSQGP7F2NH", # Whatsapp
    "Microsoft.DotNet.Sdk.8",
    "Microsoft.VisualStudioCode",
    "Microsoft.VisualStudio.2022.Community",
    "Microsoft.VisualStudio.2022.Workload.NetWeb",
    "Google.Chrome",
    "Git.Git",
    "Docker.DockerDesktop",
    "Notepad++.Notepad++",
    "SlackTechnologies.Slack",
    "Postman.Postman",
    "Python.Python.3",
    "JanDeDobbeleer.OhMyPosh",
    "PuTTY.PuTTY",
    "Oracle.MySQLWorkbench",
    "Valve.Steam",
    "Logitech.GHUB",
    "WinDirStat.WinDirStat",
    "CPUID.CPU-Z",
    "CrystalDewWorld.CrystalDiskMark"
)

foreach ($app in $wingetApps) {
    Write-Host "Installing $app..."
    winget install --silent --accept-package-agreements --accept-source-agreements -e --id $app
}

# Install applications using Chocolatey (for apps not available or better handled in Winget)
Write-Host "Installing applications via Chocolatey..." -ForegroundColor Green
$chocoApps = @(
    "poshgit",
    "resharper",
    "winrar"
)

foreach ($app in $chocoApps) {
    Write-Host "Installing $app..."
    choco install -y $app
}

# Install VS Code extensions
Write-Host "Installing VS Code extensions..." -ForegroundColor Green
$codeExtensions = @(
    "ms-vscode.powershell",
    "ms-dotnettools.csharp",
    "eamodio.gitlens"
)

foreach ($extension in $codeExtensions) {
    code --install-extension $extension
}

# Configure power settings
Write-Host "Configuring power settings..." -ForegroundColor Green
powercfg -duplicatescheme e9a42b02-d5df-448d-aa00-03f14749eb61

docker run --name redis -d --restart always -p 6379:6379 redis:latest
docker run --name mysql8 -d -p 3306:3306 -e MYSQL_ROOT_PASSWORD=P@ssw0rd1 -e MYSQL_USER=Aura -e MYSQL_PASSWORD=P@ssw0rd1 --restart always mysql:8

# Optional installations (commented out by default)
<#
# Gaming platforms
# choco install -y origin
# choco install -y battle.net
# choco install geforce-experience -y

# Additional tools
# choco install -y mysql
# choco install -y discord
# choco install boxstarter -y
# choco install GetRight -y
#>

# Prompt for restart
$restartPrompt = Read-Host "Setup is complete. Would you like to restart your computer now? (y/n)"
if ($restartPrompt -eq 'y' -or $restartPrompt -eq 'Y') {
    Restart-Computer -Force
} else {
    Write-Host "Please remember to restart your computer later to complete the setup." -ForegroundColor Yellow
}