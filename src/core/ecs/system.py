"""
Base system class and core game systems.
"""

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import pygame
from .components import Position, Velocity, Input, Renderable, Collider
from .events import CollisionEvent

if TYPE_CHECKING:
    from .world import World

class System(ABC):
    """Base class for all systems."""
    
    @abstractmethod
    def update(self, world: 'World', dt: float) -> None:
        """Update the system state."""
        pass

class PhysicsSystem(System):
    """Handles physics updates for entities with Position and Velocity."""
    
    def update(self, world: 'World', dt: float) -> None:
        for _, (pos, vel) in world.get_components(Position, Velocity):
            # Update position based on velocity
            pos.x += vel.dx * dt
            pos.y += vel.dy * dt
            pos.rotation += vel.angular * dt

            # Screen wrapping (assuming screen dimensions are stored in world resources)
            screen_width = 800  # These should come from resources
            screen_height = 600
            
            pos.x = pos.x % screen_width
            pos.y = pos.y % screen_height

class CollisionSystem(System):
    """Handles collision detection between entities."""
    
    def update(self, world: 'World', dt: float) -> None:
        # Get all entities with Position and Collider
        entities = list(world.get_components(Position, Collider))
        
        # Check each pair of entities
        for i, (entity1, (pos1, col1)) in enumerate(entities):
            if not col1.active:
                continue
                
            for entity2, (pos2, col2) in entities[i + 1:]:
                if not col2.active:
                    continue
                    
                # Simple circle collision check
                distance = pygame.Vector2(pos1.x - pos2.x, pos1.y - pos2.y).length()
                if distance < (col1.radius + col2.radius):
                    # Emit collision event
                    world.events.emit(CollisionEvent(entity1, entity2))

class InputSystem(System):
    """Handles input processing for entities with Input component."""
    
    def update(self, world: 'World', dt: float) -> None:
        keys = pygame.key.get_pressed()
        
        for _, (input_comp,) in world.get_components(Input):
            # Update input state based on keyboard
            input_comp.thrust = keys[pygame.K_UP] or keys[pygame.K_w]
            input_comp.reverse = keys[pygame.K_DOWN] or keys[pygame.K_s]
            input_comp.rotate_left = keys[pygame.K_LEFT] or keys[pygame.K_a]
            input_comp.rotate_right = keys[pygame.K_RIGHT] or keys[pygame.K_d]
            input_comp.shoot = keys[pygame.K_SPACE]

class RenderSystem(System):
    """Handles rendering of entities with Position and Renderable components."""
    
    def update(self, world: 'World', dt: float) -> None:
        # Get the screen surface
        screen = pygame.display.get_surface()
        
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw all renderable entities
        for _, (pos, render) in world.get_components(Position, Renderable):
            if not render.visible:
                continue
                
            # Try to use sprite if available
            sprite = render.sprite
            
            if sprite:
                # Calculate sprite position (center-based)
                sprite_rect = sprite.get_rect()
                sprite_rect.centerx = int(pos.x)
                sprite_rect.centery = int(pos.y)
                
                # Create a rotated copy of the sprite
                if render.rotation != 0:
                    rotated_sprite = pygame.transform.rotate(sprite, -render.rotation)
                    sprite_rect = rotated_sprite.get_rect(center=sprite_rect.center)
                    screen.blit(rotated_sprite, sprite_rect)
                else:
                    screen.blit(sprite, sprite_rect)
            
            else:
                # Use vector shape if no sprite available
                shape = render.shape
                
                if not shape:
                    continue
                
                # Transform vertices based on position and rotation
                transformed_verts = []
                for x, y in shape:
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
        
        # Update display
        pygame.display.flip()
