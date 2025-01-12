"""Service for managing game resources."""
from typing import Dict, Optional, Any
import os
import json
import pygame

class ResourceManagerService:
    """Service for managing game resources.
    
    Provides:
    - Asset loading and caching
    - Resource validation
    - Memory optimization
    - Path management
    - Debug support
    """
    
    def __init__(self):
        """Initialize the resource manager service."""
        self._resources: Dict[str, Any] = {}
        self._resource_paths = {
            'images': 'assets/images',
            'sounds': 'assets/sounds',
            'fonts': 'assets/fonts',
            'data': 'assets/data'
        }
        print("ResourceManagerService initialized")
    
    def preload_resources(self) -> None:
        """Preload commonly used resources."""
        try:
            # Ensure asset directories exist
            for path in self._resource_paths.values():
                os.makedirs(path, exist_ok=True)
                if not os.path.isdir(path):
                    raise ValueError(f"Failed to create resource directory: {path}")
            
            # Validate resource paths
            self._validate_resource_paths()
            
            # Load fonts with validation
            self._load_font_with_fallback('default', 'assets/fonts/default.ttf', 32)
            self._load_font_with_fallback('small', 'assets/fonts/default.ttf', 24)
            self._load_font_with_fallback('large', 'assets/fonts/default.ttf', 48)
            
            print("Resources preloaded")
        except Exception as e:
            print(f"Error preloading resources: {e}")
            raise
    
    def _validate_resource_paths(self) -> None:
        """Validate all resource paths exist and are accessible."""
        for category, path in self._resource_paths.items():
            if not os.path.exists(path):
                raise ValueError(f"Resource path not found: {path}")
            if not os.access(path, os.R_OK):
                raise ValueError(f"Resource path not readable: {path}")
    
    def _load_font_with_fallback(self, name: str, path: str, size: int) -> None:
        """Load a font with fallback to system default.
        
        Args:
            name: Font identifier
            path: Path to font file
            size: Font size in points
        """
        try:
            if os.path.exists(path):
                self._resources[f"font_{name}"] = pygame.font.Font(path, size)
            else:
                print(f"Warning: Font file not found: {path}")
                self._resources[f"font_{name}"] = pygame.font.SysFont('arial', size)
        except Exception as e:
            print(f"Error loading font {name}, using system font: {e}")
            self._resources[f"font_{name}"] = pygame.font.SysFont('arial', size)
    
    def load_image(self, name: str, path: str) -> Optional[pygame.Surface]:
        """Load an image resource.
        
        Args:
            name: Name to store resource under
            path: Path to image file
            
        Returns:
            Loaded image surface or None if failed
        """
        try:
            if not os.path.exists(path):
                print(f"Image not found: {path}")
                return None
                
            image = pygame.image.load(path).convert_alpha()
            self._resources[f"image:{name}"] = image
            print(f"Loaded image: {name}")
            return image
        except Exception as e:
            print(f"Error loading image {name}: {e}")
            return None
    
    def load_sound(self, name: str, path: str) -> Optional[pygame.mixer.Sound]:
        """Load a sound resource.
        
        Args:
            name: Name to store resource under
            path: Path to sound file
            
        Returns:
            Loaded sound or None if failed
        """
        try:
            if not os.path.exists(path):
                print(f"Sound not found: {path}")
                return None
                
            sound = pygame.mixer.Sound(path)
            self._resources[f"sound:{name}"] = sound
            print(f"Loaded sound: {name}")
            return sound
        except Exception as e:
            print(f"Error loading sound {name}: {e}")
            return None
    
    def load_font(self, name: str, path: str, size: int) -> Optional[pygame.font.Font]:
        """Load a font resource.
        
        Args:
            name: Name to store resource under
            path: Path to font file
            size: Font size in points
            
        Returns:
            Loaded font or None if failed
        """
        try:
            if not os.path.exists(path):
                print(f"Font not found: {path}")
                return None
                
            font = pygame.font.Font(path, size)
            self._resources[f"font:{name}"] = font
            print(f"Loaded font: {name}")
            return font
        except Exception as e:
            print(f"Error loading font {name}: {e}")
            return None
    
    def load_data(self, name: str, path: str) -> Optional[Dict]:
        """Load a JSON data resource.
        
        Args:
            name: Name to store resource under
            path: Path to JSON file
            
        Returns:
            Loaded data or None if failed
        """
        try:
            if not os.path.exists(path):
                print(f"Data file not found: {path}")
                return None
                
            with open(path, 'r') as f:
                data = json.load(f)
            self._resources[f"data:{name}"] = data
            print(f"Loaded data: {name}")
            return data
        except Exception as e:
            print(f"Error loading data {name}: {e}")
            return None
    
    def get_resource(self, name: str) -> Optional[Any]:
        """Get a loaded resource.
        
        Args:
            name: Name of resource to get
            
        Returns:
            Resource if found, None otherwise
        """
        return self._resources.get(name)
    
    def clear(self) -> None:
        """Clear all loaded resources."""
        self._resources.clear()
        print("Resources cleared")
    
    def cleanup(self) -> None:
        """Clean up loaded resources."""
        for resource in self._resources.values():
            if hasattr(resource, 'close'):
                try:
                    resource.close()
                except Exception as e:
                    print(f"Error closing resource: {e}")
        self._resources.clear()
        print("ResourceManager cleaned up") 