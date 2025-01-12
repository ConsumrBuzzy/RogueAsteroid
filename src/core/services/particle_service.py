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
    
    # Resource limits
    MAX_PARTICLES = 1000
    MAX_PARTICLES_PER_EFFECT = 100
    
    def __init__(self, screen: pygame.Surface):
        """Initialize the particle service.
        
        Args:
            screen: Pygame surface to render to
            
        Raises:
            ValueError: If screen is None
        """
        if screen is None:
            raise ValueError("Screen surface cannot be None")
            
        self._screen = screen
        self._particles: List[Particle] = []
        self._templates: Dict[str, ParticleTemplate] = {}
        self._active_effects: Dict[str, int] = {}  # Track particles per effect
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
        
    def emit(self, template_name: str, position: tuple, direction: float = 0, count: int = 1) -> bool:
        """Emit particles using a template.
        
        Args:
            template_name: Name of particle template to use
            position: (x, y) position to emit from
            direction: Direction in radians
            count: Number of particles to emit
            
        Returns:
            bool: True if particles were emitted, False if limits reached
            
        Raises:
            ValueError: If template_name doesn't exist
        """
        if template_name not in self._templates:
            raise ValueError(f"Unknown particle template: {template_name}")
            
        # Check global particle limit
        if len(self._particles) >= self.MAX_PARTICLES:
            print(f"Warning: Global particle limit reached ({self.MAX_PARTICLES})")
            return False
            
        # Check per-effect limit
        current_count = self._active_effects.get(template_name, 0)
        if current_count >= self.MAX_PARTICLES_PER_EFFECT:
            print(f"Warning: Per-effect particle limit reached for {template_name}")
            return False
            
        # Create particles
        template = self._templates[template_name]
        new_count = min(count, self.MAX_PARTICLES - len(self._particles))
        new_count = min(new_count, self.MAX_PARTICLES_PER_EFFECT - current_count)
        
        for _ in range(new_count):
            particle = template.create_particle(position, direction)
            self._particles.append(particle)
            
        # Update effect count
        self._active_effects[template_name] = current_count + new_count
        return True
        
    def update(self, dt: float) -> None:
        """Update all particles.
        
        Args:
            dt: Time delta in seconds
        """
        # Reset effect counts
        self._active_effects.clear()
        
        # Update and filter particles
        active_particles = []
        for particle in self._particles:
            particle.update(dt)
            if particle.is_alive():
                active_particles.append(particle)
                # Track effect counts
                self._active_effects[particle.template_name] = \
                    self._active_effects.get(particle.template_name, 0) + 1
                    
        self._particles = active_particles
        
    def draw(self) -> None:
        """Draw all particles."""
        try:
            for particle in self._particles:
                particle.draw(self._screen)
        except pygame.error as e:
            print(f"Warning: Error drawing particles: {e}")
            
    def clear(self) -> None:
        """Clear all particles."""
        self._particles.clear()
        self._active_effects.clear()
        
    def cleanup(self) -> None:
        """Clean up resources."""
        self.clear()
        self._templates.clear()
        print("ParticleService cleaned up")
        
    def get_stats(self) -> Dict:
        """Get particle system statistics.
        
        Returns:
            Dict containing particle counts and limits
        """
        return {
            "total_particles": len(self._particles),
            "max_particles": self.MAX_PARTICLES,
            "effects": self._active_effects.copy(),
            "max_per_effect": self.MAX_PARTICLES_PER_EFFECT
        } 