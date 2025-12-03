#!/bin/bash
# Installation script for Augur Omega CLI

echo "Installing Augur Omega CLI..."

# Create directory for the CLI
CLI_DIR="$HOME/.local/bin"
mkdir -p "$CLI_DIR"

# Copy the CLI script
cp "C:\Users\Dell\Rasa-X-Machina\augur-omega\builds\tui_cli\cli\augur_cli.py" "$CLI_DIR/augur-cli"
chmod +x "$CLI_DIR/augur-cli"

# Create symlink for easier access
ln -sf "$CLI_DIR/augur-cli" "$CLI_DIR/augur"

echo "Augur Omega CLI installed successfully!"
echo "Run 'augur --help' to get started."
