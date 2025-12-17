"""
GTK4 UI Module for Sober Profile Manager
Modern Linux-native interface using GTK4
"""

import gi
gi.require_version("Gtk", "4.0")
from gi.repository import Gtk, GLib
import os
import sys
import subprocess
import requests
from pathlib import Path

from classes import ProfileManager


class ProfileRow(Gtk.ListBoxRow):
    """A row representing a single profile in the list"""
    
    def __init__(self, name, manager, refresh_cb, launch_cb):
        super().__init__()
        self.name = name
        self.manager = manager
        self.refresh_cb = refresh_cb
        self.launch_cb = launch_cb
        self.editing = False
        
        self.set_child(self._build_row())
    
    def _build_row(self):
        """Build the row UI"""
        self.main_box = Gtk.Box(
            orientation=Gtk.Orientation.HORIZONTAL,
            spacing=10,
            margin_top=6,
            margin_bottom=6,
            margin_start=6,
            margin_end=6
        )

        self.label = Gtk.Label(label=self.name, xalign=0)
        self.label.set_hexpand(True)
        
        note = self.manager.get_profile_note(self.name)
        show_paths = self.manager.get_setting('show_paths', False)
        
        if show_paths and self.name in self.manager.profiles:
            path = self.manager.profiles[self.name]['path']
            self.label.set_label(f"{self.name}\n<small>{path}</small>")
            self.label.set_use_markup(True)
        elif note:
            self.label.set_label(f"{self.name} • {note}")
        
        self.rename_button = Gtk.Button(label="Rename")
        self.edit_button = Gtk.Button(label="Edit Note")
        self.run_button = Gtk.Button(label="Launch")
        
        self.rename_button.connect("clicked", self.on_rename_clicked)
        self.edit_button.connect("clicked", self.on_edit_clicked)
        self.run_button.connect("clicked", self.on_run_clicked)
        
        self.main_box.append(self.label)
        self.main_box.append(self.rename_button)
        self.main_box.append(self.edit_button)
        
        self.delete_button = Gtk.Button(label="Delete")
        self.delete_button.connect("clicked", self.on_delete_clicked)
        self.main_box.append(self.delete_button)
        
        self.main_box.append(self.run_button)
        
        return self.main_box
    
    def on_rename_clicked(self, button):
        """Handle rename button click"""
        dialog = Gtk.Dialog(title="Rename Profile", transient_for=self.get_root(), modal=True)
        dialog.set_default_size(300, 100)
        content_area = dialog.get_content_area()
        
        entry = Gtk.Entry()
        entry.set_text(self.name)
        entry.set_placeholder_text("Enter new profile name")
        content_area.append(entry)
        
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Rename", Gtk.ResponseType.OK)
        
        def handle_response(d, response):
            if response == Gtk.ResponseType.OK:
                new_name = entry.get_text().strip()
                if not new_name:
                    self.show_error("Profile name cannot be empty.")
                    return
                
                success, message = self.manager.rename_profile(self.name, new_name)
                if success:
                    self.name = new_name
                    self.refresh_cb()
                    d.destroy()
                else:
                    self.show_error(message)
            elif response == Gtk.ResponseType.CANCEL:
                d.destroy()
        
        dialog.connect("response", handle_response)
        dialog.present()
    
    def on_edit_clicked(self, button):
        """Handle edit note button click"""
        current_note = self.manager.get_profile_note(self.name)
        
        dialog = Gtk.Dialog(title="Edit Note", transient_for=self.get_root(), modal=True)
        dialog.set_default_size(400, 150)
        content_area = dialog.get_content_area()
        
        label = Gtk.Label(label=f"Edit note for '{self.name}'")
        content_area.append(label)
        
        scrolled = Gtk.ScrolledWindow()
        scrolled.set_vexpand(True)
        scrolled.set_margin_top(10)
        scrolled.set_margin_bottom(10)
        
        text_view = Gtk.TextView()
        text_view.set_wrap_mode(Gtk.WrapMode.WORD)
        text_buffer = text_view.get_buffer()
        text_buffer.set_text(current_note)
        scrolled.set_child(text_view)
        content_area.append(scrolled)
        
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Save", Gtk.ResponseType.OK)
        
        def handle_response(d, response):
            if response == Gtk.ResponseType.OK:
                start = text_buffer.get_start_iter()
                end = text_buffer.get_end_iter()
                new_note = text_buffer.get_text(start, end, False).strip()
                self.manager.set_profile_note(self.name, new_note)
                self.refresh_cb()
                d.destroy()
            elif response == Gtk.ResponseType.CANCEL:
                d.destroy()
        
        dialog.connect("response", handle_response)
        dialog.present()
    
    def on_delete_clicked(self, button):
        """Handle delete button click"""
        confirm_delete = self.manager.get_setting('confirm_delete', True)
        
        if confirm_delete:
            dialog = Gtk.MessageDialog(
                transient_for=self.get_root(),
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text=f"Delete profile '{self.name}'?"
            )
            dialog.connect("response", lambda d, response: self._handle_delete_response(d, response))
            dialog.present()
        else:
            self.manager.delete_profile(self.name)
            self.refresh_cb()
    
    def _handle_delete_response(self, dialog, response):
        """Handle delete confirmation response"""
        if response == Gtk.ResponseType.OK:
            self.manager.delete_profile(self.name)
            self.refresh_cb()
        dialog.destroy()
    
    def on_run_clicked(self, button):
        """Handle launch button click"""
        self.launch_cb(self.name)
    
    def show_error(self, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self.get_root(),
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=message
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()


class ProfileManagerWindow(Gtk.ApplicationWindow):
    """Main application window"""
    
    def __init__(self, app):
        super().__init__(application=app, title="Sober Profile Manager")
        self.set_default_size(700, 500)
        self.manager = ProfileManager()
        
        main_box = Gtk.Box(orientation=Gtk.Orientation.VERTICAL, spacing=0)
        self.set_child(main_box)
        
        header = Gtk.HeaderBar()
        header.set_show_title_buttons(True)
        self.set_titlebar(header)
        
        settings_button = Gtk.Button(icon_name="preferences-system-symbolic")
        settings_button.connect("clicked", self.on_settings_clicked)
        header.pack_end(settings_button)
        
        content_box = Gtk.Box(
            orientation=Gtk.Orientation.VERTICAL,
            spacing=10,
            margin_top=10,
            margin_bottom=10,
            margin_start=10,
            margin_end=10
        )
        main_box.append(content_box)
        
        base_dir_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        base_dir_label = Gtk.Label(label="Base Directory:", xalign=0)
        base_dir_label.set_markup("<b>Base Directory:</b>")
        
        self.base_dir_display = Gtk.Label(
            label=self.manager.base_directory if self.manager.base_directory else "Not set",
            xalign=0
        )
        self.base_dir_display.set_hexpand(True)
        self.base_dir_display.set_wrap(True)
        self.base_dir_display.set_max_width_chars(50)
        
        set_dir_button = Gtk.Button(label="Set Base Directory")
        set_dir_button.connect("clicked", self.on_set_base_dir)
        
        base_dir_box.append(base_dir_label)
        base_dir_box.append(self.base_dir_display)
        base_dir_box.append(set_dir_button)
        content_box.append(base_dir_box)
        
        separator = Gtk.Separator()
        content_box.append(separator)
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_vexpand(True)
        self.scrolled_window.set_hexpand(True)
        
        self.list_box = Gtk.ListBox()
        self.list_box.set_selection_mode(Gtk.SelectionMode.NONE)
        self.scrolled_window.set_child(self.list_box)
        content_box.append(self.scrolled_window)
        
        button_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=5)
        button_box.set_homogeneous(True)
        
        add_button = Gtk.Button(label="Add Profile")
        add_button.connect("clicked", self.on_add_profile)
        
        launch_place_button = Gtk.Button(label="Launch Place ID")
        launch_place_button.connect("clicked", self.on_launch_place_id)
        
        join_user_button = Gtk.Button(label="Join User")
        join_user_button.connect("clicked", self.on_join_user)
        
        refresh_button = Gtk.Button(label="Refresh")
        refresh_button.connect("clicked", lambda b: self.refresh_profiles())
        
        button_box.append(add_button)
        button_box.append(launch_place_button)
        button_box.append(join_user_button)
        button_box.append(refresh_button)
        content_box.append(button_box)
        
        self.refresh_profiles()
    
    def refresh_profiles(self):
        """Refresh the profile list"""
        while True:
            child = self.list_box.get_first_child()
            if child is None:
                break
            self.list_box.remove(child)
        
        for name in self.manager.profiles.keys():
            row = ProfileRow(name, self.manager, self.refresh_profiles, self.launch_profile)
            self.list_box.append(row)
        
        self.base_dir_display.set_label(
            self.manager.base_directory if self.manager.base_directory else "Not set"
        )
    
    def on_set_base_dir(self, button):
        """Handle set base directory button"""
        dialog = Gtk.FileDialog()
        dialog.select_folder(
            parent=self,
            cancellable=None,
            callback=self._on_folder_selected
        )
    
    def _on_folder_selected(self, dialog, result):
        """Handle folder selection result"""
        try:
            folder = dialog.select_folder_finish(result)
            if folder:
                path = folder.get_path()
                self.manager.save_base_directory(path)
                self.refresh_profiles()
                self.show_info(f"Base directory set to:\n{path}")
        except Exception as e:
            print(f"Folder selection cancelled or error: {e}")
    
    def on_add_profile(self, button):
        """Handle add profile button"""
        if not self.manager.base_directory:
            self.show_warning(
                "Base Directory Required",
                "Please set a base directory first before adding a profile."
            )
            return
        
        dialog = Gtk.Dialog(title="Add Profile", transient_for=self, modal=True)
        dialog.set_default_size(300, 100)
        content_area = dialog.get_content_area()
        
        entry = Gtk.Entry()
        entry.set_placeholder_text("Enter profile name")
        content_area.append(entry)
        
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Add", Gtk.ResponseType.OK)
        
        def handle_response(d, response):
            if response == Gtk.ResponseType.OK:
                name = entry.get_text().strip()
                if not name:
                    self.show_error("Profile name cannot be empty.")
                    return
                
                success, message = self.manager.add_profile(name)
                if success:
                    self.refresh_profiles()
                    d.destroy()
                else:
                    self.show_error(message)
            elif response == Gtk.ResponseType.CANCEL:
                d.destroy()
        
        dialog.connect("response", handle_response)
        dialog.present()
    
    def launch_profile(self, name):
        """Launch Sober with the specified profile"""
        multi_instance = self.manager.get_setting('multi_instance', False)
        if not multi_instance:
            try:
                result = subprocess.run(["flatpak", "ps"], capture_output=True, text=True)
                if result.returncode == 0 and "org.vinegarhq.Sober" in result.stdout:
                    self.show_warning(
                        "Instance Already Running",
                        "A Sober instance is already running.\nEnable multi-instance in settings to launch multiple profiles."
                    )
                    return
            except Exception:
                pass
        
        success = self.manager.launch_sober(name)
        if success:
            if self.manager.get_setting('launch_notifications', True):
                self.show_info(f"Sober launched with profile '{name}'!")
        else:
            self.show_error(f"Failed to launch Sober for profile '{name}'")
    
    def on_launch_place_id(self, button):
        """Handle launch place ID button"""
        if not self.manager.profiles:
            self.show_warning("No Profiles", "Please create a profile first.")
            return
        
        dialog = Gtk.Dialog(title="Launch Place ID", transient_for=self, modal=True)
        dialog.set_default_size(400, 200)
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        
        profile_label = Gtk.Label(label="Select Profile:")
        profile_label.set_xalign(0)
        content_area.append(profile_label)
        
        profile_dropdown = Gtk.DropDown()
        profile_list = Gtk.StringList()
        profile_names = list(self.manager.profiles.keys())
        for profile_name in profile_names:
            profile_list.append(profile_name)
        profile_dropdown.set_model(profile_list)
        
        last_profile = self.manager.get_setting('last_selected_profile', '')
        if last_profile in profile_names:
            profile_dropdown.set_selected(profile_names.index(last_profile))
        
        content_area.append(profile_dropdown)
        
        place_id_label = Gtk.Label(label="Place ID (or full game URL):")
        place_id_label.set_xalign(0)
        content_area.append(place_id_label)
        
        place_id_entry = Gtk.Entry()
        place_id_entry.set_placeholder_text("e.g., 123456789 or https://www.roblox.com/games/123456789")
        
        last_place_id = self.manager.get_setting('last_place_id', '')
        if last_place_id:
            place_id_entry.set_text(last_place_id)
        
        content_area.append(place_id_entry)
        
        private_server_label = Gtk.Label(label="Private Server Code (optional):")
        private_server_label.set_xalign(0)
        content_area.append(private_server_label)
        
        private_server_entry = Gtk.Entry()
        private_server_entry.set_placeholder_text("Leave empty for public server")
        
        last_private_code = self.manager.get_setting('last_private_server_code', '')
        if last_private_code:
            private_server_entry.set_text(last_private_code)
        
        content_area.append(private_server_entry)
        
        separator = Gtk.Separator()
        content_area.append(separator)
        
        favorites_label = Gtk.Label(label="Favorite Games:")
        favorites_label.set_xalign(0)
        content_area.append(favorites_label)
        
        favorites_scroll = Gtk.ScrolledWindow()
        favorites_scroll.set_min_content_height(100)
        favorites_scroll.set_vexpand(True)
        
        favorites_listbox = Gtk.ListBox()
        favorites_listbox.set_selection_mode(Gtk.SelectionMode.SINGLE)
        favorites_scroll.set_child(favorites_listbox)
        content_area.append(favorites_scroll)
        
        def populate_favorites():
            while True:
                child = favorites_listbox.get_first_child()
                if child is None:
                    break
                favorites_listbox.remove(child)
            
            for game in self.manager.get_favorite_games():
                row = Gtk.ListBoxRow()
                box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
                box.set_margin_start(5)
                box.set_margin_end(5)
                box.set_margin_top(5)
                box.set_margin_bottom(5)
                
                label = Gtk.Label(label=game['name'], xalign=0)
                label.set_hexpand(True)
                box.append(label)
                
                delete_btn = Gtk.Button(icon_name="user-trash-symbolic")
                delete_btn.connect("clicked", lambda b, g=game: on_remove_favorite(g))
                box.append(delete_btn)
                
                row.set_child(box)
                favorites_listbox.append(row)
        
        def on_favorite_selected(listbox, row):
            if row is None:
                return
            selected_index = row.get_index()
            favorites = self.manager.get_favorite_games()
            if selected_index < len(favorites):
                game = favorites[selected_index]
                place_id_entry.set_text(game['place_id'])
                private_server_entry.set_text(game.get('private_server_code', '') or '')
        
        def on_remove_favorite(game):
            confirm_dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.OK_CANCEL,
                text=f"Remove '{game['name']}' from favorites?"
            )
            
            def handle_confirm(d, response):
                if response == Gtk.ResponseType.OK:
                    self.manager.remove_favorite_game(game['name'])
                    populate_favorites()
                d.destroy()
            
            confirm_dialog.connect("response", handle_confirm)
            confirm_dialog.present()
        
        favorites_listbox.connect("row-activated", on_favorite_selected)
        populate_favorites()
        
        add_favorite_btn = Gtk.Button(label="⭐ Add to Favorites")
        add_favorite_btn.connect("clicked", lambda b: on_add_to_favorites())
        content_area.append(add_favorite_btn)
        
        def on_add_to_favorites():
            place_id_input = place_id_entry.get_text().strip()
            private_server_code = private_server_entry.get_text().strip() or None
            
            if not place_id_input:
                self.show_error("Please enter a Place ID first.")
                return
            
            import re
            match = re.search(r'(?:games/|placeId=)(\d+)', place_id_input)
            if match:
                place_id = match.group(1)
            elif place_id_input.isdigit():
                place_id = place_id_input
            else:
                self.show_error("Invalid Place ID or URL format.")
                return
            
            try:
                import requests
                api_url = f"https://apis.roblox.com/universes/v1/places/{place_id}/universe"
                response = requests.get(api_url, timeout=5)
                
                if response.status_code == 200:
                    universe_id = response.json().get('universeId')
                    if universe_id:
                        api_url = f"https://games.roblox.com/v1/games?universeIds={universe_id}"
                        response = requests.get(api_url, timeout=5)
                        if response.status_code == 200:
                            data = response.json()
                            if data.get('data') and len(data['data']) > 0:
                                game_name = data['data'][0].get('name', f"Place {place_id}")
                            else:
                                game_name = f"Place {place_id}"
                        else:
                            game_name = f"Place {place_id}"
                    else:
                        game_name = f"Place {place_id}"
                else:
                    game_name = f"Place {place_id}"
            except Exception as e:
                print(f"[WARNING] Failed to fetch game name: {e}")
                game_name = f"Place {place_id}"
            
            if private_server_code:
                game_name += " (Private)"
            
            success, message = self.manager.add_favorite_game(game_name, place_id, private_server_code)
            if success:
                populate_favorites()
                self.show_info(f"Added '{game_name}' to favorites!")
            else:
                self.show_error(message)
        
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Launch", Gtk.ResponseType.OK)
        
        def handle_response(d, response):
            if response == Gtk.ResponseType.OK:
                selected_index = profile_dropdown.get_selected()
                profile_names = list(self.manager.profiles.keys())
                if selected_index >= len(profile_names):
                    self.show_error("Please select a profile.")
                    return
                
                profile_name = profile_names[selected_index]
                
                self.manager.set_setting('last_selected_profile', profile_name)
                
                place_id_input = place_id_entry.get_text().strip()
                private_server_code = private_server_entry.get_text().strip() or None
                
                if not place_id_input:
                    self.show_error("Place ID cannot be empty.")
                    return
                
                import re
                match = re.search(r'(?:games/|placeId=)(\d+)', place_id_input)
                if match:
                    place_id = match.group(1)
                elif place_id_input.isdigit():
                    place_id = place_id_input
                else:
                    self.show_error("Invalid Place ID or URL format.")
                    return
                
                self.manager.set_setting('last_place_id', place_id_input)
                self.manager.set_setting('last_private_server_code', private_server_code or '')
                
                success = self.manager.launch_sober_with_place_id(profile_name, place_id, private_server_code)
                if success:
                    msg = f"Launching profile '{profile_name}' with place ID {place_id}"
                    if private_server_code:
                        msg += f" (Private Server)"
                    self.show_info(msg)
                    d.destroy()
                else:
                    self.show_error(f"Failed to launch Sober for profile '{profile_name}'")
            elif response == Gtk.ResponseType.CANCEL:
                d.destroy()
        
        dialog.connect("response", handle_response)
        dialog.present()
    
    def on_join_user(self, button):
        """Handle join user button"""
        if not self.manager.profiles:
            self.show_warning("No Profiles", "Please create a profile first.")
            return
        
        dialog = Gtk.Dialog(title="Join User", transient_for=self, modal=True)
        dialog.set_default_size(400, 150)
        content_area = dialog.get_content_area()
        content_area.set_spacing(10)
        content_area.set_margin_top(10)
        content_area.set_margin_bottom(10)
        content_area.set_margin_start(10)
        content_area.set_margin_end(10)
        
        profile_label = Gtk.Label(label="Select Profile:")
        profile_label.set_xalign(0)
        content_area.append(profile_label)
        
        profile_dropdown = Gtk.DropDown()
        profile_list = Gtk.StringList()
        profile_names = list(self.manager.profiles.keys())
        for profile_name in profile_names:
            profile_list.append(profile_name)
        profile_dropdown.set_model(profile_list)
        
        last_profile = self.manager.get_setting('last_selected_profile', '')
        if last_profile in profile_names:
            profile_dropdown.set_selected(profile_names.index(last_profile))
        
        content_area.append(profile_dropdown)
        
        username_label = Gtk.Label(label="Roblox Username:")
        username_label.set_xalign(0)
        content_area.append(username_label)
        
        username_entry = Gtk.Entry()
        username_entry.set_placeholder_text("Enter Roblox username to join")
        content_area.append(username_entry)
        
        dialog.add_button("Cancel", Gtk.ResponseType.CANCEL)
        dialog.add_button("Join", Gtk.ResponseType.OK)
        
        def handle_response(d, response):
            if response == Gtk.ResponseType.OK:
                selected_index = profile_dropdown.get_selected()
                profile_names_list = list(self.manager.profiles.keys())
                if selected_index >= len(profile_names_list):
                    self.show_error("Please select a profile.")
                    return
                
                profile_name = profile_names_list[selected_index]
                username = username_entry.get_text().strip()
                
                self.manager.set_setting('last_selected_profile', profile_name)
                
                if not username:
                    self.show_error("Username cannot be empty.")
                    return
                
                d.destroy()
                success, message = self.manager.launch_sober_join_user(profile_name, username)
                if success:
                    self.show_info(f"Launching Sober to join {username}!")
                else:
                    self.show_error(f"Failed to join user:\n{message}")
            elif response == Gtk.ResponseType.CANCEL:
                d.destroy()
        
        dialog.connect("response", handle_response)
        dialog.present()
    
    def on_settings_clicked(self, button):
        """Handle settings button click"""
        dialog = Gtk.Dialog(title="Settings", transient_for=self, modal=True)
        dialog.set_default_size(500, 400)
        content_area = dialog.get_content_area()
        content_area.set_spacing(15)
        content_area.set_margin_top(15)
        content_area.set_margin_bottom(15)
        content_area.set_margin_start(15)
        content_area.set_margin_end=15
        
        title_label = Gtk.Label()
        title_label.set_markup("<big><b>Sober Profile Manager Settings</b></big>")
        content_area.append(title_label)
        
        separator1 = Gtk.Separator()
        content_area.append(separator1)
        
        multi_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        multi_label = Gtk.Label(label="Enable Multi-Instance (unstable)")
        multi_label.set_xalign(0)
        multi_label.set_hexpand(True)
        multi_label.set_tooltip_text("Allow launching multiple Sober instances simultaneously")
        
        multi_switch = Gtk.Switch()
        multi_switch.set_active(self.manager.get_setting('multi_instance', False))
        multi_switch.connect("state-set", self.on_multi_instance_changed)
        
        multi_box.append(multi_label)
        multi_box.append(multi_switch)
        content_area.append(multi_box)
        
        refresh_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        refresh_label = Gtk.Label(label="Auto-Refresh Profiles")
        refresh_label.set_xalign(0)
        refresh_label.set_hexpand(True)
        refresh_label.set_tooltip_text("Automatically refresh profile list when window gains focus")
        
        refresh_switch = Gtk.Switch()
        refresh_switch.set_active(self.manager.get_setting('auto_refresh', True))
        refresh_switch.connect("state-set", lambda w, s: self.manager.set_setting('auto_refresh', s))
        
        refresh_box.append(refresh_label)
        refresh_box.append(refresh_switch)
        content_area.append(refresh_box)
        
        delete_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        delete_label = Gtk.Label(label="Confirm Profile Deletion")
        delete_label.set_xalign(0)
        delete_label.set_hexpand(True)
        delete_label.set_tooltip_text("Ask for confirmation before deleting profiles")
        
        delete_switch = Gtk.Switch()
        delete_switch.set_active(self.manager.get_setting('confirm_delete', True))
        delete_switch.connect("state-set", lambda w, s: self.manager.set_setting('confirm_delete', s))
        
        delete_box.append(delete_label)
        delete_box.append(delete_switch)
        content_area.append(delete_box)
        
        paths_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        paths_label = Gtk.Label(label="Show Profile Paths")
        paths_label.set_xalign(0)
        paths_label.set_hexpand(True)
        paths_label.set_tooltip_text("Display full profile paths in the list")
        
        paths_switch = Gtk.Switch()
        paths_switch.set_active(self.manager.get_setting('show_paths', False))
        paths_switch.connect("state-set", lambda w, s: self.on_show_paths_changed(s))
        
        paths_box.append(paths_label)
        paths_box.append(paths_switch)
        content_area.append(paths_box)
        
        notif_box = Gtk.Box(orientation=Gtk.Orientation.HORIZONTAL, spacing=10)
        notif_label = Gtk.Label(label="Launch Notifications")
        notif_label.set_xalign(0)
        notif_label.set_hexpand(True)
        notif_label.set_tooltip_text("Show notification when launching Sober")
        
        notif_switch = Gtk.Switch()
        notif_switch.set_active(self.manager.get_setting('launch_notifications', True))
        notif_switch.connect("state-set", lambda w, s: self.manager.set_setting('launch_notifications', s))
        
        notif_box.append(notif_label)
        notif_box.append(notif_switch)
        content_area.append(notif_box)
        
        separator2 = Gtk.Separator()
        content_area.append(separator2)
        
        update_button = Gtk.Button(label="Check for Updates")
        update_button.connect("clicked", lambda b: self.check_for_updates())
        content_area.append(update_button)
        
        separator3 = Gtk.Separator()
        content_area.append(separator3)
        
        about_label = Gtk.Label()
        about_label.set_markup(
            "<b>Sober Profile Manager</b> v1.0.2-Linux\n\n"
            "Made by evanovar\n\n"
        )
        about_label.set_justify(Gtk.Justification.CENTER)
        content_area.append(about_label)
        
        dialog.add_button("Close", Gtk.ResponseType.CLOSE)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
    
    def check_for_updates(self):
        """Check for and apply updates"""
        import os
        import requests
        
        script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "update.sh")
        
        if not os.path.exists(script_path):
            self.show_error("Update script not found.\nPlease update manually with:\ngit pull origin main")
            return
        
        try:
            response = requests.get(
                "https://raw.githubusercontent.com/evanovar/RobloxAccountManagerLinux/main/version.txt",
                timeout=5
            )
            
            if response.status_code != 200:
                self.show_error("Failed to check for updates.\nCouldn't connect to GitHub.")
                return
            
            remote_version = response.text.strip()
            current_version = self.get_application().version
            
            if remote_version == current_version:
                self.show_info(f"Already up to date!\n\nYou are running version {current_version}")
                return
            
            dialog = Gtk.MessageDialog(
                transient_for=self,
                modal=True,
                message_type=Gtk.MessageType.QUESTION,
                buttons=Gtk.ButtonsType.YES_NO,
                text=f"Update Available!"
            )
            dialog.set_property("secondary-text", 
                f"Current version: {current_version}\nNew version: {remote_version}\n\nDo you want to update now?")
            
            response_id = dialog.run()
            dialog.destroy()
            
            if response_id != Gtk.ResponseType.YES:
                return
            
            terminal_emulators = [
                ["konsole", "-e"],
                ["gnome-terminal", "--"],
                ["xterm", "-e"],
                ["alacritty", "-e"],
                ["kitty", "-e"]
            ]
            
            terminal_found = False
            for terminal in terminal_emulators:
                if subprocess.run(["which", terminal[0]], capture_output=True).returncode == 0:
                    subprocess.Popen(terminal + ["bash", script_path])
                    terminal_found = True
                    break
            
            if not terminal_found:
                self.show_error("No terminal emulator found.\nPlease run manually:\nbash update.sh")
            else:
                self.show_info("Update script launched in terminal.\nFollow the instructions there.")
                
        except requests.RequestException as e:
            self.show_error(f"Failed to check for updates:\n{e}\n\nCheck your internet connection.")
        except Exception as e:
            self.show_error(f"Failed to check for updates:\n{e}")
    
    def on_multi_instance_changed(self, switch, state):
        """Handle multi-instance setting change"""
        self.manager.set_setting('multi_instance', state)
        if state:
            self.show_info("Multi-instance enabled!\nYou can now launch multiple Sober profiles simultaneously.")
        else:
            self.show_info("Multi-instance disabled.\nOnly one Sober instance can run at a time.")
        return False
    
    def on_show_paths_changed(self, state):
        """Handle show paths setting change"""
        self.manager.set_setting('show_paths', state)
        self.refresh_profiles()
    
    def show_info(self, message):
        """Show info dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.INFO,
            buttons=Gtk.ButtonsType.CLOSE,
            text=message
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
    
    def show_warning(self, title, message):
        """Show warning dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.WARNING,
            buttons=Gtk.ButtonsType.CLOSE,
            text=title
        )
        dialog.format_secondary_text(message)
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()
    
    def show_error(self, message):
        """Show error dialog"""
        dialog = Gtk.MessageDialog(
            transient_for=self,
            modal=True,
            message_type=Gtk.MessageType.ERROR,
            buttons=Gtk.ButtonsType.CLOSE,
            text=message
        )
        dialog.connect("response", lambda d, r: d.destroy())
        dialog.present()


class ProfileManagerApp(Gtk.Application):
    """GTK Application"""
    
    def __init__(self):
        super().__init__(application_id="com.evanovar.SoberProfileManager")
        self.version = "1.0.3"
    
    def do_activate(self):
        """Application activation"""
        win = ProfileManagerWindow(self)
        win.present()
