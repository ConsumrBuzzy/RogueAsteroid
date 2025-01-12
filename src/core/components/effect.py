"""Effect component for visual effects."""
import pygame
import random
import math
from typing import List, Tuple, Optional, Dict
from enum import Enum, auto

from .base import Component
from ..config.effects import EFFECT_TEMPLATES, validate_template

class Particle:
    """Individual particle in a particle system."""
    
    def __init__(self, x: float, y: float, velocity: Tuple[float, float],
                 color: Tuple[int, int, int], lifetime: float, size: float = 1.0):
        """Initialize particle.
        
        Args:
            x: Initial x position
            y: Initial y position
            velocity: (vx, vy) velocity tuple
            color: RGB color tuple
            lifetime: Time in seconds before particle dies
            size: Particle size in pixels
        """
        self.x = x
        self.y = y
        self.vx, self.vy = velocity
        self.color = color
        self.lifetime = lifetime
        self.max_lifetime = lifetime
        self.size = size
        self.alpha = 255
    
    def update(self, dt: float) -> bool:
        """Update particle state.
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            True if particle is still alive, False if it should be removed
        """
        self.x += self.vx * dt
        self.y += self.vy * dt
        self.lifetime -= dt
        
        # Fade out as lifetime decreases
        self.alpha = int(255 * (self.lifetime / self.max_lifetime))
        
        return self.lifetime > 0

class EffectComponent(Component):
    """Component for managing particle effects and visual feedback.
    
    Provides:
    - Particle system management
    - Effect templates
    - Visual feedback
    - Performance optimization
    """
    
    def __init__(self, entity):
        """Initialize effect component.
        
        Args:
            entity: Entity this component belongs to
        """
        super().__init__(entity)
        self._particles: List[Particle] = []
        self._effect_templates: Dict[str, dict] = {}
        
        # Load default templates
        for name, template in EFFECT_TEMPLATES.items():
            self.add_effect_template(name, template)
            
        print("EffectComponent initialized")
    
    def update(self, dt: float) -> None:
        """Update all active particles.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return
            
        # Update and filter particles
        self._particles = [p for p in self._particles if p.update(dt)]
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all active particles.
        
        Args:
            screen: Pygame surface to draw on
        """
        if not self.enabled:
            return
            
        # Create temporary surface for alpha blending
        temp_surface = pygame.Surface(screen.get_size(), pygame.SRCALPHA)
        
        # Draw all particles
        for particle in self._particles:
            pygame.draw.circle(
                temp_surface,
                (*particle.color, particle.alpha),
                (int(particle.x), int(particle.y)),
                particle.size
            )
        
        # Blit temporary surface to screen
        screen.blit(temp_surface, (0, 0))
    
    def emit(self, effect_type: str, position: Optional[Tuple[float, float]] = None,
             direction: float = 0) -> None:
        """Emit particles using a predefined effect template.
        
        Args:
            effect_type: Name of effect template to use
            position: Optional emission position (uses entity position if None)
            direction: Base direction for particle emission in degrees
        """
        if effect_type not in self._effect_templates:
            print(f"Warning: Unknown effect type '{effect_type}'")
            return
            
        # Get entity position if none provided
        if position is None:
            transform = self.get_sibling_component('TransformComponent')
            if not transform:
                return
            position = (transform.x, transform.y)
        
        # Get template settings
        template = self._effect_templates[effect_type]
        
        # Create particles based on template
        for _ in range(template['count']):
            # Calculate random angle within spread
            angle = direction + random.uniform(
                -template['angle_spread']/2,
                template['angle_spread']/2
            )
            angle_rad = math.radians(angle)
            
            # Calculate random speed
            speed = random.uniform(*template['speed_range'])
            
            # Calculate velocity components
            velocity = (
                math.cos(angle_rad) * speed,
                math.sin(angle_rad) * speed
            )
            
            # Create particle with random properties from ranges
            particle = Particle(
                position[0],
                position[1],
                velocity,
                random.choice(template['colors']),
                random.uniform(*template['lifetime_range']),
                random.uniform(*template['size_range'])
            )
            
            self._particles.append(particle)
    
    def add_effect_template(self, name: str, template: dict) -> None:
        """Add or update an effect template.
        
        Args:
            name: Name of the effect template
            template: Dictionary of effect parameters
            
        Raises:
            ValueError: If template is invalid
        """
        # Validate template before adding
        validate_template(name, template)
        self._effect_templates[name] = template
        print(f"Added effect template: {name}")
    
    def clear_particles(self) -> None:
        """Remove all active particles."""
        self._particles.clear()
        print("Cleared all particles")
    
    @property
    def particle_count(self) -> int:
        """Get number of active particles."""
        return len(self._particles)
        
    def destroy(self) -> None:
        """Clean up component resources."""
        self.clear_particles()
        self._effect_templates.clear()
        super().destroy() 