"""Particle system module."""
import pygame
import random
import math
from typing import List, Tuple, Optional

class Particle:
    """Individual particle class."""
    def __init__(self, pos: Tuple[float, float], velocity: Tuple[float, float],
                 color: Tuple[int, int, int], size: float, lifetime: float,
                 acceleration: Optional[Tuple[float, float]] = None,
                 fade: bool = False, size_change: float = 0):
        self.pos = pygame.Vector2(pos)
        self.velocity = pygame.Vector2(velocity)
        self.acceleration = pygame.Vector2(acceleration) if acceleration else pygame.Vector2(0, 0)
        self.color = list(color)  # Convert to list for modification
        self.initial_color = color
        self.size = size
        self.initial_size = size
        self.size_change = size_change
        self.lifetime = lifetime
        self.initial_lifetime = lifetime
        self.fade = fade

class ParticleSystem:
    """System for managing particles."""
    def __init__(self, game):
        self.game = game
        self.particles: List[Particle] = []
        self.paused = False
    
    def create_particle(self, pos: Tuple[float, float], velocity: Tuple[float, float],
                       color: Tuple[int, int, int], size: float, lifetime: float,
                       acceleration: Optional[Tuple[float, float]] = None,
                       fade: bool = False, size_change: float = 0) -> Particle:
        """Create a new particle."""
        particle = Particle(pos, velocity, color, size, lifetime,
                          acceleration, fade, size_change)
        self.particles.append(particle)
        return particle
    
    def emit_circular(self, center: Tuple[float, float], speed: float,
                     color: Tuple[int, int, int], size: float, lifetime: float,
                     count: int = 8) -> None:
        """Emit particles in a circular pattern."""
        angle_step = 360 / count
        for i in range(count):
            angle = math.radians(i * angle_step)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.create_particle(center, velocity, color, size, lifetime)
    
    def emit_cone(self, pos: Tuple[float, float], direction: float,
                  spread: float, speed: float, color: Tuple[int, int, int],
                  size: float, lifetime: float, count: int = 5) -> None:
        """Emit particles in a cone pattern."""
        half_spread = spread / 2
        for _ in range(count):
            angle = math.radians(direction + random.uniform(-half_spread, half_spread))
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            self.create_particle(pos, velocity, color, size, lifetime)
    
    def update(self, dt: float) -> None:
        """Update all particles."""
        if self.paused:
            return
        
        # Update particles in reverse order for safe removal
        for i in range(len(self.particles) - 1, -1, -1):
            particle = self.particles[i]
            
            # Update lifetime
            particle.lifetime -= dt
            if particle.lifetime <= 0:
                self.particles.pop(i)
                continue
            
            # Update velocity
            particle.velocity += particle.acceleration * dt
            
            # Update position
            particle.pos += particle.velocity * dt
            
            # Update size
            if particle.size_change != 0:
                life_fraction = particle.lifetime / particle.initial_lifetime
                particle.size = particle.initial_size + \
                              (particle.size_change * (1 - life_fraction))
            
            # Update color for fade effect
            if particle.fade:
                life_fraction = particle.lifetime / particle.initial_lifetime
                for i in range(3):
                    particle.color[i] = int(particle.initial_color[i] * life_fraction)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw all particles."""
        for particle in self.particles:
            # Calculate alpha for fade effect
            alpha = int(255 * (particle.lifetime / particle.initial_lifetime))
            color_with_alpha = (*particle.color, alpha)
            
            # Create surface for particle
            size = max(1, int(particle.size * 2))
            particle_surface = pygame.Surface((size, size), pygame.SRCALPHA)
            
            # Draw particle
            pygame.draw.circle(
                particle_surface,
                color_with_alpha,
                (size // 2, size // 2),
                max(1, int(particle.size))
            )
            
            # Draw to main surface
            pos = (int(particle.pos.x - particle.size),
                  int(particle.pos.y - particle.size))
            surface.blit(particle_surface, pos)
    
    def clear(self) -> None:
        """Remove all particles."""
        self.particles.clear() 