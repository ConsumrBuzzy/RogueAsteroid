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
            },
            "high_scores": {
                "max_entries": 5,
                "save_path": "data/high_scores.json"
            },
            "statistics": {
                "save_path": "data/statistics.json"
            },
            "achievements": {
                "save_path": "data/achievements.json"
            }
        }
        
        self._ensure_save_directory()
        self.load_settings()
        print("SettingsService initialized")
        
    def _ensure_save_directory(self) -> None:
        """Ensure the save directory exists."""
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        
    def load_settings(self) -> None:
        """Load settings from file and merge with defaults."""
        try:
            if os.path.exists(self._save_path):
                with open(self._save_path, 'r') as f:
                    loaded_settings = json.load(f)
                    # Deep merge with defaults
                    self._settings = self._deep_merge(self._defaults.copy(), loaded_settings)
            else:
                self._settings = self._defaults.copy()
            print("Settings loaded and merged with defaults")
        except Exception as e:
            print(f"Error loading settings: {e}")
            self._settings = self._defaults.copy()
            
    def save_settings(self) -> None:
        """Save current settings to file."""
        try:
            with open(self._save_path, 'w') as f:
                json.dump(self._settings, f, indent=2)
            print("Settings saved")
        except Exception as e:
            print(f"Error saving settings: {e}")
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a setting value using dot notation.
        
        Args:
            key: Setting key in dot notation (e.g. 'display.width')
            default: Default value if key not found
            
        Returns:
            Setting value or default if not found
        """
        try:
            value = self._settings
            for part in key.split('.'):
                value = value[part]
            return value
        except (KeyError, TypeError):
            return default
            
    def set(self, key: str, value: Any) -> None:
        """Set a setting value using dot notation.
        
        Args:
            key: Setting key in dot notation (e.g. 'display.width')
            value: Value to set
        """
        parts = key.split('.')
        target = self._settings
        
        # Navigate to the correct nested dictionary
        for part in parts[:-1]:
            if part not in target:
                target[part] = {}
            target = target[part]
            
        # Set the value
        target[parts[-1]] = value
        self.save_settings()
        
    def reset_to_defaults(self) -> None:
        """Reset all settings to defaults."""
        self._settings = self._defaults.copy()
        self.save_settings()
        print("Settings reset to defaults")
        
    def _deep_merge(self, target: Dict, source: Dict) -> Dict:
        """Deep merge two dictionaries.
        
        Args:
            target: Target dictionary
            source: Source dictionary to merge in
            
        Returns:
            Merged dictionary
        """
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                target[key] = self._deep_merge(target[key], value)
            else:
                target[key] = value
        return target
        
    def get_all(self) -> Dict[str, Any]:
        """Get all settings.
        
        Returns:
            Complete settings dictionary
        """
        return self._settings.copy()
        
    def cleanup(self) -> None:
        """Clean up the service."""
        self.save_settings()
        print("SettingsService cleaned up") 