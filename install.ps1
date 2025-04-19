# Installer script for FileMate (filemate)

# Stop script on most errors
$ErrorActionPreference = 'Stop'

$ToolName = "filemate"
$PackageName = "filemate"


# --- ASCII banner ---
Write-Host ""
Write-Host "╔═════════════════════════════════════════════════════╗" -ForegroundColor Cyan
Write-Host "║                                                     ║"
Write-Host "║   🧰 Installing FileMate — Your File CLI Pal™       ║"
Write-Host "║                                                     ║"
Write-Host "╚═════════════════════════════════════════════════════╝" -ForegroundColor Cyan

Write-Host "`n🔍 Checking your system for installation options...`n"


# --- Function to check command existence ---
function Command-Exists {
    param($Command)
    $found = $null -ne (Get-Command $Command -ErrorAction SilentlyContinue)
    # Write-Host "Debug: Checking for $Command - Found: $found" # Uncomment for debugging
    return $found
}


# --- Try pipx (Preferred Method) ---
if (Command-Exists "pipx") {
    Write-Host "✅ Found 'pipx' (Recommended). Installing $ToolName in an isolated environment..." -ForegroundColor Green
    pipx install $PackageName
    Write-Host "`n🎉 $ToolName installed successfully using pipx!" -ForegroundColor Green
    Write-Host "💡 You should now be able to run the command: $($ToolName)" -ForegroundColor Yellow
    # Verify installation (optional but good)
    if (Command-Exists $ToolName) {
         Write-Host "✅ Verification successful: '$($ToolName)' command found." -ForegroundColor Green
    } else {
         Write-Host "⚠️ Verification failed. Please ensure pipx's bin directory is in your PATH." -ForegroundColor Yellow
         Write-Host "   Run: pipx ensurepath" -ForegroundColor Yellow
    }
    exit 0
}


# --- Fallback to pip (Less Ideal) ---
if (Command-Exists "pip") {
    Write-Host "⚠️ 'pipx' not found. Falling back to pip." -ForegroundColor Yellow
    Write-Host "   NOTE: Installation via pip lacks isolation and might conflict with other packages." -ForegroundColor Red
    Write-Host "   Consider installing pipx first: https://pypa.github.io/pipx/`n" -ForegroundColor Yellow

    $installCommand = "pip install --user $PackageName"
    Write-Host "Attempting installation with: $($installCommand)" -ForegroundColor Yellow
    # Note: System-wide pip install often requires Administrator privileges on Windows.
    # We don't automatically elevate, user might need to re-run in an Admin terminal.
    # Added --user flag to avoid permission issues on Windows.
    # Uncomment the line below if you want to install system-wide (requires admin privileges)
    # $installCommand = "pip install $PackageName" # Uncomment for system-wide install (requires admin)

    Invoke-Expression $installCommand

    Write-Host "`n🎉 $ToolName installed using pip." -ForegroundColor Green
    Write-Host "💡 You should now be able to run: $($ToolName)" -ForegroundColor Yellow
    Write-Host "⚠️ If the command isn't found, you may need to adjust your system's PATH variable." -ForegroundColor Yellow
    Write-Host "   (Check Python's Scripts directory or the User Scripts directory)"
    exit 0
}


# --- If nothing is available ---
Write-Host "❌ Could not find 'pipx' or 'pip' on your system." -ForegroundColor Red
Write-Host "➡️ Please install Python and pip, or preferably pipx:"
Write-Host "    Python (includes pip): https://www.python.org/downloads/"
Write-Host "    pipx (Recommended): https://pypa.github.io/pipx/"
Write-Host "    Filemate CLI Tool: https://pypi.org/project/file-mate/"
exit 1
