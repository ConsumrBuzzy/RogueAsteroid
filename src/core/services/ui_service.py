"""UI service for rendering UI elements."""
from typing import Dict, Tuple, Optional
import pygame

class UIService:
    """Service for managing UI elements.
    
    Provides:
    - Text rendering
    - UI element positioning
    - Font management
    """
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the UI service.
        
        Args:
            screen: Pygame surface to render to
        """
        self._screen = screen
        self._fonts: Dict[int, pygame.font.Font] = {}
        print("UIService initialized")
        
    def draw_text(self, 
                  text: str, 
                  position: Tuple[int, int],
                  font_size: int = 32,
                  color: Tuple[int, int, int] = (255, 255, 255),
                  centered: bool = False) -> None:
        """Draw text on screen.
        
        Args:
            text: Text to draw
            position: (x, y) position
            font_size: Font size in points
            color: RGB color tuple
            centered: Whether to center text at position
        """
        font = self._get_font(font_size)
        text_surface = font.render(text, True, color)
        
        if centered:
            rect = text_surface.get_rect(center=position)
        else:
            rect = text_surface.get_rect(topleft=position)
            
        self._screen.blit(text_surface, rect)
        
    def _get_font(self, size: int) -> pygame.font.Font:
        """Get or create font of specified size.
        
        Args:
            size: Font size in points
            
        Returns:
            Pygame font object
        """
        if size not in self._fonts:
            try:
                self._fonts[size] = pygame.font.Font(None, size)
            except pygame.error as e:
                print(f"Error loading font: {e}")
                # Fallback to default font
                self._fonts[size] = pygame.font.SysFont(None, size)
        return self._fonts[size]
        
    def draw(self) -> None:
        """Draw all UI elements.
        
        This method is called each frame to render UI elements.
        Individual UI elements should use draw_text() for rendering.
        """
        pass  # UI elements are drawn directly through draw_text()
        
    def clear(self) -> None:
        """Clear all UI elements.
        
        This method is called to clear any cached UI elements.
        """
        pass  # No cached elements to clear
        
    def cleanup(self) -> None:
        """Clean up the service."""
        self._fonts.clear()
        print("UIService cleaned up") 