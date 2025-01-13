"""Spawning system for game entities."""
import numpy as np
from random import uniform
from typing import TYPE_CHECKING, List
import pygame
from src.entities.asteroid import Asteroid
from src.core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT
)

# Spawning constants
ASTEROID_SPAWN_DISTANCE = 100  # Distance from screen edges to spawn asteroids

if TYPE_CHECKING:
    from src.core.game import Game

class Spawner:
    """Manages entity spawning and wave progression."""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.wave = 1
        self.asteroids_per_wave = 4
        self.spawn_timer = 0.0
        self.spawn_delay = 0.5  # seconds between asteroid spawns
        self.spawning_wave = False
        self.asteroids_to_spawn = 0
    
    def update(self, dt: float) -> None:
        """Update spawner state."""
        if self.spawning_wave:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay and self.asteroids_to_spawn > 0:
                self._spawn_asteroid()
                self.asteroids_to_spawn -= 1
                self.spawn_timer = 0.0
                
                if self.asteroids_to_spawn <= 0:
                    self.spawning_wave = False
    
    def start_wave(self) -> None:
        """Start a new wave of asteroids."""
        self.spawning_wave = True
        self.asteroids_to_spawn = self.asteroids_per_wave + (self.wave - 1)
        self.spawn_timer = self.spawn_delay  # Spawn first asteroid immediately
    
    def _spawn_asteroid(self) -> None:
        """Spawn a single asteroid."""
        # Choose spawn point on the edge of the screen
        if uniform(0, 1) < 0.5:
            # Spawn on left/right edge
            x = 0 if uniform(0, 1) < 0.5 else WINDOW_WIDTH
            y = uniform(0, WINDOW_HEIGHT)
        else:
            # Spawn on top/bottom edge
            x = uniform(0, WINDOW_WIDTH)
            y = 0 if uniform(0, 1) < 0.5 else WINDOW_HEIGHT
        
        # Create position vector
        position = pygame.Vector2(x, y)
        
        # Calculate velocity towards center with randomness
        center = pygame.Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        to_center = center - position
        angle = to_center.angle_to(pygame.Vector2(1, 0))
        angle += uniform(-45, 45)  # Add up to 45 degrees of randomness
        
        # Create velocity vector
        speed = uniform(50.0, 100.0)
        velocity = pygame.Vector2()
        velocity.from_polar((speed, angle))
        
        # Create asteroid
        asteroid = Asteroid(self.game, 'large', position, velocity)
        self.game.entity_manager.add_entity(asteroid)
    
    def check_wave_complete(self) -> bool:
        """Check if current wave is complete."""
        if self.spawning_wave:
            return False
            
        # Count remaining asteroids
        asteroid_count = sum(
            1 for entity in self.game.entity_manager.entities
            if isinstance(entity, Asteroid)
        )
        
        return asteroid_count == 0
    
    def advance_wave(self) -> None:
        """Advance to the next wave."""
        self.wave += 1
        self.start_wave() 