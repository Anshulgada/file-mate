#!/usr/bin/env bash

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

# --- Try uv first ---
if command_exists uv; then
    echo -e "✅ Found ${GREEN}uv${NC}. Installing using uv..."
    uv pip install --global "$PACKAGE_NAME"
    echo -e "🎉 ${GREEN}FileMate installed successfully with uv!${NC}"
    echo -e "💡 You can now run: ${YELLOW}filemate${NC}"
    exit 0
fi

# --- Try pipx ---
if command_exists pipx; then
    echo -e "✅ Found ${GREEN}pipx${NC}. Installing using pipx..."
    pipx install "$PACKAGE_NAME"
    echo -e "🎉 ${GREEN}FileMate installed successfully with pipx!${NC}"
    echo -e "💡 You can now run: ${YELLOW}filemate${NC}"
    exit 0
fi

# --- Fallback to pip (less ideal) ---
if command_exists pip; then
    echo -e "⚠️  'uv' and 'pipx' not found. Falling back to pip (no venv isolation)."

    # Suggest sudo on Linux/macOS
    if [[ "$OSTYPE" == "linux-gnu"* || "$OSTYPE" == "darwin"* ]]; then
        echo -e "${YELLOW}🔒 You might need to run with sudo:${NC}"
        echo -e "    ${RED}sudo pip install $PACKAGE_NAME${NC}"
    fi

    pip install "$PACKAGE_NAME"
    echo -e "🎉 ${GREEN}FileMate installed with pip.${NC}"
    echo -e "💡 You can now run: ${YELLOW}filemate${NC}"
    exit 0
fi

# --- If nothing is available ---
echo -e "${RED}❌ Could not find 'uv', 'pipx', or 'pip' on your system.${NC}"
echo "➡️  Please install one of them and try again:"
echo "    https://github.com/astral-sh/uv"
echo "    https://pypa.github.io/pipx"
exit 1
