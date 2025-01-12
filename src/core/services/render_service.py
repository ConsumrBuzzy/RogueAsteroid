"""Render service for game graphics."""
from typing import Dict, List, Optional
import pygame

class RenderLayer:
    """Layer for organizing game rendering."""
    
    def __init__(self, name: str, order: int):
        """Initialize render layer.
        
        Args:
            name: Layer name
            order: Render order (lower = earlier)
        """
        self.name = name
        self.order = order
        self.entities: List = []
        self.visible = True

class RenderService:
    """Service for managing game rendering.
    
    Provides:
    - Layer-based rendering
    - Entity registration
    - Screen management
    - Performance optimization
    """
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the render service.
        
        Args:
            screen: Pygame surface to render to
        """
        self._screen = screen
        self._layers: Dict[str, RenderLayer] = {}
        
        # Create default layers
        self._create_layer("background", 0)
        self._create_layer("game", 1)
        self._create_layer("particles", 2)
        self._create_layer("ui", 3)
        self._create_layer("debug", 4)
        
        print("RenderService initialized")
        
    def _create_layer(self, name: str, order: int) -> None:
        """Create a new render layer.
        
        Args:
            name: Layer name
            order: Render order
        """
        self._layers[name] = RenderLayer(name, order)
        
    def add_to_layer(self, layer_name: str, entity) -> None:
        """Add an entity to a render layer.
        
        Args:
            layer_name: Name of layer to add to
            entity: Entity to add
        """
        if layer := self._layers.get(layer_name):
            if entity not in layer.entities:
                layer.entities.append(entity)
                
    def remove_from_layer(self, layer_name: str, entity) -> None:
        """Remove an entity from a render layer.
        
        Args:
            layer_name: Name of layer to remove from
            entity: Entity to remove
        """
        if layer := self._layers.get(layer_name):
            if entity in layer.entities:
                layer.entities.remove(entity)
                
    def set_layer_visible(self, layer_name: str, visible: bool) -> None:
        """Set visibility of a render layer.
        
        Args:
            layer_name: Name of layer to modify
            visible: Whether layer should be visible
        """
        if layer := self._layers.get(layer_name):
            layer.visible = visible
            
    def clear_layer(self, layer_name: str) -> None:
        """Clear all entities from a render layer.
        
        Args:
            layer_name: Name of layer to clear
        """
        if layer := self._layers.get(layer_name):
            layer.entities.clear()
            
    def draw(self) -> None:
        """Draw all visible layers in order."""
        # Sort layers by order
        sorted_layers = sorted(self._layers.values(), key=lambda l: l.order)
        
        # Draw each visible layer
        for layer in sorted_layers:
            if layer.visible:
                for entity in layer.entities:
                    if hasattr(entity, 'draw'):
                        entity.draw(self._screen)
                        
    def clear(self) -> None:
        """Clear all render layers."""
        for layer in self._layers.values():
            layer.entities.clear()
            
    def cleanup(self) -> None:
        """Clean up the service."""
        self.clear()
        self._layers.clear()
        print("RenderService cleaned up") 