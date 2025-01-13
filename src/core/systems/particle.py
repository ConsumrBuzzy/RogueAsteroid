"""Particle system for managing particle effects."""
import pygame
import random
import math
from src.entities.particle import Particle
from src.core.entities.components import TransformComponent, PhysicsComponent

class ParticleSystem:
    """System for managing particle effects."""
    
    def __init__(self, game):
        self.game = game
        self.particles = []  # Track active particles
    
    def update(self, dt: float) -> None:
        """Update all active particles."""
        pass  # Particles handle their own updates
    
    def create_explosion(self, pos: pygame.Vector2, size: str = 'large') -> None:
        """Create an explosion effect.
        
        Args:
            pos: Position of the explosion
            size: Size of explosion ('small', 'medium', or 'large')
        """
        # Configure explosion based on size
        if size == 'large':
            count = 12
            speed = 200
            lifetime = (0.6, 0.8)
            particle_size = (3.0, 4.0)
        elif size == 'medium':
            count = 8
            speed = 150
            lifetime = (0.4, 0.6)
            particle_size = (2.0, 3.0)
        else:  # small
            count = 5
            speed = 100
            lifetime = (0.2, 0.4)
            particle_size = (1.0, 2.0)
            
        # Emit particles in a circle
        self.emit_circular(
            center=pos,
            speed=speed,
            color=(255, 165, 0),  # Orange
            size=random.uniform(*particle_size),
            lifetime=random.uniform(*lifetime),
            count=count,
            spread=360.0
        )
    
    def emit_circular(self, position, color, count, lifetime, speed_range, size_range=(1, 3)):
        """Emit particles in a circular pattern."""
        for _ in range(count):
            # Create particle
            particle = Particle(
                self.game,
                lifetime=random.uniform(*lifetime),
                color=color,
                size=random.uniform(*size_range)
            )
            
            # Set position
            transform = particle.get_component(TransformComponent)
            if transform:
                transform.position = pygame.Vector2(position)
                
                # Random direction and speed
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(*speed_range)
                
                # Set velocity in physics component
                physics = particle.get_component(PhysicsComponent)
                if physics:
                    physics.velocity = pygame.Vector2(
                        math.cos(angle) * speed,
                        math.sin(angle) * speed
                    )
            
            # Add to game
            self.game.entity_manager.add_entity(particle)
    
    def emit_cone(self, pos: pygame.Vector2, direction: float, speed: float,
                  color: tuple, size: float, lifetime: float, count: int,
                  spread: float = 30.0) -> None:
        """Emit particles in a cone pattern."""
        half_spread = spread / 2
        for _ in range(count):
            # Create particle
            particle = Particle(self.game, lifetime, color, size)
            
            # Set position
            transform = particle.get_component(TransformComponent)
            if transform:
                transform.position = pygame.Vector2(pos)
                
                # Calculate random angle within cone
                angle = direction + random.uniform(-half_spread, half_spread)
                angle_rad = math.radians(angle)
                
                # Add some speed variation
                actual_speed = speed * random.uniform(0.8, 1.2)
                
                # Set velocity based on angle
                physics = particle.get_component(PhysicsComponent)
                if physics:
                    physics.velocity = pygame.Vector2(
                        math.cos(angle_rad) * actual_speed,
                        math.sin(angle_rad) * actual_speed
                    ) 