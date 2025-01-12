"""Ship entity for the player."""
import pygame
from typing import Tuple
import math

from .base import Entity
from ..constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SHIP_ACCELERATION,
    SHIP_MAX_SPEED,
    SHIP_ROTATION_SPEED,
    SHIP_FRICTION,
    SHIP_RADIUS
)

class Ship(Entity):
    """Player-controlled ship entity."""
    
    def __init__(self, x: float = SCREEN_WIDTH/2, y: float = SCREEN_HEIGHT/2, rotation: float = 0):
        """Initialize the ship.
        
        Args:
            x: Initial x position
            y: Initial y position
            rotation: Initial rotation in degrees
        """
        super().__init__()
        
        # Add transform component
        self.add_component('TransformComponent', x=x, y=y, rotation=rotation)
        
        # Add physics component
        self.add_component('PhysicsComponent', max_speed=SHIP_MAX_SPEED, friction=SHIP_FRICTION)
        
        # Add render component with ship shape
        points = [
            (0, -15),   # Nose
            (-10, 15),  # Left corner
            (0, 10),    # Back center
            (10, 15)    # Right corner
        ]
        self.add_component('RenderComponent', color=(255, 255, 255), points=points)
        
        # Add collision component
        self.add_component('CollisionComponent', radius=SHIP_RADIUS)
        
        # Add input component
        self.add_component('InputComponent')
        
        # Add screen wrap component
        self.add_component('ScreenWrapComponent')
    
    def thrust(self) -> None:
        """Apply forward thrust to the ship."""
        transform = self.get_component('TransformComponent')
        physics = self.get_component('PhysicsComponent')
        
        if transform and physics:
            # Calculate thrust vector based on rotation
            angle = math.radians(transform.rotation)
            thrust = pygame.Vector2(
                math.sin(angle) * SHIP_ACCELERATION,
                -math.cos(angle) * SHIP_ACCELERATION
            )
            physics.apply_force(thrust)
    
    def rotate_left(self) -> None:
        """Rotate the ship counter-clockwise."""
        transform = self.get_component('TransformComponent')
        if transform:
            transform.rotation = (transform.rotation - SHIP_ROTATION_SPEED) % 360
    
    def rotate_right(self) -> None:
        """Rotate the ship clockwise."""
        transform = self.get_component('TransformComponent')
        if transform:
            transform.rotation = (transform.rotation + SHIP_ROTATION_SPEED) % 360 