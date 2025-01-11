"""Particle entity for visual effects."""
import random
import math
import pygame
from src.core.entities.base import Entity, TransformComponent
from src.core.entities.components import ParticleComponent

class Particle(Entity):
    """A single particle for visual effects."""
    
    def __init__(self, game, position: pygame.Vector2, velocity: pygame.Vector2, 
                 color: tuple = (255, 255, 255), lifetime: float = 1.0,
                 size: float = 2.0):
        """Initialize the particle.
        
        Args:
            game: Game instance
            position: Spawn position
            velocity: Initial velocity
            color: RGB color tuple
            lifetime: How long the particle lives in seconds
            size: Size of the particle in pixels
        """
        super().__init__(game)
        
        # Add transform component
        transform = self.add_component(TransformComponent)
        transform.position = pygame.Vector2(position)
        
        # Add particle component
        particle = self.add_component(ParticleComponent, lifetime=lifetime, color=color)
        particle.velocity = velocity
        particle.size = size

    @classmethod
    def create_explosion(cls, game, position: pygame.Vector2, 
                        color: tuple = (255, 200, 50), num_particles: int = 12,
                        speed_range: tuple = (50, 150), 
                        lifetime_range: tuple = (0.3, 0.8),
                        size_range: tuple = (1.0, 3.0)) -> list['Particle']:
        """Create an explosion effect at the given position.
        
        Args:
            game: Game instance
            position: Center of the explosion
            color: Base color for particles
            num_particles: Number of particles to create
            speed_range: (min, max) speed for particles
            lifetime_range: (min, max) lifetime for particles
            size_range: (min, max) size for particles
            
        Returns:
            List of created particles
        """
        particles = []
        
        for _ in range(num_particles):
            # Random angle and speed
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(*speed_range)
            
            # Calculate velocity
            velocity = pygame.Vector2(
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
            
            # Random lifetime and size
            lifetime = random.uniform(*lifetime_range)
            size = random.uniform(*size_range)
            
            # Create particle with slight color variation
            color_variation = 20
            varied_color = tuple(
                min(255, max(0, c + random.randint(-color_variation, color_variation)))
                for c in color
            )
            
            particle = cls(game, position, velocity, varied_color, lifetime, size)
            particles.append(particle)
            
        return particles 