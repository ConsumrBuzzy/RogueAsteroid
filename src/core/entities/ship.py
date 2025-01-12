"""Ship entity for the player."""
import pygame
from typing import Tuple
import math

from .base import Entity
from ..components import (
    TransformComponent,
    PhysicsComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)
from ..constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    SHIP_ACCELERATION,
    SHIP_MAX_SPEED,
    SHIP_ROTATION_SPEED,
    SHIP_FRICTION
)

class Ship(Entity):
    """Player-controlled ship entity."""
    
    def __init__(self, position: Tuple[float, float], rotation: float = 0):
        """Initialize the ship.
        
        Args:
            position: Initial (x, y) position
            rotation: Initial rotation in degrees
        """
        super().__init__()
        
        # Add required components
        self.add_component(TransformComponent(
            position=position,
            rotation=rotation,
            scale=(1, 1)
        ))
        
        self.add_component(PhysicsComponent(
            velocity=(0, 0),
            acceleration=0,
            max_speed=SHIP_MAX_SPEED,
            friction=SHIP_FRICTION
        ))
        
        self.add_component(RenderComponent(
            color=(255, 255, 255),  # White
            points=[
                (0, -20),   # Nose
                (-10, 10),  # Left wing
                (0, 5),     # Tail
                (10, 10)    # Right wing
            ]
        ))
        
        self.add_component(CollisionComponent(
            radius=15,
            layer="ship"
        ))
        
        self.add_component(InputComponent(
            controls={
                pygame.K_w: self._thrust,
                pygame.K_a: self._rotate_left,
                pygame.K_d: self._rotate_right,
                pygame.K_SPACE: self._fire
            }
        ))
        
        self.add_component(ScreenWrapComponent(
            width=SCREEN_WIDTH,
            height=SCREEN_HEIGHT
        ))
        
    def _thrust(self, dt: float):
        """Apply forward thrust."""
        transform = self.get_component(TransformComponent)
        physics = self.get_component(PhysicsComponent)
        
        # Convert rotation to radians
        angle = math.radians(transform.rotation - 90)  # -90 because ship points up at 0
        
        # Calculate thrust vector
        thrust_x = math.cos(angle) * SHIP_ACCELERATION
        thrust_y = math.sin(angle) * SHIP_ACCELERATION
        
        # Apply thrust
        current_vx, current_vy = physics.velocity
        new_vx = current_vx + thrust_x * dt
        new_vy = current_vy + thrust_y * dt
        
        # Limit speed
        speed = math.sqrt(new_vx * new_vx + new_vy * new_vy)
        if speed > SHIP_MAX_SPEED:
            scale = SHIP_MAX_SPEED / speed
            new_vx *= scale
            new_vy *= scale
            
        physics.velocity = (new_vx, new_vy)
        
    def _rotate_left(self, dt: float):
        """Rotate ship counter-clockwise."""
        transform = self.get_component(TransformComponent)
        transform.rotation = (transform.rotation - SHIP_ROTATION_SPEED * dt) % 360
        
    def _rotate_right(self, dt: float):
        """Rotate ship clockwise."""
        transform = self.get_component(TransformComponent)
        transform.rotation = (transform.rotation + SHIP_ROTATION_SPEED * dt) % 360
        
    def _fire(self, dt: float):
        """Fire the ship's weapon."""
        # TODO: Implement weapon firing
        pass 