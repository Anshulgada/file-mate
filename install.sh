#!/usr/bin/env bash
# Installer script for FileMate (filemate)

# Exit immediately if a command exits with a non-zero status.
set -e

TOOL_NAME="filemate"
PACKAGE_NAME="filemate"


# --- Colors ---
GREEN='\033[1;32m'
BLUE='\033[1;34m'
YELLOW='\033[1;33m'
RED='\033[1;31m'
NC='\033[0m' # No Color

# --- ASCII banner ---
echo ""
echo -e "${BLUE}"
echo "╔═════════════════════════════════════════════════════╗"
echo "║                                                     ║"
echo "║   🧰 Installing FileMate — Your File CLI Pal™       ║"
echo "║                                                     ║"
echo "╚═════════════════════════════════════════════════════╝"
echo -e "${NC}"


# --- Show version from pyproject.toml if present ---
if [[ -f "pyproject.toml" ]]; then
    VERSION=$(grep -m1 '^version =' pyproject.toml | cut -d '"' -f2)
    echo -e "📦 Version: ${YELLOW}${VERSION}${NC}"
fi

echo -e "\n🔍 Checking your system for install options...\n"


# --- Function to check command existence ---
command_exists() {
    command -v "$1" >/dev/null 2>&1
}


# --- Try pipx (Preferred Method) ---
if command_exists pipx; then
    echo -e "✅ Found ${GREEN}pipx${NC} (Recommended). Installing ${TOOL_NAME} in an isolated environment..."
    pipx install "$PACKAGE_NAME"
    echo -e "\n🎉 ${GREEN}${TOOL_NAME} installed successfully using pipx!${NC}"
    echo -e "💡 You should now be able to run the command: ${YELLOW}${TOOL_NAME}${NC}"

    # Verify installation (optional but good)
    if command_exists ${TOOL_NAME}; then
         echo -e "✅ Verification successful: '${TOOL_NAME}' command found."
    else
         echo -e "${YELLOW}⚠️ Verification failed. Please ensure pipx's bin directory is in your PATH.${NC}"
         echo -e "   Run: ${YELLOW}pipx ensurepath${NC}"
    fi

    # Enable autocomplete (Bash)
    echo -e "\n🔧 Enabling autocomplete for FileMate..." -ForegroundColor Cyan
    if ! grep -q "filemate_complete=source filemate" ~/.bashrc; then
        echo 'eval "$(_FILEMATE_COMPLETE=source filemate)"' >> ~/.bashrc
        echo -e "✅ Autocompletion added to your .bashrc!" -ForegroundColor Green
    else
        echo -e "⚠️ Autocompletion already exists in .bashrc!" -ForegroundColor Yellow
    fi
    exit 0
fi


# --- Fallback to pip (Less Ideal) ---
if command_exists pip; then
    echo -e "⚠️  ${YELLOW}pipx not found.${NC} Falling back to pip."
    echo -e "   ${RED}NOTE:${NC} Installation via pip lacks isolation and might conflict with other packages."
    echo -e "   Consider installing pipx first: https://pypa.github.io/pipx/\n"

    # Suggest sudo only if not installing as user
    INSTALL_CMD="pip install $PACKAGE_NAME"
    INSTALL_NOTE=""
    if [[ "$EUID" -ne 0 && ("$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"*) ]]; then
        echo -e "${YELLOW}🔒 Installing system-wide might require sudo:${NC}"
        echo -e "    ${RED}sudo pip install $PACKAGE_NAME${NC}"
        echo -e "${YELLOW}   Alternatively, try installing for the current user (might require PATH adjustment):${NC}"
        echo -e "    ${YELLOW}pip install --user $PACKAGE_NAME${NC}"
        INSTALL_NOTE=" (using default pip install)" # Clarify if sudo/--user isn't explicitly used by the script itself
    fi

    echo -e "Attempting installation with: ${YELLOW}${INSTALL_CMD}${INSTALL_NOTE}${NC}"
    $INSTALL_CMD # Execute the basic pip install command

    echo -e "\n🎉 ${GREEN}${TOOL_NAME} installed using pip.${NC}"
    echo -e "💡 You should now be able to run: ${YELLOW}${TOOL_NAME}${NC}"
    echo -e "${YELLOW}⚠️  If the command isn't found, you may need to adjust your system's PATH variable.${NC}"
    echo -e "   (Check Python's script directory or user script directory)"
    exit 0
fi


# --- If nothing is available ---
echo -e "${RED}❌ Could not find 'pipx' or 'pip' on your system.${NC}"
echo "➡️  Please install Python and pip, or preferably pipx:"
echo "    Python (includes pip): https://www.python.org/downloads/"
echo "    pipx (Recommended): https://pypa.github.io/pipx/"
exit 1
