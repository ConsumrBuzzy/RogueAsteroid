"""
Core game systems for the ECS architecture.
"""

import math
import random
import pygame
from typing import List, Tuple, Optional
from .components import (
    Position, Velocity, Input, Renderable, Collider,
    Physics, Player, Bullet, Asteroid, Particle, Sound
)
from .resources import WindowInfo, GameState, SpriteResource, AudioResource
from .events import CollisionEvent, ScoreEvent

class System:
    """Base class for all systems."""
    def update(self, world: 'World', dt: float) -> None:
        """Update the system.
        
        Args:
            world: The game world
            dt: Delta time in seconds
        """
        pass

class InputSystem(System):
    """Handles input processing."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Process input state."""
        keys = pygame.key.get_pressed()
        
        for entity, (input_comp,) in world.get_components(Input):
            # Update input state
            input_comp.up = keys[pygame.K_UP] or keys[pygame.K_w]
            input_comp.down = keys[pygame.K_DOWN] or keys[pygame.K_s]
            input_comp.left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            input_comp.right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            input_comp.fire = keys[pygame.K_SPACE]

class PhysicsSystem(System):
    """Handles physics simulation."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update physics for all entities with Position and Velocity."""
        window = world.resources.get(WindowInfo)
        if not window:
            return
        
        for entity, (pos, vel, physics) in world.get_components(Position, Velocity, Physics):
            # Update position based on velocity
            pos.x += vel.x * dt
            pos.y += vel.y * dt
            
            # Apply friction
            if physics.friction > 0:
                vel.x *= (1.0 - physics.friction * dt)
                vel.y *= (1.0 - physics.friction * dt)
            
            # Screen wrapping
            if pos.x < 0:
                pos.x = window.width
            elif pos.x > window.width:
                pos.x = 0
            
            if pos.y < 0:
                pos.y = window.height
            elif pos.y > window.height:
                pos.y = 0

class CollisionSystem(System):
    """Handles collision detection."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Check for collisions between entities."""
        # Get all entities with Position and Collider
        colliders = list(world.get_components(Position, Collider))
        
        # Check each pair of entities
        for i, (entity1, (pos1, col1)) in enumerate(colliders):
            if not col1.active:
                continue
                
            for entity2, (pos2, col2) in colliders[i + 1:]:
                if not col2.active:
                    continue
                
                # Skip if collision masks don't match
                if not (col1.mask & col2.mask):
                    continue
                
                # Calculate distance between entities
                dx = pos2.x - pos1.x
                dy = pos2.y - pos1.y
                distance = math.sqrt(dx * dx + dy * dy)
                
                # Check if collision occurred
                if distance < col1.radius + col2.radius:
                    world.events.emit(CollisionEvent(entity1, entity2))

class RenderSystem(System):
    """Handles rendering."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Render all entities with Position and Renderable components."""
        window = world.resources.get(WindowInfo)
        if not window:
            return
        
        screen = pygame.display.get_surface()
        if not screen:
            return
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Get all renderable entities and sort by layer
        renderables = sorted(
            world.get_components(Position, Renderable),
            key=lambda x: x[1][1].layer
        )
        
        # Draw each entity
        for entity, (pos, render) in renderables:
            if not render.visible:
                continue
            
            # Skip if blinking and in invisible phase
            if render.blink:
                render.blink_timer += dt
                if render.blink_timer % (render.blink_rate * 2) < render.blink_rate:
                    continue
            
            # Try to use sprite if available
            if render.sprite:
                # Calculate sprite position (center-based)
                sprite_rect = render.sprite.get_rect()
                sprite_rect.centerx = int(pos.x)
                sprite_rect.centery = int(pos.y)
                
                # Create a rotated copy of the sprite
                if render.rotation != 0:
                    rotated_sprite = pygame.transform.rotate(render.sprite, -render.rotation)
                    sprite_rect = rotated_sprite.get_rect(center=sprite_rect.center)
                    screen.blit(rotated_sprite, sprite_rect)
                else:
                    screen.blit(render.sprite, sprite_rect)
            
            # Use vector shape if no sprite
            elif render.shape:
                # Transform vertices based on position and rotation
                transformed_verts = []
                for x, y in render.shape:
                    if render.rotation != 0:
                        angle = math.radians(render.rotation)
                        rx = x * math.cos(angle) - y * math.sin(angle)
                        ry = x * math.sin(angle) + y * math.cos(angle)
                        x, y = rx, ry
                    
                    transformed_verts.append((
                        int(pos.x + x),
                        int(pos.y + y)
                    ))
                
                # Draw the shape
                if len(transformed_verts) == 1:
                    # Single point for particles
                    pygame.draw.circle(
                        screen,
                        render.color,
                        transformed_verts[0],
                        render.size
                    )
                else:
                    # Line shape for other entities
                    pygame.draw.polygon(
                        screen,
                        render.color,
                        transformed_verts,
                        render.line_width
                    )

class ParticleSystem(System):
    """Handles particle effects."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update particle lifetimes and effects."""
        for entity, (particle, render) in world.get_components(Particle, Renderable):
            # Update lifetime
            particle.time_alive += dt
            if particle.time_alive >= particle.lifetime:
                world.destroy_entity(entity)
                continue
            
            # Update effects
            life_ratio = particle.time_alive / particle.lifetime
            
            # Handle fading
            if particle.fade:
                render.alpha = int(255 * (1.0 - life_ratio))
            
            # Handle shrinking
            if particle.shrink:
                render.size = particle.size * (1.0 - life_ratio)

class SoundSystem(System):
    """Handles sound effects and music."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update sound states."""
        for entity, (sound,) in world.get_components(Sound):
            # Update volume for all sounds
            for sound_effect in sound.sounds.values():
                sound_effect.set_volume(sound.volume)

class MenuSystem(System):
    """Handles menu interaction."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update menu state."""
        # This will be implemented when we add menu functionality
        pass
