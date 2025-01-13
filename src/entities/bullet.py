"""Bullet entity fired by the player ship."""
import random
import math
import pygame
from typing import TYPE_CHECKING
from src.core.entities.base import Entity
from src.core.entities.components import (
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    PhysicsComponent,
    ScreenWrapComponent
)
from src.core.constants import (
    WHITE,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    ASTEROID_SIZES
)
from src.entities.asteroid import Asteroid

if TYPE_CHECKING:
    from src.core.game import Game

class Bullet(Entity):
    """Projectile fired by the player ship."""
    
    LIFETIME = 0.5  # Reduced from 0.6 to 0.5 seconds
    SPEED = 1200  # pixels per second
    
    def __init__(self, game: 'Game', position: pygame.Vector2, direction: pygame.Vector2):
        """Initialize the bullet.
        
        Args:
            game: The game instance.
            position: Initial position as Vector2.
            direction: Direction vector (will be normalized).
        """
        super().__init__(game)
        self.lifetime = self.LIFETIME  # Time until bullet disappears
        # Normalize direction
        self.direction = direction.normalize()
        
        # Add components
        self._init_components(position, direction)
    
    def _init_components(self, position: pygame.Vector2, direction: pygame.Vector2) -> None:
        """Initialize bullet components."""
        # Transform component for position and movement
        transform = self.add_component(TransformComponent)
        transform.position = position
        
        # Physics component for movement
        physics = self.add_component(PhysicsComponent)
        physics.velocity = direction * self.SPEED
        physics.friction = 0.0  # No friction for bullets
        physics.max_speed = self.SPEED  # Don't let bullets slow down
        
        # Render component for drawing
        render = self.add_component(RenderComponent)
        render.vertices = [(0, -2), (0, 2)]  # Simple line shape
        render.color = WHITE
        
        # Collision component for hit detection
        collision = self.add_component(CollisionComponent, radius=2.0)
        
        # Screen wrap component to wrap around screen edges
        screen_wrap = self.add_component(ScreenWrapComponent)
    
    def update(self, dt: float) -> None:
        """Update bullet state."""
        super().update(dt)
        
        # Update lifetime and despawn if expired
        self.lifetime -= dt
        if self.lifetime <= 0:
            # Remove bullet from tracking lists
            if self in self.game.bullets:
                self.game.bullets.remove(self)
            if self in self.game.entities:
                self.game.entities.remove(self)
            return
        
        # Check for collisions with asteroids
        collision = self.get_component(CollisionComponent)
        if collision:
            for entity in self.game.entities[:]:  # Copy list to allow removal
                if isinstance(entity, Asteroid):
                    other_collision = entity.get_component(CollisionComponent)
                    if other_collision and collision.check_collision(other_collision):
                        # Handle asteroid hit and scoring
                        points = ASTEROID_SIZES[entity.size]['points']
                        self.game.scoring.add_points(points)
                        print(f"Hit asteroid size {entity.size}, awarded {points} points")  # Debug info
                        
                        # Split asteroid if not smallest size
                        if entity.size in ['large', 'medium']:
                            pieces = entity.split()
                            # Add new pieces to game
                            for piece in pieces:
                                self.game.asteroids.append(piece)
                                self.game.entities.append(piece)
                                print(f"Created new asteroid piece size {piece.size}")  # Debug info
                        
                        # Remove asteroid from tracking lists
                        if entity in self.game.asteroids:
                            self.game.asteroids.remove(entity)
                        if entity in self.game.entities:
                            self.game.entities.remove(entity)
                            
                        # Remove bullet from tracking lists
                        if self in self.game.bullets:
                            self.game.bullets.remove(self)
                        if self in self.game.entities:
                            self.game.entities.remove(self)
                        return 
    
    def destroy(self):
        """Remove the bullet from the game."""
        if self in self.game.entity_manager.entities:
            self.game.entity_manager.remove_entity(self)
            
        if self in self.game.bullets:
            self.game.bullets.remove(self)
            
    def check_collisions(self):
        """Check for collisions with asteroids."""
        for entity in self.game.entity_manager.entities[:]:  # Copy list to allow removal
            if isinstance(entity, Asteroid):
                if self._check_collision(entity):
                    self._handle_collision(entity)
                    break
                    
    def _handle_collision(self, asteroid):
        """Handle collision with an asteroid."""
        # Create explosion effect
        transform = asteroid.get_component(TransformComponent)
        if transform:
            self.game.create_explosion(transform.position, asteroid.size)
            
        # Split asteroid into pieces
        pieces = asteroid.split()
        for piece in pieces:
            self.game.entity_manager.add_entity(piece)
            
        # Remove asteroid and bullet
        if entity in self.game.entity_manager.entities:
            self.game.entity_manager.remove_entity(entity)
            
        if self in self.game.entity_manager.entities:
            self.game.entity_manager.remove_entity(self) 