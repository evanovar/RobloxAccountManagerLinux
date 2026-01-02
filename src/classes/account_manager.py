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
        
        self.running_processes = {}
        
        self.profiles = self.load_profiles()
        self.base_directory = self.load_base_directory()
        
        if not self.base_directory:
            default_base = Path(self.data_folder) / "Profiles"
            default_base.mkdir(parents=True, exist_ok=True)
            self.save_base_directory(str(default_base))
    
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
        
        profile_path = Path(self.profiles[profile_name]['path'])
        
        if profile_path.exists():
            try:
                import shutil
                shutil.rmtree(profile_path)
                print(f"[SUCCESS] Deleted profile directory: {profile_path}")
            except Exception as e:
                print(f"[WARNING] Failed to delete profile directory: {e}")
        
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
            proc = subprocess.Popen(
                ["env", f"HOME={profile_path}", "flatpak", "run", "org.vinegarhq.Sober"],
                preexec_fn=os.setsid,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            self.running_processes[profile_name] = proc
            
            print(f"[SUCCESS] Sober launched with profile: {profile_name}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to launch Sober: {e}")
            return False
    
    def is_profile_running(self, profile_name):
        """Check if a specific profile is currently running"""
        if profile_name not in self.profiles:
            return False
        
        profile_path = self.profiles[profile_name]['path']
        
        try:
            result = subprocess.run(
                ["flatpak", "ps"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "org.vinegarhq.Sober" in line and profile_path in line:
                        return True
            
            result = subprocess.run(
                ["ps", "aux"], 
                capture_output=True, 
                text=True
            )
            
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if "org.vinegarhq.Sober" in line and f'HOME={profile_path}' in line:
                        return True
                        
        except Exception as e:
            print(f"[WARNING] Could not check if profile is running: {e}")
        
        return False
    
    def kill_profile(self, profile_name):
        """Kill a specific profile's Sober instance"""
        if profile_name in self.running_processes:
            proc = self.running_processes[profile_name]
            if proc.poll() is None:
                try:
                    proc.terminate()
                    proc.wait(timeout=2)
                    print(f"[INFO] Terminated tracked process for '{profile_name}'")
                except:
                    try:
                        proc.kill()
                        print(f"[INFO] Force killed tracked process for '{profile_name}'")
                    except Exception as e:
                        print(f"[WARNING] Failed to kill tracked process: {e}")
            del self.running_processes[profile_name]
        
        active_profiles = [name for name, proc in self.running_processes.items() if proc.poll() is None]
        if not active_profiles:
            try:
                subprocess.run(["flatpak", "kill", "org.vinegarhq.Sober"], capture_output=True)
                print(f"[INFO] Ran flatpak kill as backup")
            except Exception as e:
                print(f"[WARNING] flatpak kill failed: {e}")
    
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
    
    def is_profile_logged_in(self, profile_name):
        """Check if profile has a valid .ROBLOSECURITY cookie"""
        if profile_name not in self.profiles:
            return False
        
        profile_path = Path(self.profiles[profile_name]['path'])
        cookie_file = profile_path / ".var" / "app" / "org.vinegarhq.Sober" / "data" / "sober" / "cookies"
        
        if not cookie_file.exists():
            return False
        
        try:
            with open(cookie_file, 'r') as f:
                content = f.read()
                return '.ROBLOSECURITY=' in content and 'WARNING:-DO-NOT-SHARE-THIS' in content
        except Exception:
            return False
    
    def get_profile_username(self, profile_name):
        """Get Roblox username for a profile by reading cookie and fetching from API"""
        if not self.is_profile_logged_in(profile_name):
            return None
        
        profile_path = Path(self.profiles[profile_name]['path'])
        cookie_file = profile_path / ".var" / "app" / "org.vinegarhq.Sober" / "data" / "sober" / "cookies"
        
        try:
            with open(cookie_file, 'r') as f:
                content = f.read()
                if '.ROBLOSECURITY=' in content:
                    cookie_line = [line for line in content.split(';') if '.ROBLOSECURITY=' in line][0]
                    cookie_value = cookie_line.split('.ROBLOSECURITY=')[1].strip()
                    
                    import requests
                    headers = {'Cookie': f'.ROBLOSECURITY={cookie_value}'}
                    response = requests.get('https://users.roblox.com/v1/users/authenticated', headers=headers, timeout=5)
                    
                    if response.status_code == 200:
                        data = response.json()
                        return data.get('name', 'Unknown')
        except Exception as e:
            print(f"[WARNING] Failed to get username: {e}")
        
        return None
    
    def launch_sober_join_user(self, profile_name, username, private_server_input=None):
        """Launch Sober and join a specific user by fetching their job ID, or use private server code"""
        if profile_name not in self.profiles:
            print(f"[ERROR] Profile '{profile_name}' not found")
            return False, "Profile not found"
        
        profile_path = self.profiles[profile_name]['path']
        
        if not os.path.exists(profile_path):
            print(f"[ERROR] Profile directory not found: {profile_path}")
            return False, "Profile directory not found"
        
        cookie_file = Path(profile_path) / ".var" / "app" / "org.vinegarhq.Sober" / "data" / "sober" / "cookies"
        
        if not cookie_file.exists():
            print(f"[ERROR] No cookies found for profile '{profile_name}'")
            return False, "Profile not logged in"
        
        private_server_code = None
        if private_server_input:
            import re
            match = re.search(r'privateServerLinkCode=(\d+)', private_server_input)
            if match:
                private_server_code = match.group(1)
            else:
                private_server_code = private_server_input.strip()
        
        try:
            with open(cookie_file, 'r') as f:
                content = f.read()
                if '.ROBLOSECURITY=' not in content:
                    return False, "Invalid cookie format"
                
                cookie_line = [line for line in content.split(';') if '.ROBLOSECURITY=' in line][0]
                cookie_value = cookie_line.split('.ROBLOSECURITY=')[1].strip()
            
            import requests
            user_response = requests.post(
                'https://users.roblox.com/v1/usernames/users',
                json={"usernames": [username], "excludeBannedUsers": True},
                timeout=5
            )
            
            if user_response.status_code != 200:
                return False, "Failed to find user"
            
            user_data = user_response.json()
            if not user_data.get('data') or len(user_data['data']) == 0:
                return False, f"User '{username}' not found"
            
            user_id = user_data['data'][0]['id']
            
            csrf_response = requests.post(
                'https://auth.roblox.com/v2/logout',
                headers={'Cookie': f'.ROBLOSECURITY={cookie_value}'},
                timeout=5
            )
            csrf_token = csrf_response.headers.get('x-csrf-token', '')
            
            presence_response = requests.post(
                'https://presence.roblox.com/v1/presence/users',
                headers={
                    'Cookie': f'.ROBLOSECURITY={cookie_value}',
                    'Content-Type': 'application/json',
                    'X-CSRF-TOKEN': csrf_token
                },
                json={"userIds": [user_id]},
                timeout=5
            )
            
            if presence_response.status_code != 200:
                return False, "Failed to get user presence"
            
            presence_data = presence_response.json()
            if not presence_data.get('userPresences') or len(presence_data['userPresences']) == 0:
                return False, "User presence not found"
            
            presence = presence_data['userPresences'][0]
            
            if presence.get('userPresenceType') != 2:
                return False, f"{username} is not currently in a game"
            
            place_id = presence.get('placeId')
            job_id = presence.get('gameId')
            
            if not place_id:
                return False, "Could not get game information"
            
            if private_server_code:
                roblox_uri = f"roblox://placeId={place_id}&linkCode={private_server_code}"
                print(f"[INFO] Joining {username} in place {place_id} with private server code {private_server_code}")
            else:
                if not job_id:
                    return False, "Could not get game instance ID. Try providing a private server code if this is a VIP server."
                roblox_uri = f"roblox://experiences/start?placeId={place_id}&gameInstanceId={job_id}"
                print(f"[INFO] Joining {username} in place {place_id}, job {job_id}")
            
            proc = subprocess.Popen(
                ["env", f"HOME={profile_path}", "flatpak", "run", "org.vinegarhq.Sober", roblox_uri],
                preexec_fn=os.setsid,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            self.running_processes[profile_name] = proc
            
            print(f"[SUCCESS] Launched Sober to join {username}")
            return True, f"Joining {username}"
            
        except requests.RequestException as e:
            print(f"[ERROR] Network error: {e}")
            return False, "Network error - check your connection"
        except Exception as e:
            print(f"[ERROR] Failed to launch: {e}")
            return False, str(e)
    
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
    
    def launch_sober_with_place_id(self, profile_name, place_id, private_server_input=None):
        """Launch Sober with a specific place ID (and optional private server)"""
        if profile_name not in self.profiles:
            print(f"[ERROR] Profile '{profile_name}' not found")
            return False
        
        profile_path = self.profiles[profile_name]['path']
        
        if not os.path.exists(profile_path):
            print(f"[ERROR] Profile directory not found: {profile_path}")
            return False
        
        private_server_code = None
        url_place_id = None
        
        if private_server_input:
            import re
            
            if 'roblox.com/games/' in private_server_input or 'privateServerLinkCode=' in private_server_input:
                place_match = re.search(r'games/(\d+)', private_server_input)
                if place_match:
                    url_place_id = place_match.group(1)
                
                code_match = re.search(r'privateServerLinkCode=([\d]+)', private_server_input)
                if code_match:
                    private_server_code = code_match.group(1)
                
                if not place_id or str(place_id).strip() == '':
                    if url_place_id:
                        place_id = url_place_id
                        print(f"[INFO] Using place ID from URL: {place_id}")
                    else:
                        print(f"[ERROR] Could not extract place ID from URL")
                        return False
                elif url_place_id and str(place_id) != url_place_id:
                    print(f"[ERROR] Place ID mismatch: Input={place_id}, URL={url_place_id}")
                    return False
            else:
                private_server_code = private_server_input.strip()
        
        if not place_id or str(place_id).strip() == '':
            print(f"[ERROR] Place ID is required")
            return False
        
        if private_server_code:
            roblox_uri = f"roblox://placeId={place_id}&linkCode={private_server_code}"
        else:
            roblox_uri = f"roblox://experiences/start?placeId={place_id}"
        
        print(f"[INFO] Launching Sober with profile: {profile_name}, URI: {roblox_uri}")
        
        try:
            proc = subprocess.Popen(
                ["env", f"HOME={profile_path}", "flatpak", "run", "org.vinegarhq.Sober", roblox_uri],
                preexec_fn=os.setsid,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                stdin=subprocess.DEVNULL
            )
            self.running_processes[profile_name] = proc
            
            print(f"[SUCCESS] Sober launched with profile: {profile_name} and place ID: {place_id}")
            return True
            
        except Exception as e:
            print(f"[ERROR] Failed to launch Sober: {e}")
            return False
