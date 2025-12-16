# Sober Profile Manager

A modern GTK4 profile manager for [Sober](https://sober.vinegarhq.org/) on Linux. Easily manage multiple Roblox profiles with isolated environments.

![License](https://img.shields.io/badge/license-GPL--3.0-blue.svg)
![Python](https://img.shields.io/badge/python-3.7+-green.svg)
![Platform](https://img.shields.io/badge/platform-Linux-orange.svg)

## Features

- 🚀 **Profile Management** - Create, rename, delete, and launch multiple Sober profiles
- 🏠 **Isolated Environments** - Each profile runs with its own HOME directory
- 📝 **Profile Notes** - Add custom notes to organize your profiles
- ⭐ **Favorite Games** - Save your favorite Roblox games with place IDs and private server codes
- 🎮 **Direct Game Launch** - Launch specific games directly from the manager
- 🔧 **Settings** - Configurable multi-instance support, auto-refresh, and more
- 🎨 **Modern GTK4 UI** - Native Linux interface with dark theme support
- 📦 **No Dependencies** - Uses only standard library (except `requests` for game name fetching)

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
git clone https://github.com/evanovar/RobloxAccountManager.git
cd RobloxAccountManager
git checkout linux
```

### 4. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 5. Run the Application

```bash
python main.py
```


## Troubleshooting

### Sober won't launch
- Ensure Sober is installed via Flatpak: `flatpak list | grep Sober`
- Try running manually: `flatpak run org.vinegarhq.Sober`

### Multi-instance not working
- Enable in Settings
- Check if Sober supports multiple instances on your system

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