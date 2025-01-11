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
    
    SPEED = 25000.0  # pixels per second
    LIFETIME = 2  # seconds before despawning
    
    def __init__(self, game: 'Game', x: float, y: float, direction: np.ndarray):
        super().__init__(game)
        self.lifetime = self.LIFETIME
        self.direction = direction  # Store direction for use in initialization
        
        # Add components
        self._init_transform(x, y)
        self._init_physics()
        self._init_render()
        self._init_collision()
        self._init_screen_wrap()
    
    def _init_transform(self, x: float, y: float) -> None:
        """Initialize transform component."""
        transform = self.add_component(TransformComponent, x, y)
        # Calculate rotation from direction
        transform.rotation = np.degrees(np.arctan2(self.direction[1], self.direction[0]))
    
    def _init_physics(self) -> None:
        """Initialize physics component."""
        physics = self.add_component(PhysicsComponent, mass=0.1, max_speed=self.SPEED)
        physics.friction = 0.0  # No friction for bullets
        
        # Set initial velocity using physics component
        velocity = self.direction * self.SPEED
        physics.apply_force(velocity * physics.mass)  # F = ma to achieve desired velocity instantly
        print(f"Bullet velocity: {velocity}")  # Debug info
    
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
            if self in self.game.entities:
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
                print("Bullet hit asteroid!")  # Debug info
                
                # Remove bullet and asteroid
                if self in self.game.entities:
                    self.game.entities.remove(self)
                
                # Split asteroid and add new ones to game
                if entity in self.game.entities:
                    new_asteroids = entity.split()
                    self.game.asteroids.remove(entity)
                    self.game.entities.remove(entity)
                    
                    # Add new asteroids
                    for new_asteroid in new_asteroids:
                        self.game.asteroids.append(new_asteroid)
                        self.game.entities.append(new_asteroid)
                    
                    print(f"Created {len(new_asteroids)} new asteroids")  # Debug info
                return 