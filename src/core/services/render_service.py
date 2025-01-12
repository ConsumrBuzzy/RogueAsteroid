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
        self._sorted_layers: Optional[List[RenderLayer]] = None
        self._needs_sort = False
        
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
            order: Render order (lower = earlier)
        """
        self._layers[name] = RenderLayer(name, order)
        self._needs_sort = True
        
    def _ensure_sorted_layers(self) -> None:
        """Sort layers by render order if needed."""
        if self._needs_sort:
            self._sorted_layers = sorted(
                self._layers.values(), 
                key=lambda x: x.order
            )
            self._needs_sort = False
            
    def add_to_layer(self, layer_name: str, entity) -> None:
        """Add entity to render layer.
        
        Args:
            layer_name: Name of layer to add to
            entity: Entity to add
        """
        if layer_name in self._layers:
            self._layers[layer_name].entities.append(entity)
            
    def remove_from_layer(self, layer_name: str, entity) -> None:
        """Remove entity from render layer.
        
        Args:
            layer_name: Name of layer to remove from
            entity: Entity to remove
        """
        if layer_name in self._layers:
            try:
                self._layers[layer_name].entities.remove(entity)
            except ValueError:
                pass
                
    def set_layer_visible(self, layer_name: str, visible: bool) -> None:
        """Set layer visibility.
        
        Args:
            layer_name: Name of layer
            visible: Whether layer should be visible
        """
        if layer_name in self._layers:
            self._layers[layer_name].visible = visible
            
    def clear_layer(self, layer_name: str) -> None:
        """Clear all entities from layer.
        
        Args:
            layer_name: Name of layer to clear
        """
        if layer_name in self._layers:
            self._layers[layer_name].entities.clear()
            
    def draw(self) -> None:
        """Draw all visible layers in order."""
        self._ensure_sorted_layers()
        self._screen.fill((0, 0, 0))  # Clear screen
        
        if not self._sorted_layers:
            return
            
        for layer in self._sorted_layers:
            if not layer.visible:
                continue
                
            for entity in layer.entities:
                if hasattr(entity, 'draw'):
                    entity.draw(self._screen)
                    
    def present(self) -> None:
        """Update the display with the current frame."""
        pygame.display.flip()
                    
    def clear(self) -> None:
        """Clear the screen."""
        self._screen.fill((0, 0, 0))
        
    def cleanup(self) -> None:
        """Clean up render service resources."""
        for layer in self._layers.values():
            layer.entities.clear()
        self._layers.clear()
        self._sorted_layers = None
        print("RenderService cleaned up") 