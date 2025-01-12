"""Rendering service for game-wide display management."""
from typing import List, Dict, Optional, Tuple
import pygame
from ..entity import Entity

class RenderLayer:
    """Enumeration of render layers."""
    BACKGROUND = 0
    PARTICLES = 1
    ENTITIES = 2
    EFFECTS = 3
    UI = 4
    DEBUG = 5

class RenderService:
    """Service for game-wide rendering management.
    
    Provides:
    - Layer-based rendering
    - Entity rendering
    - Screen management
    - Debug visualization
    - Performance optimization
    """
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the render service.
        
        Args:
            screen: Pygame surface to render to
        """
        self._screen = screen
        self._entities: Dict[int, List[Entity]] = {
            layer: [] for layer in range(RenderLayer.DEBUG + 1)
        }
        self._background_color = (0, 0, 0)
        print("RenderService initialized")
        
    def register_entity(self, entity: Entity, layer: int = RenderLayer.ENTITIES) -> None:
        """Register an entity for rendering.
        
        Args:
            entity: Entity to register
            layer: Render layer to use
        """
        if layer not in self._entities:
            print(f"Invalid render layer: {layer}")
            return
            
        if entity not in self._entities[layer]:
            self._entities[layer].append(entity)
            print(f"Registered entity {entity.id} for rendering on layer {layer}")
            
    def unregister_entity(self, entity: Entity, layer: int = RenderLayer.ENTITIES) -> None:
        """Unregister an entity from rendering.
        
        Args:
            entity: Entity to unregister
            layer: Render layer to remove from
        """
        if layer in self._entities and entity in self._entities[layer]:
            self._entities[layer].remove(entity)
            print(f"Unregistered entity {entity.id} from rendering")
            
    def set_background_color(self, color: Tuple[int, int, int]) -> None:
        """Set the background color.
        
        Args:
            color: RGB color tuple
        """
        self._background_color = color
        print(f"Background color set to {color}")
        
    def render(self) -> None:
        """Render all registered entities by layer."""
        # Clear screen
        self._screen.fill(self._background_color)
        
        # Render each layer
        for layer in range(RenderLayer.DEBUG + 1):
            for entity in self._entities[layer]:
                render = entity.get_component('RenderComponent')
                if render and render.enabled:
                    try:
                        render.draw(self._screen)
                    except Exception as e:
                        print(f"Error rendering entity {entity.id}: {e}")
                        
        # Update display
        pygame.display.flip()
        
    def get_screen_size(self) -> Tuple[int, int]:
        """Get the screen dimensions.
        
        Returns:
            Tuple of (width, height)
        """
        return self._screen.get_size()
        
    def clear_layer(self, layer: int) -> None:
        """Clear all entities from a render layer.
        
        Args:
            layer: Layer to clear
        """
        if layer in self._entities:
            self._entities[layer].clear()
            print(f"Cleared render layer {layer}")
            
    def clear(self) -> None:
        """Clear all registered entities from all layers."""
        for layer in self._entities.values():
            layer.clear()
        print("Render service cleared") 