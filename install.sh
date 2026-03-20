#!/bin/bash
#
# Layout Switcher Installer
# https://github.com/moiz2306/layout-switcher
#
# Usage:
#   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/moiz2306/layout-switcher/main/install.sh)"
#
# This script installs Layout Switcher to ~/layout-switcher and sets up
# a Python virtual environment with all dependencies.
#

set -e

# --- Colors ---
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
BOLD='\033[1m'
NC='\033[0m' # No Color

REPO_URL="https://github.com/moiz2306/layout-switcher.git"
INSTALL_DIR="$HOME/layout-switcher"
CONFIG_DIR="$HOME/.config/layout-switcher"

# --- Helper functions ---

info() {
    echo -e "${BLUE}==>${NC} ${BOLD}$1${NC}"
}

success() {
    echo -e "${GREEN}==>${NC} ${BOLD}$1${NC}"
}

warn() {
    echo -e "${YELLOW}Warning:${NC} $1"
}

error() {
    echo -e "${RED}Error:${NC} $1"
    exit 1
}

# --- Banner ---

echo ""
echo -e "${BOLD}  Layout Switcher Installer${NC}"
echo -e "  Auto-detect and correct wrong keyboard layout on macOS"
echo -e "  ${BLUE}https://github.com/moiz2306/layout-switcher${NC}"
echo ""

# --- Check macOS ---

if [[ "$(uname)" != "Darwin" ]]; then
    error "Layout Switcher only works on macOS."
fi

# --- Check Python ---

info "Checking prerequisites..."

if ! command -v python3 &>/dev/null; then
    error "Python 3 is not installed.

  Install it with one of these methods:

  1. Xcode Command Line Tools (recommended):
     xcode-select --install

  2. Homebrew:
     brew install python

  3. Download from https://www.python.org/downloads/

  Then run this installer again."
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}")')
PYTHON_MAJOR=$(python3 -c 'import sys; print(sys.version_info.major)')
PYTHON_MINOR=$(python3 -c 'import sys; print(sys.version_info.minor)')

if [[ "$PYTHON_MAJOR" -lt 3 ]] || [[ "$PYTHON_MAJOR" -eq 3 && "$PYTHON_MINOR" -lt 11 ]]; then
    error "Python 3.11 or later is required. You have Python $PYTHON_VERSION."
fi

success "Python $PYTHON_VERSION found"

# --- Check git ---

if ! command -v git &>/dev/null; then
    error "Git is not installed.

  Install it with:
     xcode-select --install

  Then run this installer again."
fi

success "Git found"

# --- Check if already installed ---

if [[ -d "$INSTALL_DIR" ]]; then
    echo ""
    warn "Layout Switcher is already installed at $INSTALL_DIR"
    echo ""
    read -p "  Reinstall? This will remove the existing installation. [y/N] " reinstall
    if [[ "$reinstall" != "y" && "$reinstall" != "Y" ]]; then
        echo "  Aborted."
        exit 0
    fi
    rm -rf "$INSTALL_DIR"
    echo ""
fi

# --- Clone repository ---

info "Downloading Layout Switcher..."
git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" 2>/dev/null
success "Downloaded to $INSTALL_DIR"

# --- Create virtual environment ---

info "Creating Python virtual environment..."
python3 -m venv "$INSTALL_DIR/.venv"
success "Virtual environment created"

# --- Install dependencies ---

info "Installing dependencies (this may take a minute)..."
"$INSTALL_DIR/.venv/bin/pip" install -r "$INSTALL_DIR/requirements.txt" --quiet 2>/dev/null
success "Dependencies installed"

# --- Build word dictionary ---

info "Building English word dictionary..."
"$INSTALL_DIR/.venv/bin/python3" "$INSTALL_DIR/scripts/build_wordlist.py" 2>/dev/null
success "Dictionary built"

# --- Create config ---

mkdir -p "$CONFIG_DIR"
if [[ ! -f "$CONFIG_DIR/config.yaml" ]]; then
    cp "$INSTALL_DIR/config.example.yaml" "$CONFIG_DIR/config.yaml"
    success "Config created at $CONFIG_DIR/config.yaml"
else
    success "Config already exists (kept)"
fi

# --- Launch at login ---

echo ""
read -p "$(echo -e "${BLUE}==>${NC} ${BOLD}Start Layout Switcher automatically at login? [y/N]${NC} ")" auto_start
if [[ "$auto_start" == "y" || "$auto_start" == "Y" ]]; then
    mkdir -p "$HOME/Library/LaunchAgents"
    sed -e "s|__VENV_PYTHON__|$INSTALL_DIR/.venv/bin/python3|g" \
        -e "s|__SRC_MAIN__|$INSTALL_DIR/src/main.py|g" \
        -e "s|__LOG_DIR__|$CONFIG_DIR|g" \
        "$INSTALL_DIR/com.layout-switcher.plist" > "$HOME/Library/LaunchAgents/com.layout-switcher.plist"
    launchctl load "$HOME/Library/LaunchAgents/com.layout-switcher.plist" 2>/dev/null
    success "Launch at login enabled"
fi

# --- Done ---

echo ""
echo -e "${GREEN}${BOLD}  Installation complete!${NC}"
echo ""
echo -e "  ${BOLD}Before you start:${NC} Grant macOS permissions"
echo ""
echo -e "  Layout Switcher needs two permissions to work. Open:"
echo -e "  ${BOLD}System Settings → Privacy & Security${NC}"
echo ""
echo -e "  1. ${BOLD}Input Monitoring${NC} → click + → add your Terminal app"
echo -e "  2. ${BOLD}Accessibility${NC}    → click + → add your Terminal app"
echo ""
echo -e "  Then ${BOLD}restart your terminal${NC} (Cmd+Q, reopen) and run:"
echo ""
echo -e "  ${GREEN}$INSTALL_DIR/.venv/bin/python3 $INSTALL_DIR/src/main.py${NC}"
echo ""
echo -e "  Or create an alias for convenience:"
echo ""
echo -e "  ${YELLOW}echo 'alias layout-switcher=\"$INSTALL_DIR/.venv/bin/python3 $INSTALL_DIR/src/main.py\"' >> ~/.zshrc${NC}"
echo -e "  ${YELLOW}source ~/.zshrc${NC}"
echo -e "  ${YELLOW}layout-switcher${NC}"
echo ""
echo -e "  A green dot ${GREEN}●${NC} will appear in your menu bar when it's running."
echo ""
