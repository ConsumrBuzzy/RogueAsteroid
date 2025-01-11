"""Bullet entity fired by the player ship."""
import numpy as np
from typing import TYPE_CHECKING
from src.core.entities.base import Entity, TransformComponent, RenderComponent, CollisionComponent
from src.core.entities.components import PhysicsComponent, ScreenWrapComponent
from src.core.constants import WHITE, WINDOW_WIDTH, WINDOW_HEIGHT, ASTEROID_SIZES
from src.entities.asteroid import Asteroid
from src.entities.particle import Particle
import random
import math
import pygame

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
    
    def _create_impact_particles(self, hit_pos):
        """Create particles for bullet impact effect"""
        num_particles = random.randint(4, 6)
        for _ in range(num_particles):
            particle = Particle(self.game)
            
            # Position slightly randomized around impact point
            offset = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
            particle_transform = particle.get_component('transform')
            if particle_transform:
                particle_transform.position = hit_pos + offset
            
            # Velocity in random direction
            angle = random.uniform(0, 360)
            speed = random.uniform(50, 100)
            velocity = pygame.Vector2(
                math.cos(math.radians(angle)) * speed,
                math.sin(math.radians(angle)) * speed
            )
            
            # Set velocity through physics component
            physics = particle.get_component('physics')
            if physics:
                physics.velocity = velocity
            
            # Set color and lifetime through particle component
            particle_comp = particle.get_component('particle')
            if particle_comp:
                # Yellow-white spark color
                r = random.randint(220, 255)
                g = random.randint(180, 220)
                particle_comp.color = (r, g, 50)
                particle_comp.lifetime = random.uniform(0.1, 0.2)
            
            self.game.entities.append(particle)
    
    def update(self, dt: float) -> None:
        """Update bullet state."""
        super().update(dt)
        
        # Update lifetime and despawn if expired
        self.lifetime -= dt
        if self.lifetime <= 0:
            if self in self.game.entities:
                self.game.entities.remove(self)
            if self in self.game.bullets:
                self.game.bullets.remove(self)
            return
        
        # Check for collisions with asteroids
        collision = self.get_component('collision')
        if collision:
            for entity in self.game.entities:
                if isinstance(entity, Asteroid):
                    other_collision = entity.get_component('collision')
                    if other_collision and collision.check_collision(other_collision):
                        # Get transform for particle position
                        transform = self.get_component('transform')
                        if transform:
                            # Create impact particles at collision point
                            self._create_impact_particles(transform.position)
                        
                        # Handle asteroid hit
                        points = ASTEROID_SIZES[entity.size]['points']
                        self.game.score += points
                        print(f"Hit asteroid size {entity.size}, awarded {points} points")  # Debug info
                        
                        # Split asteroid if not smallest size
                        if entity.size in ['large', 'medium']:
                            entity.split()
                        
                        # Remove asteroid and bullet
                        if entity in self.game.entities:
                            self.game.entities.remove(entity)
                        if self in self.game.entities:
                            self.game.entities.remove(self)
                        if self in self.game.bullets:
                            self.game.bullets.remove(self)
                        return 