"""Game settings management."""
import json
import os
from typing import Dict, Any

class Settings:
    """Manages game settings and preferences."""
    
    DEFAULT_SETTINGS = {
        "controls": {
            "scheme": "arrows",  # 'arrows' or 'wasd'
            "shoot_key": "space",
            "thrust_key": "up",
            "left_key": "left",
            "right_key": "right"
        },
        "video": {
            "fullscreen": False,
            "show_fps": True
        },
        "audio": {
            "sound_enabled": True,
            "music_enabled": True,
            "volume": 0.7
        }
    }
    
    def __init__(self):
        self.settings = self.DEFAULT_SETTINGS.copy()
        self.settings_file = "settings.json"
        self.load()
    
    def load(self) -> None:
        """Load settings from file."""
        try:
            if os.path.exists(self.settings_file):
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    # Update only existing settings to maintain structure
                    self._update_recursive(self.settings, loaded)
        except Exception as e:
            print(f"Error loading settings: {e}")
    
    def save(self) -> None:
        """Save settings to file."""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except Exception as e:
            print(f"Error saving settings: {e}")
    
    def get(self, *keys: str) -> Any:
        """Get a setting value by key path."""
        value = self.settings
        for key in keys:
            value = value[key]
        return value
    
    def set(self, *keys: str, value: Any) -> None:
        """Set a setting value by key path."""
        target = self.settings
        for key in keys[:-1]:
            target = target[key]
        target[keys[-1]] = value
        self.save()
    
    def _update_recursive(self, target: Dict, source: Dict) -> None:
        """Recursively update settings while maintaining structure."""
        for key, value in source.items():
            if key in target:
                if isinstance(value, dict) and isinstance(target[key], dict):
                    self._update_recursive(target[key], value)
                else:
                    target[key] = value 