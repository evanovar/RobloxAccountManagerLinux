#!/usr/bin/env python3
"""
Sober Profile Manager - GTK4 Version
Main entry point for the GTK4 application
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from classes import ProfileManager
from utils.ui import ProfileManagerWindow, ProfileManagerApp


def main():
    """Main application entry point"""
    data_folder = "ProfileManagerData"
    if not os.path.exists(data_folder):
        os.makedirs(data_folder)
    
    app = ProfileManagerApp()
    return app.run(sys.argv)


if __name__ == "__main__":
    sys.exit(main())
