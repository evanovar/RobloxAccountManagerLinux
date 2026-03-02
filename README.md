# Sober Profile Manager

A modern GTK4 profile manager for [Sober](https://sober.vinegarhq.org/) on Linux. Easily manage multiple Roblox profiles with isolated environments.

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-orange.svg)

> [!IMPORTANT]
> As of right now, I have lost interest on developing on this program, this might change in the future.


## Features

- 🚀 **Profile Management** - Create, rename, delete, and launch multiple Sober profiles
- 🏠 **Isolated Environments** - Each profile runs with its own HOME directory
- 📝 **Profile Notes** - Add custom notes to organize your profiles
- ⭐ **Favorite Games** - Save your favorite Roblox games with place IDs and private server codes
- 🎮 **Direct Game Launch** - Launch specific games directly from the manager
- 🔧 **Settings** - Configurable multi-instance support, auto-refresh, and more
- 🎨 **Modern GTK4 UI** - Native Linux interface with dark theme support

## Requirements

- **Linux** (tested on Arch Linux with Hyprland)<br>
<sup> i use arch btw </sup>
- **Python 3.7+**
- **GTK4** and Python GObject bindings
- **Flatpak** with **Sober** installed (`org.vinegarhq.Sober`)

## Installation

### 1. Install System Dependencies

**Arch Linux / Manjaro:**
```bash
sudo pacman -S python-gobject gtk4
```

**Ubuntu / Debian:**
```bash
sudo apt install python3-gi gir1.2-gtk-4.0
```

**Fedora:**
```bash
sudo dnf install python3-gobject gtk4
```

### 2. Install Sober via Flatpak

```bash
flatpak install flathub org.vinegarhq.Sober
```

### 3. Clone the Repository

```bash
git clone https://github.com/evanovar/RobloxAccountManagerLinux.git
cd RobloxAccountManagerLinux
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python main.py
```

## Updating

### Method 1: Using the Built-in Updater (Recommended)

1. Open the application
2. Click the settings icon (⚙️) in the header bar
3. Click **"Check for Updates"**
4. Follow the instructions in the terminal

### Method 2: Using the Update Script

```bash
bash update.sh
```

The update script will:
- Check for updates from GitHub
- Show you what changed
- Backup your ProfileManagerData
- Pull the latest changes
- Update dependencies if needed

### Method 3: Manual Update

```bash
git pull origin main
pip install -r requirements.txt --upgrade
```

**Note**: Your profile data in `ProfileManagerData/` is preserved during updates and backed up automatically.

## Troubleshooting

### Sober won't launch
- Ensure Sober is installed via Flatpak: `flatpak list | grep Sober`
- Try running manually: `flatpak run org.vinegarhq.Sober`

### Game names not fetching
- Ensure `requests` library is installed: `pip install requests`
- Check your internet connection

### Profiles not appearing
- Click the refresh button
- Enable "Auto-Refresh Profiles" in settings
- Check that profile directories exist in base directory

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📄 License

GNU General Public License v3.0 - See [LICENSE](LICENSE) file for details

## ⚠️ Disclaimer

This project is not affiliated with or endorsed by Roblox Corporation or VinegarHQ. Use at your own risk.
