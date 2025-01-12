"""UI service for game-wide interface management."""
from typing import List, Dict, Optional, Tuple, Union
import pygame

class UIElement:
    """Individual UI element with text and rendering properties."""
    def __init__(self, 
                 text: str,
                 position: Tuple[int, int],
                 color: Tuple[int, int, int] = (255, 255, 255),
                 font_size: int = 24,
                 centered: bool = False,
                 visible: bool = True):
        """Initialize a UI element.
        
        Args:
            text: Text to display
            position: (x, y) position on screen
            color: RGB color tuple
            font_size: Font size in pixels
            centered: Whether to center text at position
            visible: Initial visibility state
        """
        self.text = text
        self.position = position
        self.color = color
        self.font_size = font_size
        self.centered = centered
        self.visible = visible
        self._font: Optional[pygame.font.Font] = None
        self._surface: Optional[pygame.Surface] = None
        self._needs_update = True
        
    def _ensure_font(self) -> None:
        """Ensure font is initialized."""
        if self._font is None:
            self._font = pygame.font.Font(None, self.font_size)
            
    def _update_surface(self) -> None:
        """Update the cached text surface."""
        self._ensure_font()
        self._surface = self._font.render(self.text, True, self.color)
        self._needs_update = False
        
    def set_text(self, text: str) -> None:
        """Set new text for the element.
        
        Args:
            text: New text to display
        """
        if self.text != text:
            self.text = text
            self._needs_update = True
            
    def set_color(self, color: Tuple[int, int, int]) -> None:
        """Set new color for the element.
        
        Args:
            color: New RGB color tuple
        """
        if self.color != color:
            self.color = color
            self._needs_update = True
            
    def set_visible(self, visible: bool) -> None:
        """Set visibility of the element.
        
        Args:
            visible: New visibility state
        """
        self.visible = visible
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the element on the screen.
        
        Args:
            screen: Surface to draw on
        """
        if not self.visible:
            return
            
        if self._needs_update or self._surface is None:
            self._update_surface()
            
        if self._surface:
            x, y = self.position
            if self.centered:
                x -= self._surface.get_width() // 2
                y -= self._surface.get_height() // 2
            screen.blit(self._surface, (x, y))

class UIService:
    """Service for game-wide UI management.
    
    Provides:
    - UI element management
    - Text rendering
    - Element positioning
    - Visibility control
    - Performance optimization
    """
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the UI service.
        
        Args:
            screen: Pygame surface to render to
        """
        self._screen = screen
        self._elements: Dict[str, UIElement] = {}
        print("UIService initialized")
        
    def add_element(self, id: str, element: UIElement) -> None:
        """Add a UI element.
        
        Args:
            id: Unique identifier for the element
            element: UIElement to add
        """
        self._elements[id] = element
        print(f"Added UI element: {id}")
        
    def remove_element(self, id: str) -> None:
        """Remove a UI element.
        
        Args:
            id: ID of element to remove
        """
        if id in self._elements:
            del self._elements[id]
            print(f"Removed UI element: {id}")
            
    def get_element(self, id: str) -> Optional[UIElement]:
        """Get a UI element by ID.
        
        Args:
            id: ID of element to get
            
        Returns:
            UIElement if found, None otherwise
        """
        return self._elements.get(id)
        
    def update_text(self, id: str, text: str) -> None:
        """Update text of an element.
        
        Args:
            id: Element ID
            text: New text
        """
        if element := self._elements.get(id):
            element.set_text(text)
            
    def set_visible(self, id: str, visible: bool) -> None:
        """Set visibility of an element.
        
        Args:
            id: Element ID
            visible: New visibility state
        """
        if element := self._elements.get(id):
            element.set_visible(visible)
            
    def draw(self) -> None:
        """Draw all visible UI elements."""
        for element in self._elements.values():
            element.draw(self._screen)
            
    def clear(self) -> None:
        """Remove all UI elements."""
        self._elements.clear()
        print("UI service cleared") 