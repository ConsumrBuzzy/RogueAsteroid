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
        # Get all renderable entities and sort by layer
        renderables = sorted(
            world.get_components(Position, Renderable),
            key=lambda x: x[1][1].layer
        )
        
        screen = pygame.display.get_surface()
        
        for _, (pos, render) in renderables:
            if not render.visible or not render.texture:
                continue
                
            # Get the rotated surface
            rotated = pygame.transform.rotate(render.texture, -pos.rotation)
            
            # Get the new rect centered at the entity's position
            rect = rotated.get_rect(center=(pos.x, pos.y))
            
            # Draw to screen
            screen.blit(rotated, rect)
