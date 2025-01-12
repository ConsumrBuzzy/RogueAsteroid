"""Transform component for handling entity position, rotation, and scale."""
import math
from typing import Tuple
from .component import Component

class TransformComponent(Component):
    """Component for managing entity transformation.
    
    Provides:
    - Position management (x, y)
    - Rotation handling (angle, direction)
    - Scale control
    - Forward/right vector calculations
    - Local to world space conversion
    """
    
    def __init__(self, entity, x: float = 0, y: float = 0, rotation: float = 0, scale: float = 1):
        """Initialize transform component.
        
        Args:
            entity: Entity this component belongs to
            x: Initial x position
            y: Initial y position
            rotation: Initial rotation in degrees
            scale: Initial scale factor
        """
        super().__init__(entity)
        self.x = x
        self.y = y
        self._rotation = rotation  # in degrees
        self.scale = scale
        
        # Cache for direction vectors
        self._forward = (0, 0)
        self._right = (0, 0)
        self._update_direction_vectors()
        
        print(f"TransformComponent initialized at ({x}, {y}) with rotation {rotation}°")
    
    @property
    def position(self) -> Tuple[float, float]:
        """Get current position."""
        return (self.x, self.y)
    
    @position.setter
    def position(self, value: Tuple[float, float]) -> None:
        """Set position from tuple.
        
        Args:
            value: (x, y) position tuple
        """
        self.x, self.y = value
    
    @property
    def rotation(self) -> float:
        """Get rotation in degrees."""
        return self._rotation
    
    @rotation.setter
    def rotation(self, value: float) -> None:
        """Set rotation in degrees.
        
        Args:
            value: Rotation angle in degrees
        """
        self._rotation = value % 360
        self._update_direction_vectors()
    
    @property
    def forward(self) -> Tuple[float, float]:
        """Get normalized forward vector."""
        return self._forward
    
    @property
    def right(self) -> Tuple[float, float]:
        """Get normalized right vector."""
        return self._right
    
    def _update_direction_vectors(self) -> None:
        """Update cached direction vectors based on current rotation."""
        # Convert rotation to radians
        angle_rad = math.radians(self._rotation)
        
        # Calculate forward vector (normalized)
        self._forward = (
            math.cos(angle_rad),
            math.sin(angle_rad)
        )
        
        # Calculate right vector (90° clockwise from forward)
        self._right = (
            math.cos(angle_rad + math.pi/2),
            math.sin(angle_rad + math.pi/2)
        )
    
    def move(self, dx: float, dy: float) -> None:
        """Move relative to current position.
        
        Args:
            dx: Change in x position
            dy: Change in y position
        """
        self.x += dx
        self.y += dy
    
    def move_forward(self, distance: float) -> None:
        """Move forward based on current rotation.
        
        Args:
            distance: Distance to move
        """
        self.x += self._forward[0] * distance
        self.y += self._forward[1] * distance
    
    def rotate(self, angle: float) -> None:
        """Rotate by specified angle.
        
        Args:
            angle: Angle to rotate by in degrees
        """
        self.rotation = self._rotation + angle
    
    def look_at(self, target_x: float, target_y: float) -> None:
        """Rotate to look at a point.
        
        Args:
            target_x: Target x position
            target_y: Target y position
        """
        dx = target_x - self.x
        dy = target_y - self.y
        self.rotation = math.degrees(math.atan2(dy, dx))
    
    def distance_to(self, other_x: float, other_y: float) -> float:
        """Calculate distance to another point.
        
        Args:
            other_x: Other point x position
            other_y: Other point y position
            
        Returns:
            Distance to other point
        """
        dx = other_x - self.x
        dy = other_y - self.y
        return math.sqrt(dx * dx + dy * dy) 