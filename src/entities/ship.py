import pygame
import numpy as np
from typing import List, Tuple
from src.core.entity import Entity
from src.core.constants import (
    SHIP_ACCELERATION,
    SHIP_MAX_SPEED,
    SHIP_ROTATION_SPEED,
    SHIP_FRICTION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WHITE
)
from src.core.game import Game

class Ship(Entity):
    """Player controlled ship entity."""
    
    def __init__(self):
        # Start at center of screen
        super().__init__(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        
        # Ship properties
        self.radius = 12.0
        self.color = WHITE
        
        # Define ship shape (triangle)
        size = 20.0
        self.vertices = [
            (0, -size),           # nose
            (-size/2, size/2),    # left wing
            (size/2, size/2)      # right wing
        ]
        
        # Movement flags
        self.thrusting = False
        self.turning_left = False
        self.turning_right = False
    
    def handle_input(self, keys: List[bool]) -> None:
        """Process keyboard input based on control scheme."""
        game = self.game  # type: Game
        
        if game.settings.get('controls', 'scheme') == 'arrows':
            self.thrusting = keys[pygame.K_UP]
            self.turning_left = keys[pygame.K_LEFT]
            self.turning_right = keys[pygame.K_RIGHT]
        else:  # wasd
            self.thrusting = keys[pygame.K_w]
            self.turning_left = keys[pygame.K_a]
            self.turning_right = keys[pygame.K_d]
    
    def update(self, dt: float) -> None:
        """Update ship state based on input."""
        # Rotation
        if self.turning_left:
            self.rotation -= SHIP_ROTATION_SPEED * dt * 60
        if self.turning_right:
            self.rotation += SHIP_ROTATION_SPEED * dt * 60
        
        # Thrust
        if self.thrusting:
            # Get direction vector
            direction = self.get_direction()
            
            # Apply acceleration in that direction
            acceleration = direction * SHIP_ACCELERATION
            self.velocity += acceleration * dt * 60
            
            # Limit speed
            speed = np.linalg.norm(self.velocity)
            if speed > SHIP_MAX_SPEED:
                self.velocity = (self.velocity / speed) * SHIP_MAX_SPEED
        
        # Apply friction
        self.velocity *= SHIP_FRICTION
        
        # Update position
        super().update(dt)
    
    def draw(self, surface) -> None:
        """Draw the ship and its thrust if active."""
        # Draw ship
        super().draw(surface)
        
        # Draw thrust flame when thrusting
        if self.thrusting:
            self._draw_thrust(surface)
    
    def _draw_thrust(self, surface) -> None:
        """Draw a simple thrust flame behind the ship."""
        # Get ship's rear center point
        rear_center = np.array([0, self.radius * 0.7])
        
        # Define flame shape
        flame_size = self.radius * 0.8
        flame_vertices = [
            (rear_center[0], rear_center[1]),
            (rear_center[0] - flame_size/2, rear_center[1] + flame_size),
            (rear_center[0] + flame_size/2, rear_center[1] + flame_size)
        ]
        
        # Transform flame vertices
        angle_rad = np.radians(self.rotation)
        cos_rot = np.cos(angle_rad)
        sin_rot = np.sin(angle_rad)
        
        transformed = []
        for x, y in flame_vertices:
            # Rotate
            rx = x * cos_rot - y * sin_rot
            ry = x * sin_rot + y * cos_rot
            # Translate
            rx += self.position[0]
            ry += self.position[1]
            transformed.append((rx, ry))
        
        # Draw flame
        pygame.draw.polygon(surface, (255, 165, 0), transformed)  # Orange flame 