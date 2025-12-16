"""
Profile Manager class
Handles profile storage and Sober instance management
"""

import os
import json
import subprocess
from pathlib import Path


class ProfileManager:
    
    def __init__(self):
        self.data_folder = "ProfileManagerData"
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        
        self.profiles_file = os.path.join(self.data_folder, "profiles.json")
        self.settings_file = os.path.join(self.data_folder, "settings.json")
        
        self.profiles = self.load_profiles()
        self.base_directory = self.load_base_directory()
        
        if not self.base_directory:
            default_base = Path(self.data_folder) / "Profiles"
            default_base.mkdir(parents=True, exist_ok=True)
            self.save_base_directory(str(default_base))
        
        if not self.profiles:
            self.profiles["Main Profile"] = {
                'name': "Main Profile",
                'path': str(Path.home()),
                'note': ''
            }
            self.save_profiles()
            print("[SUCCESS] Created Main Profile")
    
    def load_profiles(self):
        """Load saved profiles from JSON file"""
        if os.path.exists(self.profiles_file):
            try:
                with open(self.profiles_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                return data if isinstance(data, dict) else {}
            except Exception as e:
                print(f"[WARNING] Error loading profiles: {e}")
                return {}
        return {}
    
    def save_profiles(self):
        """Save profiles to JSON file"""
        with open(self.profiles_file, 'w', encoding='utf-8') as f:
            json.dump(self.profiles, f, indent=2, ensure_ascii=False)
    
    def load_settings(self):
        """Load all settings from settings file"""
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                print(f"[WARNING] Error loading settings: {e}")
        return {}
    
    def save_settings(self, settings):
        """Save all settings to settings file"""
        with open(self.settings_file, 'w', encoding='utf-8') as f:
            json.dump(settings, f, indent=2, ensure_ascii=False)
    
    def get_setting(self, key, default=None):
        """Get a specific setting value"""
        settings = self.load_settings()
        return settings.get(key, default)
    
    def set_setting(self, key, value):
        """Set a specific setting value"""
        settings = self.load_settings()
        settings[key] = value
        self.save_settings(settings)
    
    def load_base_directory(self):
        """Load base directory from settings"""
        base_dir = self.get_setting('base_directory')
        if base_dir:
            return base_dir
        return str(Path(self.data_folder) / "Profiles")
    
    def save_base_directory(self, path):
        """Save base directory to settings"""
        self.set_setting('base_directory', path)
        self.base_directory = path
    
    def add_profile(self, profile_name):
        """Add a new profile"""
        if not self.base_directory:
            return False, "Base directory not set"
        
        if profile_name in self.profiles:
            return False, f"Profile '{profile_name}' already exists"
        
        profile_path = Path(self.base_directory) / profile_name
        
        try:
            profile_path.mkdir(parents=True, exist_ok=False)
            
            self.profiles[profile_name] = {
                'name': profile_name,
                'path': str(profile_path),
                'note': ''
            }
            self.save_profiles()
            
            print(f"[SUCCESS] Created profile: {profile_name}")
            return True, profile_name
            
        except FileExistsError:
            return False, f"Directory for profile '{profile_name}' already exists"
        except Exception as e:
            return False, f"Failed to create profile: {str(e)}"
    
    def delete_profile(self, profile_name):
        """Delete a profile"""
        if profile_name not in self.profiles:
            print(f"[ERROR] Profile '{profile_name}' not found")
            return False
        
        del self.profiles[profile_name]
        self.save_profiles()
        print(f"[SUCCESS] Deleted profile: {profile_name}")
        return True
    
    def rename_profile(self, old_name, new_name):
        """Rename a profile"""
        if old_name not in self.profiles:
            return False, f"Profile '{old_name}' not found"
        
        if new_name in self.profiles:
            return False, f"Profile '{new_name}' already exists"
        
        if not new_name.strip():
            return False, "Profile name cannot be empty"
        
        old_path = Path(self.profiles[old_name]['path'])
        new_path = old_path.parent / new_name
        
        try:
            if old_path.exists():
                old_path.rename(new_path)
            
            self.profiles[new_name] = {
                'name': new_name,
                'path': str(new_path),
                'note': self.profiles[old_name].get('note', '')
            }
            del self.profiles[old_name]
            self.save_profiles()
            
            print(f"[SUCCESS] Renamed profile: {old_name} -> {new_name}")
            return True, new_name
            
        except Exception as e:
            return False, f"Failed to rename profile: {str(e)}"
    
    def launch_sober(self, profile_name):
        """Launch Sober with the specified profile"""
        if profile_name not in self.profiles:
            print(f"[ERROR] Profile '{profile_name}' not found")
            return False
        
        profile_path = self.profiles[profile_name]['path']
        
        if not os.path.exists(profile_path):
            print(f"[ERROR] Profile directory not found: {profile_path}")
            return False
        
        print(f"[INFO] Launching Sober with profile: {profile_name}")
        
        try:
            if profile_name == "Main Profile":
                subprocess.Popen(
                    ["flatpak", "run", "org.vinegarhq.Sober"],
                    preexec_fn=os.setsid,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    ["env", f"HOME={profile_path}", "flatpak", "run", "org.vinegarhq.Sober"],
                    preexec_fn=os.setsid,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            
            print(f"[SUCCESS] Sober launched with profile: {profile_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to launch Sober: {e}")
            return False
    
    def set_profile_note(self, profile_name, note):
        """Set or update note for a profile"""
        if profile_name not in self.profiles:
            print(f"[ERROR] Profile '{profile_name}' not found")
            return False
        
        self.profiles[profile_name]['note'] = note
        self.save_profiles()
        print(f"[SUCCESS] Note updated for profile: {profile_name}")
        return True
    
    def get_profile_note(self, profile_name):
        """Get note for a specific profile"""
        if profile_name in self.profiles:
            return self.profiles[profile_name].get('note', '')
        return ''
    
    def get_favorite_games(self):
        """Get list of favorite games"""
        return self.get_setting('favorite_games', [])
    
    def add_favorite_game(self, name, place_id, private_server_code=None):
        """Add a game to favorites"""
        favorites = self.get_favorite_games()
        
        for game in favorites:
            if game['place_id'] == place_id and game.get('private_server_code') == private_server_code:
                return False, "This game is already in favorites"
        
        favorites.append({
            'name': name,
            'place_id': place_id,
            'private_server_code': private_server_code
        })
        self.set_setting('favorite_games', favorites)
        return True, "Game added to favorites"
    
    def remove_favorite_game(self, name):
        """Remove a game from favorites"""
        favorites = self.get_favorite_games()
        favorites = [g for g in favorites if g['name'] != name]
        self.set_setting('favorite_games', favorites)
        return True
    
    def launch_sober_with_place_id(self, profile_name, place_id, private_server_code=None):
        """Launch Sober with a specific place ID (and optional private server)"""
        if profile_name not in self.profiles:
            print(f"[ERROR] Profile '{profile_name}' not found")
            return False
        
        profile_path = self.profiles[profile_name]['path']
        
        if not os.path.exists(profile_path):
            print(f"[ERROR] Profile directory not found: {profile_path}")
            return False
        
        if private_server_code:
            roblox_uri = f"roblox://placeId={place_id}&linkCode={private_server_code}"
        else:
            roblox_uri = f"roblox://placeId={place_id}"
        
        print(f"[INFO] Launching Sober with profile: {profile_name}, URI: {roblox_uri}")
        
        try:
            if profile_name == "Main Profile":
                subprocess.Popen(
                    ["flatpak", "run", "org.vinegarhq.Sober", roblox_uri],
                    preexec_fn=os.setsid,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            else:
                subprocess.Popen(
                    ["env", f"HOME={profile_path}", "flatpak", "run", "org.vinegarhq.Sober", roblox_uri],
                    preexec_fn=os.setsid,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    stdin=subprocess.DEVNULL
                )
            
            print(f"[SUCCESS] Sober launched with profile: {profile_name} and place ID: {place_id}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to launch Sober: {e}")
            return False
