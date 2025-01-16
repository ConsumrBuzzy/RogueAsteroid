"""
Particle system for visual effects.
"""

import random
import pygame
from typing import TYPE_CHECKING
from .system import System
from .components import Position, Velocity, Renderable
from .game_components import Lifetime, EntityTag, EntityType
from .sprite_manager import SpriteResource

if TYPE_CHECKING:
    from .world import World

class ParticleSystem(System):
    """Handles particle creation, updates, and cleanup."""
    
    def update(self, world: 'World', dt: float) -> None:
        # Update existing particles
        for entity, (lifetime, pos, vel) in world.get_components(Lifetime, Position, Velocity):
            tag = world.get_component(entity, EntityTag)
            if not tag or tag.type != EntityType.PARTICLE:
                continue
            
            # Update lifetime
            lifetime.remaining -= dt
            
            # Remove expired particles
            if lifetime.remaining <= 0:
                world.destroy_entity(entity)
                continue
            
            # Fade out particle
            renderable = world.get_component(entity, Renderable)
            if renderable and renderable.texture:
                alpha = int((lifetime.remaining / lifetime.total) * 255)
                renderable.texture.set_alpha(alpha)
    
    def create_explosion(self, world: 'World', x: float, y: float, scale: float = 1.0) -> None:
        """Create an explosion effect at the given position."""
        sprites = world.resources.get(SpriteResource)
        if not sprites:
            return
            
        num_particles = int(10 * scale)
        
        for _ in range(num_particles):
            particle = world.create_entity()
            
            # Random velocity
            angle = random.random() * 2 * 3.14159
            speed = random.uniform(50, 150) * scale
            vel_x = pygame.math.cos(angle) * speed
            vel_y = pygame.math.sin(angle) * speed
            
            # Add components
            world.add_component(particle, Position(x=x, y=y))
            world.add_component(particle, Velocity(dx=vel_x, dy=vel_y))
            world.add_component(particle, Lifetime(
                total=random.uniform(0.5, 1.0),
                remaining=random.uniform(0.5, 1.0)
            ))
            world.add_component(particle, EntityTag(type=EntityType.PARTICLE))
            
            # Add renderable if sprite exists
            if explosion_sprite := sprites.sprites.get("particle_explosion"):
                world.add_component(particle, Renderable(
                    texture=explosion_sprite.copy(),
                    width=8,
                    height=8,
                    layer=10  # Particles render above most things
                ))
    
    def create_thrust(self, world: 'World', x: float, y: float, angle: float) -> None:
        """Create a thrust effect behind the ship."""
        sprites = world.resources.get(SpriteResource)
        if not sprites:
            return
            
        particle = world.create_entity()
        
        # Velocity opposite to ship direction
        vel_x = -pygame.math.cos(angle) * random.uniform(50, 100)
        vel_y = pygame.math.sin(angle) * random.uniform(50, 100)
        
        # Add components
        world.add_component(particle, Position(x=x, y=y))
        world.add_component(particle, Velocity(dx=vel_x, dy=vel_y))
        world.add_component(particle, Lifetime(
            total=0.3,
            remaining=0.3
        ))
        world.add_component(particle, EntityTag(type=EntityType.PARTICLE))
        
        # Add renderable if sprite exists
        if thrust_sprite := sprites.sprites.get("particle_thrust"):
            world.add_component(particle, Renderable(
                texture=thrust_sprite.copy(),
                width=4,
                height=4,
                layer=5  # Below ship but above most things
            ))
