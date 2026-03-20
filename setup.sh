#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
CONFIG_DIR="$HOME/.config/layout-switcher"

echo "=== Layout Switcher Setup ==="

# Create venv if needed
if [ ! -d "$SCRIPT_DIR/.venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv "$SCRIPT_DIR/.venv"
fi

echo "Installing dependencies..."
"$SCRIPT_DIR/.venv/bin/pip" install -r "$SCRIPT_DIR/requirements.txt" --quiet

# Build wordlist
echo "Building English wordlist..."
"$SCRIPT_DIR/.venv/bin/python3" "$SCRIPT_DIR/scripts/build_wordlist.py"

# Create config directory
mkdir -p "$CONFIG_DIR"

# Copy example config if no config exists
if [ ! -f "$CONFIG_DIR/config.yaml" ]; then
    cp "$SCRIPT_DIR/config.example.yaml" "$CONFIG_DIR/config.yaml"
    echo "Created config at $CONFIG_DIR/config.yaml"
else
    echo "Config already exists at $CONFIG_DIR/config.yaml"
fi

echo ""
echo "=== Setup complete ==="
echo ""
echo "To run manually:"
echo "  $SCRIPT_DIR/.venv/bin/python3 $SCRIPT_DIR/src/main.py"
echo ""
read -p "Install as autostart service? [y/N] " install_autostart
if [ "$install_autostart" = "y" ] || [ "$install_autostart" = "Y" ]; then
    mkdir -p ~/Library/LaunchAgents
    sed -e "s|__VENV_PYTHON__|$SCRIPT_DIR/.venv/bin/python3|g" \
        -e "s|__SRC_MAIN__|$SCRIPT_DIR/src/main.py|g" \
        -e "s|__LOG_DIR__|$CONFIG_DIR|g" \
        "$SCRIPT_DIR/com.layout-switcher.plist" > ~/Library/LaunchAgents/com.layout-switcher.plist
    launchctl load ~/Library/LaunchAgents/com.layout-switcher.plist
    echo "LaunchAgent installed and loaded."
fi
echo ""
echo "IMPORTANT: Grant permissions in System Settings → Privacy & Security:"
echo "  1. Input Monitoring → enable Python/Terminal"
echo "  2. Accessibility → enable Python/Terminal"
