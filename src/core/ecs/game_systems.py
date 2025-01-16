"""
Game-specific systems for Rogue Asteroid.
"""

import math
import pygame
from typing import TYPE_CHECKING
from .system import System
from .components import Position, Velocity, Input, Collider
from .game_components import (
    Player,
    Asteroid,
    Bullet,
    Lifetime,
    Physics,
    EntityType,
    EntityTag
)
from .events import CollisionEvent, ScoreEvent
from .resources import GameState, WindowInfo

if TYPE_CHECKING:
    from .world import World

class PlayerControlSystem(System):
    """Handles player ship control and movement."""
    
    THRUST_FORCE = 200.0
    ROTATION_SPEED = 180.0  # Degrees per second
    
    def update(self, world: 'World', dt: float) -> None:
        for entity, (pos, vel, input_comp, physics) in world.get_components(
            Position, Velocity, Input, Physics
        ):
            if not world.has_component(entity, Player):
                continue
                
            # Handle rotation
            if input_comp.rotate_left:
                pos.rotation += self.ROTATION_SPEED * dt
            if input_comp.rotate_right:
                pos.rotation -= self.ROTATION_SPEED * dt
            
            # Handle thrust
            if input_comp.thrust:
                # Convert rotation to radians
                angle_rad = math.radians(pos.rotation)
                # Apply thrust force in direction of rotation
                force_x = math.cos(angle_rad) * self.THRUST_FORCE
                force_y = -math.sin(angle_rad) * self.THRUST_FORCE
                
                vel.dx += force_x * dt
                vel.dy += force_y * dt
            
            # Apply drag
            if physics.drag > 0:
                vel.dx *= (1.0 - physics.drag * dt)
                vel.dy *= (1.0 - physics.drag * dt)
            
            # Enforce speed limit
            speed = math.sqrt(vel.dx * vel.dx + vel.dy * vel.dy)
            if speed > physics.max_speed:
                vel.dx = (vel.dx / speed) * physics.max_speed
                vel.dy = (vel.dy / speed) * physics.max_speed

class BulletSystem(System):
    """Handles bullet lifetime and cleanup."""
    
    def update(self, world: 'World', dt: float) -> None:
        for entity, (lifetime,) in world.get_components(Lifetime):
            if not world.has_component(entity, Bullet):
                continue
            
            lifetime.remaining -= dt
            if lifetime.remaining <= 0:
                world.destroy_entity(entity)

class AsteroidSystem(System):
    """Handles asteroid behavior and spawning."""
    
    def update(self, world: 'World', dt: float) -> None:
        # This will be expanded with asteroid splitting logic
        pass

class CollisionHandlingSystem(System):
    """Handles collision responses between different entity types."""
    
    def update(self, world: 'World', dt: float) -> None:
        for event in world.events._pending_events:
            if not isinstance(event, CollisionEvent):
                continue
            
            self._handle_collision(world, event.entity1, event.entity2)
    
    def _handle_collision(self, world: 'World', entity1: int, entity2: int) -> None:
        # Get entity types
        tag1 = world.get_component(entity1, EntityTag)
        tag2 = world.get_component(entity2, EntityTag)
        
        if not tag1 or not tag2:
            return
        
        # Handle bullet-asteroid collision
        if (tag1.type == EntityType.BULLET and tag2.type == EntityType.ASTEROID or
            tag2.type == EntityType.BULLET and tag1.type == EntityType.ASTEROID):
            self._handle_bullet_asteroid_collision(
                world,
                entity1 if tag1.type == EntityType.ASTEROID else entity2,
                entity2 if tag2.type == EntityType.BULLET else entity1
            )
        
        # Handle player-asteroid collision
        elif (tag1.type == EntityType.PLAYER and tag2.type == EntityType.ASTEROID or
              tag2.type == EntityType.PLAYER and tag1.type == EntityType.ASTEROID):
            self._handle_player_asteroid_collision(
                world,
                entity1 if tag1.type == EntityType.PLAYER else entity2,
                entity2 if tag2.type == EntityType.ASTEROID else entity1
            )
    
    def _handle_bullet_asteroid_collision(
        self,
        world: 'World',
        asteroid_entity: int,
        bullet_entity: int
    ) -> None:
        asteroid = world.get_component(asteroid_entity, Asteroid)
        if not asteroid:
            return
        
        # Award points
        world.events.emit(ScoreEvent(points=asteroid.points, entity=asteroid_entity))
        
        # Destroy bullet
        world.destroy_entity(bullet_entity)
        
        # Handle asteroid splitting or destruction
        if asteroid.size == "large":
            self._split_asteroid(world, asteroid_entity, "medium")
        elif asteroid.size == "medium":
            self._split_asteroid(world, asteroid_entity, "small")
        
        # Destroy the original asteroid
        world.destroy_entity(asteroid_entity)
    
    def _handle_player_asteroid_collision(
        self,
        world: 'World',
        player_entity: int,
        asteroid_entity: int
    ) -> None:
        player = world.get_component(player_entity, Player)
        if not player or player.invulnerable:
            return
        
        # Reduce player lives
        player.lives -= 1
        if player.lives <= 0:
            # Game over
            game_state = world.resources.get(GameState)
            if game_state:
                game_state.paused = True
        else:
            # Make player invulnerable temporarily
            player.invulnerable = True
            player.invulnerable_timer = 3.0  # 3 seconds of invulnerability
    
    def _split_asteroid(self, world: 'World', asteroid_entity: int, new_size: str) -> None:
        pos = world.get_component(asteroid_entity, Position)
        asteroid = world.get_component(asteroid_entity, Asteroid)
        
        if not pos or not asteroid:
            return
        
        for _ in range(asteroid.split_count):
            # Create new asteroid with random velocity
            angle = pygame.random.random() * 2 * math.pi
            speed = 50.0 + pygame.random.random() * 50.0
            
            new_asteroid = world.create_entity()
            world.add_component(new_asteroid, Position(x=pos.x, y=pos.y))
            world.add_component(new_asteroid, Velocity(
                dx=math.cos(angle) * speed,
                dy=math.sin(angle) * speed
            ))
            world.add_component(new_asteroid, Asteroid(
                size=new_size,
                points=asteroid.points * 2
            ))
            world.add_component(new_asteroid, EntityTag(type=EntityType.ASTEROID))
            world.add_component(new_asteroid, Collider(
                radius=20.0 if new_size == "medium" else 10.0
            ))
