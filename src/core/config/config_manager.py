"""Configuration management system for game settings."""
from typing import Dict, Any, Optional
import json
from pathlib import Path

class ConfigManager:
    """Manager for game-wide configuration handling.
    
    Provides:
    - Settings management
    - Default configuration
    - Config validation
    - Hot reloading
    - Debug support
    """
    
    def __init__(self):
        """Initialize the configuration manager."""
        self._config: Dict[str, Any] = {}
        self._defaults: Dict[str, Any] = {}
        self._config_path: Optional[Path] = None
        print("ConfigManager initialized")
        
    def set_defaults(self, defaults: Dict[str, Any]) -> None:
        """Set default configuration values.
        
        Args:
            defaults: Dictionary of default settings
        """
        self._defaults = defaults.copy()
        # Apply defaults to current config for any missing values
        for key, value in self._defaults.items():
            if key not in self._config:
                self._config[key] = value
        print("Default configuration values set")
        
    def load_config(self, path: str) -> bool:
        """Load configuration from file.
        
        Args:
            path: Path to config file
            
        Returns:
            True if loading successful, False otherwise
        """
        try:
            config_path = Path(path)
            if not config_path.exists():
                print(f"Config file not found: {path}")
                return False
                
            with open(config_path, 'r') as f:
                loaded_config = json.load(f)
                
            # Validate loaded config
            if not self._validate_config(loaded_config):
                print("Invalid configuration format")
                return False
                
            self._config_path = config_path
            self._config.update(loaded_config)
            print(f"Configuration loaded from: {path}")
            return True
            
        except Exception as e:
            print(f"Error loading config: {e}")
            return False
            
    def save_config(self) -> bool:
        """Save current configuration to file.
        
        Returns:
            True if saving successful, False otherwise
        """
        if not self._config_path:
            print("No config file path set")
            return False
            
        try:
            with open(self._config_path, 'w') as f:
                json.dump(self._config, f, indent=4)
            print(f"Configuration saved to: {self._config_path}")
            return True
            
        except Exception as e:
            print(f"Error saving config: {e}")
            return False
            
    def get(self, key: str, default: Any = None) -> Any:
        """Get a configuration value.
        
        Args:
            key: Configuration key to retrieve
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        return self._config.get(key, default)
        
    def set(self, key: str, value: Any) -> None:
        """Set a configuration value.
        
        Args:
            key: Configuration key to set
            value: Value to set
        """
        self._config[key] = value
        print(f"Configuration updated: {key}")
        
    def reset(self, key: str) -> None:
        """Reset a configuration value to default.
        
        Args:
            key: Configuration key to reset
        """
        if key in self._defaults:
            self._config[key] = self._defaults[key]
            print(f"Configuration reset to default: {key}")
        else:
            print(f"No default value for: {key}")
            
    def reset_all(self) -> None:
        """Reset all configuration values to defaults."""
        self._config = self._defaults.copy()
        print("All configurations reset to defaults")
        
    def _validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate configuration format and values.
        
        Args:
            config: Configuration to validate
            
        Returns:
            True if valid, False otherwise
        """
        # Add validation logic here based on expected config structure
        # For now, just ensure it's a dictionary
        return isinstance(config, dict) 