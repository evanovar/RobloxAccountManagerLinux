#!/bin/bash

echo "==================================="
echo "Sober Profile Manager - Updater"
echo "==================================="
echo ""

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR" || exit 1

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
        if cp -r ProfileManagerData "$BACKUP_DIR"; then
            echo "✓ Backup created: $BACKUP_DIR"
        else
            echo "✗ Warning: Backup creation failed"
        fi
    else
        echo "⚠ ProfileManagerData directory not found (nothing to back up)"
    fi
    
    echo ""
    echo "Pulling latest changes..."
    
    if ! git diff-index --quiet HEAD --; then
        echo "⚠ Local changes detected. Stashing them temporarily..."
        git stash
        STASHED=1
    else
        STASHED=0
    fi
    
    git pull origin "$CURRENT_BRANCH"
    GIT_PULL_EXIT=$?
    
    if [ $STASHED -eq 1 ]; then
        echo "Restoring your local changes..."
        git stash pop 2>/dev/null || echo "⚠ Warning: Could not automatically restore changes. Use 'git stash pop' manually."
    fi
    
    if [ $GIT_PULL_EXIT -eq 0 ]; then
        echo ""
        echo "✓ Update successful!"
        echo ""
        
        if git diff HEAD@{1} HEAD --name-only 2>/dev/null | grep -q "requirements.txt"; then
            echo "Dependencies may have changed. Updating..."
            if command -v pip &> /dev/null; then
                pip install -r requirements.txt --upgrade 2>&1
                echo "✓ Dependencies updated!"
            else
                echo "⚠ Warning: pip not found. Please manually run:"
                echo "    pip install -r requirements.txt --upgrade"
            fi
        fi
        
        echo ""
        echo "==================================="
        echo "Update complete!"
        echo ""
        echo "IMPORTANT: Close the app and restart it:"
        echo "  python main.py"
        echo "==================================="
    else
        echo ""
        echo "✗ Update failed (git exit code: $GIT_PULL_EXIT)"
        echo "There may be conflicts or connectivity issues."
        echo "If you have local changes, try:"
        echo "  git stash        # Save your changes"
        echo "  git pull         # Update"
        echo "  git stash pop    # Restore your changes"
        echo ""
        echo "Press Enter to continue..."
        read
        exit 1
    fi
else
    echo "Update cancelled."
    exit 0
fi

echo ""
echo "Press Enter to close this window..."
read
