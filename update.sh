#!/bin/bash

echo "==================================="
echo "Sober Profile Manager - Updater"
echo "==================================="
echo ""

if ! command -v git &> /dev/null; then
    echo "Error: git is not installed. Please install git first."
    echo "  Arch/Manjaro: sudo pacman -S git"
    echo "  Ubuntu/Debian: sudo apt install git"
    echo "  Fedora: sudo dnf install git"
    exit 1
fi

if [ ! -d .git ]; then
    echo "Error: Not a git repository. Cannot update."
    echo "Please clone the repository using:"
    echo "  git clone https://github.com/evanovar/RobloxAccountManagerLinux.git"
    exit 1
fi

echo "Fetching latest changes from GitHub..."
git fetch origin

CURRENT_BRANCH=$(git rev-parse --abbrev-ref HEAD)
echo "Current branch: $CURRENT_BRANCH"

LOCAL=$(git rev-parse @)
REMOTE=$(git rev-parse @{u})

if [ "$LOCAL" = "$REMOTE" ]; then
    echo ""
    echo "✓ You are already up to date!"
    exit 0
fi

echo ""
echo "Updates available!"
echo ""

echo "Changes to be pulled:"
git log HEAD..@{u} --oneline --decorate --color

echo ""
read -p "Do you want to update? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo ""
    echo "Backing up your data..."
    
    if [ -d "ProfileManagerData" ]; then
        BACKUP_DIR="ProfileManagerData_backup_$(date +%Y%m%d_%H%M%S)"
        cp -r ProfileManagerData "$BACKUP_DIR"
        echo "✓ Backup created: $BACKUP_DIR"
    fi
    
    echo ""
    echo "Pulling latest changes..."
    
    if git pull origin "$CURRENT_BRANCH"; then
        echo ""
        echo "✓ Update successful!"
        echo ""
        
        if git diff HEAD@{1} HEAD --name-only | grep -q "requirements.txt"; then
            echo "Dependencies may have changed. Updating..."
            if command -v pip &> /dev/null; then
                pip install -r requirements.txt --upgrade
                echo "✓ Dependencies updated!"
            else
                echo "⚠ Warning: pip not found. Please manually run:"
                echo "    pip install -r requirements.txt --upgrade"
            fi
        fi
        
        echo ""
        echo "==================================="
        echo "Update complete! You can now run:"
        echo "  python main.py"
        echo "==================================="
    else
        echo ""
        echo "✗ Update failed. There may be conflicts."
        echo "If you have local changes, try:"
        echo "  git stash        # Save your changes"
        echo "  git pull         # Update"
        echo "  git stash pop    # Restore your changes"
        exit 1
    fi
else
    echo "Update cancelled."
    exit 0
fi
