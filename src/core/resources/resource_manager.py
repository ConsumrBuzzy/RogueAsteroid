"""Resource management system for game assets."""
from typing import Dict, Any, Optional
from pathlib import Path
import pygame

class ResourceManager:
    """Manager for game-wide resource handling.
    
    Provides:
    - Asset loading/unloading
    - Resource caching
    - Memory management
    - Resource validation
    - Debug support
    """
    
    def __init__(self):
        """Initialize the resource manager."""
        self._fonts: Dict[str, Dict[int, pygame.font.Font]] = {}
        self._surfaces: Dict[str, pygame.Surface] = {}
        self._configs: Dict[str, dict] = {}
        print("ResourceManager initialized")
        
    def load_font(self, name: str, size: int) -> Optional[pygame.font.Font]:
        """Load or retrieve a cached font.
        
        Args:
            name: Font name or path
            size: Font size in points
            
        Returns:
            Loaded font or None if loading failed
        """
        if name not in self._fonts:
            self._fonts[name] = {}
            
        if size not in self._fonts[name]:
            try:
                if Path(name).exists():
                    font = pygame.font.Font(name, size)
                else:
                    font = pygame.font.SysFont(name, size)
                self._fonts[name][size] = font
                print(f"Loaded font: {name} at size {size}")
            except Exception as e:
                print(f"Error loading font {name}: {e}")
                return None
                
        return self._fonts[name][size]
        
    def load_surface(self, path: str) -> Optional[pygame.Surface]:
        """Load or retrieve a cached surface.
        
        Args:
            path: Path to image file
            
        Returns:
            Loaded surface or None if loading failed
        """
        if path not in self._surfaces:
            try:
                surface = pygame.image.load(path).convert_alpha()
                self._surfaces[path] = surface
                print(f"Loaded surface: {path}")
            except Exception as e:
                print(f"Error loading surface {path}: {e}")
                return None
                
        return self._surfaces[path]
        
    def load_config(self, path: str) -> Optional[dict]:
        """Load or retrieve a cached configuration.
        
        Args:
            path: Path to config file
            
        Returns:
            Loaded config dict or None if loading failed
        """
        if path not in self._configs:
            try:
                with open(path, 'r') as f:
                    import json
                    config = json.load(f)
                self._configs[path] = config
                print(f"Loaded config: {path}")
            except Exception as e:
                print(f"Error loading config {path}: {e}")
                return None
                
        return self._configs[path]
        
    def unload_font(self, name: str, size: Optional[int] = None) -> None:
        """Unload a font from cache.
        
        Args:
            name: Font name or path
            size: Optional specific size to unload, or all sizes if None
        """
        if name in self._fonts:
            if size is None:
                del self._fonts[name]
                print(f"Unloaded all sizes of font: {name}")
            elif size in self._fonts[name]:
                del self._fonts[name][size]
                print(f"Unloaded font {name} size {size}")
                if not self._fonts[name]:
                    del self._fonts[name]
                    
    def unload_surface(self, path: str) -> None:
        """Unload a surface from cache.
        
        Args:
            path: Path of surface to unload
        """
        if path in self._surfaces:
            del self._surfaces[path]
            print(f"Unloaded surface: {path}")
            
    def unload_config(self, path: str) -> None:
        """Unload a config from cache.
        
        Args:
            path: Path of config to unload
        """
        if path in self._configs:
            del self._configs[path]
            print(f"Unloaded config: {path}")
            
    def clear(self) -> None:
        """Clear all cached resources."""
        self._fonts.clear()
        self._surfaces.clear()
        self._configs.clear()
        print("Resource cache cleared") 