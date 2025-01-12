"""Particle service for game-wide particle effects management."""
from typing import List, Dict, Optional, Tuple
import random
import math
import pygame
from ..entity import Entity
from ..config.effects import EFFECT_TEMPLATES, validate_template

class ParticleTemplate:
    """Template for particle effect configuration."""
    def __init__(self, 
                 lifetime_range: Tuple[float, float],
                 speed_range: Tuple[float, float],
                 size_range: Tuple[float, float],
                 colors: List[Tuple[int, int, int]],
                 angle_spread: float = math.pi * 2,
                 count: int = 10):
        self.lifetime_range = lifetime_range
        self.speed_range = speed_range
        self.size_range = size_range
        self.colors = colors
        self.angle_spread = angle_spread
        self.count = count

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
        self.alpha = 255
        
        # Calculate velocity
        speed = random.uniform(*template.speed_range)
        angle = direction + random.uniform(-template.angle_spread/2, template.angle_spread/2)
        self.vx = speed * math.cos(angle)
        self.vy = speed * math.sin(angle)
        
        self.color = random.choice(template.colors)

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
        for name, config in EFFECT_TEMPLATES.items():
            template = ParticleTemplate(
                lifetime_range=config['lifetime_range'],
                speed_range=config['speed_range'],
                size_range=config['size_range'],
                colors=config['colors'],
                angle_spread=math.radians(config['angle_spread']),
                count=config['count']
            )
            self._templates[name] = template
            print(f"Loaded template: {name}")
    
    def register_template(self, name: str, config: dict) -> None:
        """Register a new particle effect template.
        
        Args:
            name: Template name
            config: Template configuration dictionary
            
        Raises:
            ValueError: If template configuration is invalid
        """
        # Validate configuration
        validate_template(name, config)
        
        # Create template
        template = ParticleTemplate(
            lifetime_range=config['lifetime_range'],
            speed_range=config['speed_range'],
            size_range=config['size_range'],
            colors=config['colors'],
            angle_spread=math.radians(config['angle_spread']),
            count=config['count']
        )
        
        self._templates[name] = template
        print(f"Registered particle template: {name}")
    
    def emit(self, template_name: str, position: tuple, direction: float = 0, count: Optional[int] = None) -> bool:
        """Emit particles using a template.
        
        Args:
            template_name: Name of particle template to use
            position: (x, y) position to emit from
            direction: Direction in radians
            count: Optional override for particle count
            
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
            
        # Get template and determine count
        template = self._templates[template_name]
        emit_count = count if count is not None else template.count
        new_count = min(emit_count, self.MAX_PARTICLES - len(self._particles))
        new_count = min(new_count, self.MAX_PARTICLES_PER_EFFECT - current_count)
        
        # Create particles
        for _ in range(new_count):
            particle = Particle(position[0], position[1], template, direction)
            self._particles.append(particle)
            
        # Update effect count
        self._active_effects[template_name] = current_count + new_count
        return True
    
    def update(self, dt: float) -> None:
        """Update all active particles.
        
        Args:
            dt: Delta time in seconds
        """
        # Update remaining time and remove dead particles
        active_particles = []
        for particle in self._particles:
            particle.time_remaining -= dt
            if particle.time_remaining > 0:
                # Update position
                particle.x += particle.vx * dt
                particle.y += particle.vy * dt
                # Update alpha for fade out
                particle.alpha = int(255 * (particle.time_remaining / particle.lifetime))
                active_particles.append(particle)
                
        # Update counts
        removed = len(self._particles) - len(active_particles)
        if removed > 0:
            # Distribute removals across effects (approximate)
            per_effect = removed // len(self._active_effects) if self._active_effects else 0
            for effect in self._active_effects:
                self._active_effects[effect] = max(0, self._active_effects[effect] - per_effect)
                
        self._particles = active_particles
    
    def draw(self, screen: Optional[pygame.Surface] = None) -> None:
        """Draw all active particles.
        
        Args:
            screen: Optional surface to draw on (uses service screen if None)
        """
        surface = screen if screen is not None else self._screen
        
        # Create temporary surface for alpha blending
        temp_surface = pygame.Surface(surface.get_size(), pygame.SRCALPHA)
        
        # Draw particles
        for particle in self._particles:
            pygame.draw.circle(
                temp_surface,
                (*particle.color, particle.alpha),
                (int(particle.x), int(particle.y)),
                particle.size
            )
            
        # Blit to target surface
        surface.blit(temp_surface, (0, 0))
    
    def clear(self) -> None:
        """Clear all active particles and reset counts."""
        self._particles.clear()
        self._active_effects.clear()
        print("Cleared all particles") 