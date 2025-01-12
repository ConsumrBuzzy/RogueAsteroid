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
            
            # Load fonts
            self.load_font('default', 'assets/fonts/default.ttf', 32)
            self.load_font('small', 'assets/fonts/default.ttf', 24)
            self.load_font('large', 'assets/fonts/default.ttf', 48)
            
            print("Resources preloaded")
        except Exception as e:
            print(f"Error preloading resources: {e}")
    
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
        """Clean up the service."""
        self.clear()
        print("ResourceManagerService cleaned up") 