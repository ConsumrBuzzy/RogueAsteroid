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

class Effect:
    """Individual visual effect."""
    
    def __init__(self, vertices: List[Tuple[float, float]], color: Tuple[int, int, int], 
                 offset: pygame.Vector2):
        """Initialize effect.
        
        Args:
            vertices: List of points defining effect shape
            color: RGB color tuple
            offset: Offset from entity position
        """
        self.vertices = vertices
        self.color = color
        self.offset = offset
        self.active = False
        self.lifetime = 0
        self.particles: List[Particle] = []

class EffectComponent(Component):
    """Component for managing visual effects.
    
    Provides:
    - Effect templates
    - Particle systems
    - Effect triggers
    - Effect lifecycle
    """
    
    def __init__(self, entity):
        """Initialize effect component.
        
        Args:
            entity: Entity this component belongs to
        """
        super().__init__(entity)
        self.effects: Dict[str, Effect] = {}
        self._templates = EFFECT_TEMPLATES.copy()
        
        # Initialize default effects
        self._init_default_effects()
        
        print("EffectComponent initialized")
    
    def _init_default_effects(self):
        """Initialize default effect templates."""
        # Add default templates
        self.add_effect_template('thrust', {
            'count': 10,
            'speed_range': (50, 100),
            'angle_spread': 30,
            'lifetime_range': (0.2, 0.4),
            'size_range': (1, 2),
            'colors': [(255, 200, 50), (255, 100, 0), (200, 50, 0)]
        })
        
        self.add_effect_template('explosion', {
            'count': 20,
            'speed_range': (100, 200),
            'angle_spread': 360,
            'lifetime_range': (0.5, 1.0),
            'size_range': (2, 4),
            'colors': [(255, 200, 50), (255, 100, 0), (200, 50, 0)]
        })
        
        self.add_effect_template('sparkle', {
            'count': 5,
            'speed_range': (20, 50),
            'angle_spread': 360,
            'lifetime_range': (0.2, 0.5),
            'size_range': (1, 2),
            'colors': [(255, 255, 200), (255, 255, 100)]
        })
        
        self.add_effect_template('impact', {
            'count': 8,
            'speed_range': (80, 150),
            'angle_spread': 90,
            'lifetime_range': (0.2, 0.4),
            'size_range': (1, 3),
            'colors': [(255, 255, 255), (200, 200, 255)]
        })
        
        self.add_effect_template('debris', {
            'count': 12,
            'speed_range': (30, 80),
            'angle_spread': 360,
            'lifetime_range': (0.8, 1.5),
            'size_range': (2, 4),
            'colors': [(150, 150, 150), (100, 100, 100)]
        })
    
    def add_effect_template(self, name: str, template: dict) -> None:
        """Add a new effect template.
        
        Args:
            name: Template name
            template: Template parameters
        """
        if validate_template(name, template):
            self._templates[name] = template
            print(f"Added effect template: {name}")
    
    def add_effect(self, name: str, vertices: List[Tuple[float, float]], 
                  color: Tuple[int, int, int], offset: pygame.Vector2) -> None:
        """Add a new effect.
        
        Args:
            name: Effect name
            vertices: List of points defining effect shape
            color: RGB color tuple
            offset: Offset from entity position
        """
        self.effects[name] = Effect(vertices, color, offset)
    
    def emit(self, template_name: str, position: pygame.Vector2, direction: pygame.Vector2 | float) -> None:
        """Emit particles using a template.
        
        Args:
            template_name: Name of template to use
            position: Emission position
            direction: Emission direction (Vector2 or angle in radians)
        """
        template = self._templates.get(template_name)
        if not template:
            return
            
        # Create particles based on template
        count = template['count']
        speed_min, speed_max = template['speed_range']
        angle_spread = template['angle_spread']
        lifetime_min, lifetime_max = template['lifetime_range']
        size_min, size_max = template['size_range']
        colors = template['colors']
        
        # Handle direction as either Vector2 or angle
        if isinstance(direction, pygame.Vector2):
            base_angle = math.atan2(direction.y, direction.x)
        else:
            base_angle = float(direction)
        
        for _ in range(count):
            # Randomize particle properties
            angle = base_angle + math.radians(random.uniform(-angle_spread/2, angle_spread/2))
            speed = random.uniform(speed_min, speed_max)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            lifetime = random.uniform(lifetime_min, lifetime_max)
            size = random.uniform(size_min, size_max)
            color = random.choice(colors)
            
            # Create and add particle
            particle = Particle(position.x, position.y, velocity, color, lifetime, size)
            self.effects.setdefault(template_name, Effect([], color, pygame.Vector2())).particles.append(particle)
    
    def update(self, dt: float) -> None:
        """Update effects and particles.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.active:
            return
            
        # Update all effects
        for effect in self.effects.values():
            # Update particles
            effect.particles = [p for p in effect.particles if p.update(dt)]
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw effects and particles.
        
        Args:
            surface: Surface to draw on
        """
        if not self.active:
            return
            
        transform = self.entity.get_component('TransformComponent')
        if not transform:
            return
            
        # Draw all effects
        for effect in self.effects.values():
            if effect.active and effect.vertices:
                # Transform vertices
                transformed = []
                for x, y in effect.vertices:
                    # Apply offset and entity position
                    pos = pygame.Vector2(x, y) + effect.offset
                    if transform.rotation != 0:
                        pos = pos.rotate(transform.rotation)
                    transformed.append((pos.x + transform.x, pos.y + transform.y))
                
                # Draw effect shape
                if len(transformed) > 2:
                    pygame.draw.polygon(surface, effect.color, transformed)
                elif len(transformed) == 2:
                    pygame.draw.line(surface, effect.color, transformed[0], transformed[1])
                else:
                    pygame.draw.circle(surface, effect.color, transformed[0], 1)
            
            # Draw particles
            for particle in effect.particles:
                # Calculate alpha
                color = list(particle.color)
                if len(color) == 3:
                    color.append(particle.alpha)
                
                # Draw particle
                pygame.draw.circle(surface, color, (int(particle.x), int(particle.y)), 
                                 int(particle.size)) 