"""Bullet entity using component system."""
import numpy as np
from typing import TYPE_CHECKING
from src.core.entities.base import Entity, TransformComponent, RenderComponent, CollisionComponent
from src.core.entities.components import PhysicsComponent
from src.core.constants import WHITE

if TYPE_CHECKING:
    from src.core.game import Game

class Bullet(Entity):
    """Player bullet entity."""
    
    SPEED = 500.0  # pixels per second
    LIFETIME = 1.0  # seconds
    SIZE = 3.0  # pixels
    
    def __init__(self, game: 'Game', x: float, y: float, direction: np.ndarray):
        super().__init__(game)
        self.time_alive = 0.0
        
        # Add components
        self._init_transform(x, y, direction)
        self._init_physics()
        self._init_render()
        self._init_collision()
        
        # Play shoot sound
        self.game.audio.play_sound('shoot')
    
    def _init_transform(self, x: float, y: float, direction: np.ndarray) -> None:
        """Initialize transform component."""
        transform = self.add_component(TransformComponent, x, y)
        transform.velocity = direction * self.SPEED
    
    def _init_physics(self) -> None:
        """Initialize physics component."""
        physics = self.add_component(PhysicsComponent, mass=0.1)
        physics.friction = 0.0  # No friction for bullets
    
    def _init_render(self) -> None:
        """Initialize render component."""
        render = self.add_component(RenderComponent)
        render.color = WHITE
        render.vertices = [
            (-self.SIZE/2, -self.SIZE/2),
            (self.SIZE/2, -self.SIZE/2),
            (self.SIZE/2, self.SIZE/2),
            (-self.SIZE/2, self.SIZE/2)
        ]
    
    def _init_collision(self) -> None:
        """Initialize collision component."""
        self.add_component(CollisionComponent, radius=self.SIZE/2)
    
    def update(self, dt: float) -> None:
        """Update bullet state and check lifetime."""
        super().update(dt)
        
        self.time_alive += dt
        if self.time_alive >= self.LIFETIME:
            self.game.entities.remove(self)
            return
        
        # Check collisions with asteroids
        collision = self.get_component(CollisionComponent)
        if not collision:
            return
            
        for asteroid in self.game.asteroids[:]:  # Copy list for safe removal
            asteroid_collision = asteroid.get_component(CollisionComponent)
            if not asteroid_collision:
                continue
                
            if collision.collides_with(asteroid_collision):
                # Create explosion effect
                transform = asteroid.get_component(TransformComponent)
                if transform:
                    self.game.particles.create_explosion(
                        transform.position,
                        (255, 255, 0),  # Yellow explosion
                        num_particles=15 if asteroid.size_category == 'small' else 25,
                        speed_range=(75, 150),
                        lifetime_range=(0.3, 0.6)
                    )
                    self.game.audio.play_explosion(asteroid.size_category)
                
                # Split asteroid
                new_asteroids = asteroid.split()
                
                # Update game state
                self.game.asteroids.remove(asteroid)
                self.game.entities.remove(asteroid)
                self.game.score += asteroid.config['points']
                
                # Add new asteroids
                for new_asteroid in new_asteroids:
                    self.game.asteroids.append(new_asteroid)
                    self.game.entities.append(new_asteroid)
                
                # Remove bullet
                self.game.entities.remove(self)
                return 