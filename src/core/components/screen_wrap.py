"""Screen wrap component for handling entity wrapping at screen boundaries."""
from typing import Optional, Tuple, List
import pygame
from .component import Component

class ScreenWrapComponent(Component):
    """Component for managing entity screen wrapping.
    
    Provides:
    - Screen boundary detection
    - Position wrapping
    - Wrap offset control
    - Smooth transitions
    - Transform integration
    """
    
    def __init__(self, entity, screen_size: Tuple[int, int], wrap_offset: float = 2.0):
        """Initialize screen wrap component.
        
        Args:
            entity: Entity this component belongs to
            screen_size: (width, height) of screen
            wrap_offset: Offset for wrapping (prevents edge sticking)
        """
        super().__init__(entity)
        self.screen_width, self.screen_height = screen_size
        self.wrap_offset = wrap_offset
        self._last_wrap: Optional[str] = None  # Track last wrap direction
        
        print(f"ScreenWrapComponent initialized with screen size {screen_size}")
    
    def update(self, dt: float) -> None:
        """Update entity wrapping.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return
            
        # Get transform component
        transform = self.get_sibling_component('TransformComponent')
        if not transform:
            return
            
        # Track if we wrapped this frame
        wrapped = False
        
        # Check horizontal wrapping
        if transform.x < -self.wrap_offset:
            transform.x = self.screen_width + self.wrap_offset
            self._last_wrap = "left"
            wrapped = True
        elif transform.x > self.screen_width + self.wrap_offset:
            transform.x = -self.wrap_offset
            self._last_wrap = "right"
            wrapped = True
            
        # Check vertical wrapping
        if transform.y < -self.wrap_offset:
            transform.y = self.screen_height + self.wrap_offset
            self._last_wrap = "top"
            wrapped = True
        elif transform.y > self.screen_height + self.wrap_offset:
            transform.y = -self.wrap_offset
            self._last_wrap = "bottom"
            wrapped = True
            
        # Clear wrap tracking if we didn't wrap this frame
        if not wrapped:
            self._last_wrap = None
    
    def get_wrap_positions(self) -> List[Tuple[float, float]]:
        """Get list of positions where entity should be drawn when wrapping.
        
        Returns:
            List of (x, y) positions for drawing
        """
        transform = self.get_sibling_component('TransformComponent')
        if not transform:
            return []
            
        positions = [(transform.x, transform.y)]
        
        # Add wrapped positions when near screen edges
        if transform.x < self.wrap_offset:
            positions.append((transform.x + self.screen_width, transform.y))
        elif transform.x > self.screen_width - self.wrap_offset:
            positions.append((transform.x - self.screen_width, transform.y))
            
        if transform.y < self.wrap_offset:
            positions.append((transform.x, transform.y + self.screen_height))
        elif transform.y > self.screen_height - self.wrap_offset:
            positions.append((transform.x, transform.y - self.screen_height))
            
        # Add corner positions when wrapping both horizontally and vertically
        if len(positions) > 2:
            positions.append((
                positions[1][0],  # Wrapped x
                positions[2][1]   # Wrapped y
            ))
            
        return positions
    
    def set_screen_size(self, width: int, height: int) -> None:
        """Update screen size.
        
        Args:
            width: New screen width
            height: New screen height
        """
        self.screen_width = width
        self.screen_height = height
        print(f"Updated screen size to {width}x{height}")
    
    def set_wrap_offset(self, offset: float) -> None:
        """Set wrap offset distance.
        
        Args:
            offset: New wrap offset in pixels
        """
        self.wrap_offset = offset
        print(f"Updated wrap offset to {offset}")
    
    @property
    def last_wrap_direction(self) -> Optional[str]:
        """Get direction of last wrap (None if didn't wrap this frame)."""
        return self._last_wrap
    
    def is_wrapping(self) -> bool:
        """Check if entity is currently in a wrap transition."""
        transform = self.get_sibling_component('TransformComponent')
        if not transform:
            return False
            
        return (
            transform.x < self.wrap_offset or
            transform.x > self.screen_width - self.wrap_offset or
            transform.y < self.wrap_offset or
            transform.y > self.screen_height - self.wrap_offset
        ) 