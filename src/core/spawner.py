"""Spawning system for game entities."""
import numpy as np
from random import uniform
from typing import TYPE_CHECKING, List
from src.entities.asteroid import Asteroid
from src.core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    ASTEROID_SPAWN_DISTANCE
)

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
        
        # Create asteroid
        asteroid = Asteroid(x, y)
        
        # Ensure asteroid is moving towards the center
        center = np.array([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
        to_center = center - asteroid.position
        angle = np.arctan2(to_center[1], to_center[0])
        
        # Add some randomness to the angle
        angle += uniform(-np.pi/4, np.pi/4)
        
        # Set velocity
        speed = uniform(50.0, 100.0)
        asteroid.velocity = np.array([
            speed * np.cos(angle),
            speed * np.sin(angle)
        ])
        
        self.game.add_entity(asteroid)
    
    def check_wave_complete(self) -> bool:
        """Check if current wave is complete."""
        if self.spawning_wave:
            return False
            
        # Count remaining asteroids
        asteroid_count = sum(
            1 for entity in self.game.entities
            if isinstance(entity, Asteroid)
        )
        
        return asteroid_count == 0
    
    def advance_wave(self) -> None:
        """Advance to the next wave."""
        self.wave += 1
        self.start_wave() 