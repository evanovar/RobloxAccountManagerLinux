#!/usr/bin/env python3
"""
Sober Profile Manager - GTK4 Version
Main entry point for the GTK4 application
"""

import gi
gi.require_version("Gtk", "4.0")
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from src.utils.ui import ProfileManagerApp

def main():
    """Main application entry point"""
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_folder = os.path.join(script_dir, "ProfileManagerData")
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    app = ProfileManagerApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
