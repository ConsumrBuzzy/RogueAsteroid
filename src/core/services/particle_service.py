"""Particle service for game-wide particle effects management."""
from typing import List, Dict, Optional, Tuple
import random
import math
import pygame
from ..entity import Entity

class ParticleTemplate:
    """Template for particle effect configuration."""
    def __init__(self, 
                 lifetime_range: Tuple[float, float],
                 speed_range: Tuple[float, float],
                 size_range: Tuple[float, float],
                 color: Tuple[int, int, int],
                 alpha_range: Tuple[int, int],
                 spread_angle: float = math.pi * 2):
        self.lifetime_range = lifetime_range
        self.speed_range = speed_range
        self.size_range = size_range
        self.color = color
        self.alpha_range = alpha_range
        self.spread_angle = spread_angle

class Particle:
    """Individual particle with position, velocity, and properties."""
    def __init__(self, x: float, y: float, template: ParticleTemplate, direction: float = 0):
        """Initialize a particle.
        
        Args:
            x: Initial x position
            y: Initial y position
            template: ParticleTemplate to use
            direction: Base direction in radians
        """
        self.x = x
        self.y = y
        self.lifetime = random.uniform(*template.lifetime_range)
        self.time_remaining = self.lifetime
        self.size = random.uniform(*template.size_range)
        self.alpha = random.randint(*template.alpha_range)
        
        # Calculate velocity
        speed = random.uniform(*template.speed_range)
        angle = direction + random.uniform(-template.spread_angle/2, template.spread_angle/2)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        
        self.color = template.color

class ParticleService:
    """Service for game-wide particle effect management.
    
    Provides:
    - Particle system management
    - Effect templates
    - Performance optimization
    - Visual feedback
    """
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the particle service.
        
        Args:
            screen: Pygame surface to render to
        """
        self._screen = screen
        self._particles: List[Particle] = []
        self._templates: Dict[str, ParticleTemplate] = {}
        self._setup_default_templates()
        print("ParticleService initialized")
        
    def _setup_default_templates(self) -> None:
        """Set up default particle effect templates."""
        self._templates["thrust"] = ParticleTemplate(
            lifetime_range=(0.2, 0.4),
            speed_range=(50, 100),
            size_range=(2, 4),
            color=(255, 165, 0),
            alpha_range=(128, 255),
            spread_angle=math.pi/4
        )
        
        self._templates["explosion"] = ParticleTemplate(
            lifetime_range=(0.5, 1.0),
            speed_range=(100, 200),
            size_range=(3, 6),
            color=(255, 0, 0),
            alpha_range=(192, 255)
        )
        
        self._templates["sparkle"] = ParticleTemplate(
            lifetime_range=(0.3, 0.6),
            speed_range=(20, 40),
            size_range=(1, 2),
            color=(255, 255, 255),
            alpha_range=(128, 255)
        )
        
    def register_template(self, name: str, template: ParticleTemplate) -> None:
        """Register a new particle effect template.
        
        Args:
            name: Template name
            template: ParticleTemplate to register
        """
        self._templates[name] = template
        print(f"Registered particle template: {name}")
        
    def emit(self, template_name: str, x: float, y: float, 
             count: int, direction: float = 0) -> None:
        """Emit particles using a template.
        
        Args:
            template_name: Name of template to use
            x: Emission x position
            y: Emission y position
            count: Number of particles to emit
            direction: Base direction in radians
        """
        if template_name not in self._templates:
            print(f"Unknown particle template: {template_name}")
            return
            
        template = self._templates[template_name]
        for _ in range(count):
            self._particles.append(Particle(x, y, template, direction))
            
    def update(self, dt: float) -> None:
        """Update all active particles.
        
        Args:
            dt: Delta time in seconds
        """
        # Update particles in reverse to safely remove dead ones
        for i in range(len(self._particles) - 1, -1, -1):
            particle = self._particles[i]
            
            # Update lifetime
            particle.time_remaining -= dt
            if particle.time_remaining <= 0:
                self._particles.pop(i)
                continue
                
            # Update position
            particle.x += particle.vx * dt
            particle.y += particle.vy * dt
            
            # Update alpha based on remaining lifetime
            life_fraction = particle.time_remaining / particle.lifetime
            particle.alpha = int(255 * life_fraction)
            
    def draw(self) -> None:
        """Draw all active particles."""
        for particle in self._particles:
            # Create surface for particle
            surface = pygame.Surface((particle.size * 2, particle.size * 2), pygame.SRCALPHA)
            
            # Draw particle
            pygame.draw.circle(
                surface,
                (*particle.color, particle.alpha),
                (particle.size, particle.size),
                particle.size
            )
            
            # Blit to screen
            self._screen.blit(
                surface,
                (particle.x - particle.size, particle.y - particle.size)
            )
            
    def clear(self) -> None:
        """Clear all active particles."""
        self._particles.clear()
        print("Particle service cleared") 