"""Particle system for managing particle effects."""
import pygame
import random
import math
from src.entities.particle import Particle

class ParticleSystem:
    """System for managing particle effects."""
    
    def __init__(self, game):
        self.game = game
        self.particles = []  # Track active particles
    
    def update(self, dt: float) -> None:
        """Update all active particles.
        
        Args:
            dt: Delta time in seconds
        """
        # Let particles update themselves - they will remove themselves when done
        pass  # No need to do anything since particles handle their own updates
    
    def emit_circular(self, center: pygame.Vector2, speed: float, color: tuple,
                     size: float, lifetime: float, count: int,
                     spread: float = 360.0) -> None:
        """Emit particles in a circular pattern.
        
        Args:
            center: Center position to emit from
            speed: Base speed of particles
            color: RGB color tuple
            size: Size of particles
            lifetime: How long particles should live
            count: Number of particles to emit
            spread: Angle in degrees to spread particles over (360 for full circle)
        """
        for _ in range(count):
            # Create particle
            particle = Particle(self.game, lifetime, color, size)
            
            # Set position
            transform = particle.get_component(TransformComponent)
            if transform:
                transform.position = pygame.Vector2(center)
                
                # Calculate random angle within spread
                base_angle = random.uniform(0, spread)
                angle_rad = math.radians(base_angle)
                
                # Add some speed variation
                actual_speed = speed * random.uniform(0.8, 1.2)
                
                # Set velocity based on angle
                physics = particle.get_component(PhysicsComponent)
                if physics:
                    physics.velocity = pygame.Vector2(
                        math.cos(angle_rad) * actual_speed,
                        math.sin(angle_rad) * actual_speed
                    )
            
            # Add to game
            self.game.entities.append(particle)
    
    def emit_cone(self, pos: pygame.Vector2, direction: float, speed: float,
                  color: tuple, size: float, lifetime: float, count: int,
                  spread: float = 30.0) -> None:
        """Emit particles in a cone pattern.
        
        Args:
            pos: Position to emit from
            direction: Base angle in degrees
            speed: Base speed of particles
            color: RGB color tuple
            size: Size of particles
            lifetime: How long particles should live
            count: Number of particles to emit
            spread: Total spread angle of cone in degrees
        """
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