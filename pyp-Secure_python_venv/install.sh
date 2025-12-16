#!/bin/bash

# pyp Installation Script
# This script installs the pyp Python virtual environment manager

set -e

echo "🚀 Installing pyp - Python Virtual Environment Manager"
echo "======================================================"

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PYP_SOURCE="$SCRIPT_DIR/pyp.py"

# Check if pyp.py exists
if [ ! -f "$PYP_SOURCE" ]; then
    echo "❌ Error: pyp.py not found in $SCRIPT_DIR"
    echo "Please make sure pyp.py is in the same directory as this installation script."
    exit 1
fi

# Make pyp.py executable
chmod +x "$PYP_SOURCE"
echo "✓ Made pyp.py executable"

# Ask user for installation method
echo
echo "Choose installation method:"
echo "1) Create symlink in /usr/local/bin (requires sudo)"
echo "2) Create symlink in ~/.local/bin (recommended)"
echo "3) Add alias to shell profile"
echo "4) Just copy the script (you'll need to run it with python3)"
echo
read -p "Enter your choice (1-4): " choice

case $choice in
    1)
        # System-wide installation
        echo "Installing to /usr/local/bin..."
        if sudo ln -sf "$PYP_SOURCE" /usr/local/bin/pyp; then
            echo "✓ Successfully installed pyp to /usr/local/bin/pyp"
            echo "You can now use 'pyp' command from anywhere"
        else
            echo "❌ Failed to install to /usr/local/bin. Try running with sudo or choose option 2."
            exit 1
        fi
        ;;
    2)
        # User-local installation
        mkdir -p ~/.local/bin
        if ln -sf "$PYP_SOURCE" ~/.local/bin/pyp; then
            echo "✓ Successfully installed pyp to ~/.local/bin/pyp"
            echo "Make sure ~/.local/bin is in your PATH:"
            echo "  export PATH=\"\$HOME/.local/bin:\$PATH\""
            echo "Add this line to your ~/.bashrc or ~/.zshrc"
        else
            echo "❌ Failed to install to ~/.local/bin"
            exit 1
        fi
        ;;
    3)
        # Alias installation
        echo "Setting up alias..."
        alias_line="alias pyp='python3 $PYP_SOURCE'"
        
        # Detect shell and add to appropriate profile
        if [ -n "$BASH_VERSION" ]; then
            profile_file="$HOME/.bashrc"
        elif [ -n "$ZSH_VERSION" ]; then
            profile_file="$HOME/.zshrc"
        else
            profile_file="$HOME/.profile"
        fi
        
        if ! grep -q "alias pyp=" "$profile_file" 2>/dev/null; then
            echo "" >> "$profile_file"
            echo "# pyp - Python Virtual Environment Manager" >> "$profile_file"
            echo "$alias_line" >> "$profile_file"
            echo "✓ Added alias to $profile_file"
            echo "Restart your shell or run: source $profile_file"
        else
            echo "✓ pyp alias already exists in $profile_file"
        fi
        ;;
    4)
        # Just copy the script
        cp "$PYP_SOURCE" "./pyp"
        chmod +x "./pyp"
        echo "✓ Copied pyp.py to ./pyp"
        echo "Run it with: python3 pyp.py or ./pyp"
        ;;
    *)
        echo "❌ Invalid choice"
        exit 1
        ;;
esac

echo
echo "🎉 Installation complete!"
echo
echo "Quick start:"
echo "  pyp -b myenv     # Create a new environment"
echo "  pyp -a myenv     # Activate the environment"
echo "  pyp -l           # List all environments"
echo "  pyp -d           # Deactivate environment"
echo
echo "For help: pyp --help"
echo "Documentation: See README.md"

# Test installation
echo
echo "Testing installation..."
if command -v pyp >/dev/null 2>&1; then
    echo "✓ pyp command is available"
    pyp --help >/dev/null && echo "✓ pyp is working correctly"
else
    echo "⚠️  pyp command not found in PATH"
    echo "Make sure the installation directory is in your PATH"
fi