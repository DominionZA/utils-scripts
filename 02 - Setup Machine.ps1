# Ensure winget is installed
if (!(Get-Command winget -ErrorAction SilentlyContinue)) {
    Write-Host "Winget is not installed. Please install it from the Microsoft Store or GitHub."
    exit
}

# Install applications
winget install --silent -e --id Oracle.MySQLWorkbench
winget install --silent -e --id Google.Chrome
winget install --silent -e --id Notepad++.Notepad++
winget install --silent -e --id RARLab.WinRAR
winget install --silent -e --id Google.Drive
winget install --silent -e --id SlackTechnologies.Slack
winget install --silent -e --id Postman.Postman
winget install --silent -e --id WinDirStat.WinDirStat
winget install --silent -e --id Devart.DbForgeStudioForMySQL
winget install --silent -e --id CrystalDewWorld.CrystalDiskMark
winget install --silent -e --id CPUID.CPU-Z
winget install --silent -e --id Git.Git
winget install --silent -e --id PuTTY.PuTTY
winget install --silent -e --id Docker.DockerDesktop
winget install --silent -e --id Microsoft.VisualStudioCode
winget install --silent -e --id Microsoft.VisualStudio.2022.Community
winget install --silent -e --id Python.Python.3
winget install --silent -e --id JanDeDobbeleer.OhMyPosh
winget install --silent -e --id Valve.Steam
winget install --silent -e --id Logitech.GHUB
winget install --silent -e --id Logitech.GHUB
# Install Visual Studio Code extensions
code --install-extension ms-vscode.powershell
code --install-extension ms-dotnettools.csharp
code --install-extension eamodio.gitlens

# Install Visual Studio Workload
winget install --silent -e --id Microsoft.VisualStudio.2022.Workload.NetWeb

# Note: Some applications might not be available through winget or might have different package names.
# You may need to manually install or find alternative sources for:
# - Boxstarter
# - GetRight
# - Discord (available, but commented out in original script)
# - MySQL (you might want to use MySQL Installer instead)
# - ReSharper (usually installed as a Visual Studio extension)
# - GeForce Experience (available, but commented out in original script)
# - Origin (not typically available through package managers)
# - Battle.net (not typically available through package managers)

# For Visual Studio extensions like ReSharper, you might need to use the Visual Studio Installer or the extension marketplace within Visual Studio.