"""UI component for managing user interface elements."""
import pygame
from typing import Dict, Optional, Tuple, List
from .base import Component

class UIElement:
    """Individual UI element for text rendering."""
    
    def __init__(self, text: str, position: Tuple[int, int], color: Tuple[int, int, int],
                 font_size: int = 32, centered: bool = False):
        """Initialize UI element.
        
        Args:
            text: Text to display
            position: (x, y) position on screen
            color: RGB color tuple
            font_size: Font size in pixels
            centered: Whether to center text at position
        """
        self.text = text
        self.position = position
        self.color = color
        self.font_size = font_size
        self.centered = centered
        self.visible = True
        self._font = None
        self._surface = None
        self._needs_update = True
    
    def update_text(self, new_text: str) -> None:
        """Update the element's text.
        
        Args:
            new_text: New text to display
        """
        if self.text != new_text:
            self.text = new_text
            self._needs_update = True
    
    def render(self, screen: pygame.Surface) -> None:
        """Render the element on screen.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.visible:
            return
            
        # Create/update font and surface if needed
        if self._font is None:
            self._font = pygame.font.Font(None, self.font_size)
            self._needs_update = True
            
        if self._needs_update:
            self._surface = self._font.render(self.text, True, self.color)
            self._needs_update = False
        
        # Calculate position (centered or top-left)
        pos = list(self.position)
        if self.centered:
            pos[0] -= self._surface.get_width() // 2
            pos[1] -= self._surface.get_height() // 2
        
        screen.blit(self._surface, pos)

class UIComponent(Component):
    """Component for managing UI elements and text rendering.
    
    Provides:
    - Text rendering
    - Element positioning
    - Color management
    - Visibility control
    - Dynamic updates
    """
    
    def __init__(self, entity):
        """Initialize UI component.
        
        Args:
            entity: Entity this component belongs to
        """
        super().__init__(entity)
        self._elements: Dict[str, UIElement] = {}
        
        print("UIComponent initialized")
    
    def add_element(self, name: str, text: str, position: Tuple[int, int],
                   color: Tuple[int, int, int] = (255, 255, 255),
                   font_size: int = 32, centered: bool = False) -> None:
        """Add a new UI element.
        
        Args:
            name: Unique name for the element
            text: Initial text to display
            position: (x, y) position on screen
            color: RGB color tuple
            font_size: Font size in pixels
            centered: Whether to center text at position
        """
        if name in self._elements:
            print(f"Warning: Overwriting existing UI element '{name}'")
            
        self._elements[name] = UIElement(text, position, color, font_size, centered)
        print(f"Added UI element '{name}' at position {position}")
    
    def remove_element(self, name: str) -> None:
        """Remove a UI element.
        
        Args:
            name: Name of element to remove
        """
        if name in self._elements:
            del self._elements[name]
            print(f"Removed UI element '{name}'")
    
    def update_text(self, name: str, text: str) -> None:
        """Update text of an element.
        
        Args:
            name: Name of element to update
            text: New text to display
        """
        if name in self._elements:
            self._elements[name].update_text(text)
    
    def set_visible(self, name: str, visible: bool) -> None:
        """Set visibility of an element.
        
        Args:
            name: Name of element to update
            visible: Whether element should be visible
        """
        if name in self._elements:
            self._elements[name].visible = visible
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all visible UI elements.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.enabled:
            return
            
        for element in self._elements.values():
            element.render(screen)
    
    def clear_elements(self) -> None:
        """Remove all UI elements."""
        self._elements.clear()
        print("All UI elements cleared") 