"""Bullet entity fired by the player ship."""
import numpy as np
from typing import TYPE_CHECKING
from src.core.entities.base import Entity, TransformComponent, RenderComponent, CollisionComponent
from src.core.entities.components import PhysicsComponent, ScreenWrapComponent
from src.core.constants import WHITE, WINDOW_WIDTH, WINDOW_HEIGHT
from src.entities.asteroid import Asteroid

if TYPE_CHECKING:
    from src.core.game import Game

class Bullet(Entity):
    """Projectile fired by the player ship."""
    
    SPEED = 500.0  # pixels per second
    LIFETIME = 1.0  # seconds before despawning
    
    def __init__(self, game: 'Game', x: float, y: float, direction: np.ndarray):
        super().__init__(game)
        self.lifetime = self.LIFETIME
        
        # Add components
        self._init_transform(x, y)
        self._init_physics(direction)
        self._init_render()
        self._init_collision()
        self._init_screen_wrap()
    
    def _init_transform(self, x: float, y: float) -> None:
        """Initialize transform component."""
        transform = self.add_component(TransformComponent, x, y)
        # Calculate rotation from direction
        transform.rotation = np.degrees(np.arctan2(direction[1], direction[0]))
    
    def _init_physics(self, direction: np.ndarray) -> None:
        """Initialize physics component."""
        physics = self.add_component(PhysicsComponent, mass=0.1)
        # Set initial velocity
        physics.velocity = direction * self.SPEED
        physics.friction = 0.0  # No friction for bullets
    
    def _init_render(self) -> None:
        """Initialize render component."""
        render = self.add_component(RenderComponent)
        render.color = WHITE
        
        # Define bullet shape (small line)
        size = 4.0
        render.vertices = [
            (-size/2, 0),
            (size/2, 0)
        ]
    
    def _init_collision(self) -> None:
        """Initialize collision component."""
        self.add_component(CollisionComponent, radius=2.0)
    
    def _init_screen_wrap(self) -> None:
        """Initialize screen wrapping component."""
        self.add_component(ScreenWrapComponent, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def update(self, dt: float) -> None:
        """Update bullet state."""
        super().update(dt)
        
        # Update lifetime and despawn if expired
        self.lifetime -= dt
        if self.lifetime <= 0:
            self.game.entities.remove(self)
            return
        
        # Check for collisions with asteroids
        collision = self.get_component('collision')
        if not collision:
            return
            
        for entity in self.game.entities:
            if not isinstance(entity, Asteroid):
                continue
                
            asteroid_collision = entity.get_component('collision')
            if not asteroid_collision:
                continue
                
            if collision.check_collision(asteroid_collision):
                # Remove bullet
                self.game.entities.remove(self)
                
                # Split asteroid
                entity.split()
                return 