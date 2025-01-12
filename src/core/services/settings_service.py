"""Settings service for managing game configuration and user preferences."""
from typing import Dict, Any, Optional
import json
import os

class SettingsService:
    """Service for managing game settings and user preferences.
    
    Provides:
    - Settings persistence
    - Default settings management
    - User preference handling
    - Settings validation
    - Hot reloading
    """
    
    def __init__(self, save_path: str = "data/settings.json"):
        """Initialize the settings service.
        
        Args:
            save_path: Path to save settings file
        """
        self._save_path = save_path
        self._settings: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {
            "display": {
                "width": 800,
                "height": 600,
                "fullscreen": False,
                "vsync": True
            },
            "controls": {
                "scheme": "arrows",  # or "wasd"
                "shoot_key": "space"
            },
            "gameplay": {
                "difficulty": "normal",
                "starting_lives": 3,
                "max_asteroids": 12
            },
            "graphics": {
                "particles_enabled": True,
                "debug_visuals": False
            }
        }
        self._ensure_save_directory()
        self.load_settings()
        print("SettingsService initialized")
        
    def _ensure_save_directory(self) -> None:
        """Ensure the save directory exists."""
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        
    def load_settings(self) -> None:
        """Load settings from file or create with defaults."""
        try:
            if os.path.exists(self._save_path):
                with open(self._save_path, 'r') as f:
                    loaded = json.load(f)
                    # Merge with defaults to ensure all settings exist
                    self._settings = self._merge_settings(self._defaults, loaded)
                print("Settings loaded and merged with defaults")
            else:
                self._settings = self._defaults.copy()
                self.save_settings()
                print("Created new settings with defaults")
        except Exception as e:
            print(f"Error loading settings: {e}")
            self._settings = self._defaults.copy()
            
    def _merge_settings(self, defaults: Dict[str, Any], loaded: Dict[str, Any]) -> Dict[str, Any]:
        """Merge loaded settings with defaults to ensure all settings exist.
        
        Args:
            defaults: Default settings
            loaded: Loaded settings to merge
            
        Returns:
            Merged settings dictionary
        """
        result = defaults.copy()
        for key, value in loaded.items():
            if key in result and isinstance(value, dict) and isinstance(result[key], dict):
                result[key] = self._merge_settings(result[key], value)
            else:
                result[key] = value
        return result
            
    def save_settings(self) -> None:
        """Save current settings to file."""
        try:
            with open(self._save_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
            print("Settings saved")
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get_setting(self, category: str, name: str) -> Optional[Any]:
        """Get a specific setting value.
        
        Args:
            category: Setting category
            name: Setting name
            
        Returns:
            Setting value or None if not found
        """
        try:
            return self._settings[category][name]
        except KeyError:
            print(f"Setting not found: {category}.{name}")
            return None
            
    def set_setting(self, category: str, name: str, value: Any) -> bool:
        """Set a specific setting value.
        
        Args:
            category: Setting category
            name: Setting name
            value: New setting value
            
        Returns:
            True if setting was updated
        """
        try:
            if category in self._settings and name in self._settings[category]:
                self._settings[category][name] = value
                self.save_settings()
                print(f"Updated setting: {category}.{name} = {value}")
                return True
            else:
                print(f"Invalid setting: {category}.{name}")
                return False
        except Exception as e:
            print(f"Error setting value: {e}")
            return False
            
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self._settings = self._defaults.copy()
        self.save_settings()
        print("Settings reset to defaults")
        
    def get_all_settings(self) -> Dict[str, Any]:
        """Get all current settings.
        
        Returns:
            Dictionary of all settings
        """
        return self._settings.copy()
        
    def validate_settings(self) -> bool:
        """Validate current settings against defaults structure.
        
        Returns:
            True if settings are valid
        """
        try:
            return self._validate_dict(self._defaults, self._settings)
        except Exception as e:
            print(f"Settings validation error: {e}")
            return False
            
    def _validate_dict(self, template: Dict[str, Any], target: Dict[str, Any]) -> bool:
        """Recursively validate dictionary structure.
        
        Args:
            template: Template dictionary
            target: Target dictionary to validate
            
        Returns:
            True if target matches template structure
        """
        for key, value in template.items():
            if key not in target:
                return False
            if isinstance(value, dict):
                if not isinstance(target[key], dict):
                    return False
                if not self._validate_dict(value, target[key]):
                    return False
        return True 