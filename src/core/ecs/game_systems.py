"""
Game-specific systems for the ECS architecture.
"""

import math
import random
import pygame
from typing import TYPE_CHECKING, List, Tuple
from .components import (
    Position, Velocity, Input, Renderable, Collider,
    Physics, Player, Bullet, Asteroid, Particle
)
from .resources import WindowInfo, SpriteResource
from .events import CollisionEvent, ScoreEvent

if TYPE_CHECKING:
    from .world import World

class PlayerControlSystem:
    """Handles player input and control."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update player based on input."""
        for entity, (pos, vel, input_comp, physics) in world.get_components(Position, Velocity, Input, Physics):
            if not world.has_component(entity, Player):
                continue
            
            # Handle rotation
            if input_comp.left:
                pos.rotation += 360 * dt  # Rotate counterclockwise
            if input_comp.right:
                pos.rotation -= 360 * dt  # Rotate clockwise
            
            # Handle thrust
            if input_comp.up:
                # Calculate thrust vector based on rotation
                angle = math.radians(pos.rotation)
                thrust_x = math.cos(angle) * physics.thrust
                thrust_y = -math.sin(angle) * physics.thrust
                
                # Apply thrust
                vel.x += thrust_x * dt
                vel.y += thrust_y * dt
                
                # Limit speed
                speed = math.sqrt(vel.x * vel.x + vel.y * vel.y)
                if speed > physics.max_speed:
                    vel.x = (vel.x / speed) * physics.max_speed
                    vel.y = (vel.y / speed) * physics.max_speed
            
            # Apply friction
            if physics.friction > 0:
                vel.x *= (1.0 - physics.friction * dt)
                vel.y *= (1.0 - physics.friction * dt)
            
            # Handle shooting
            player = world.get_component(entity, Player)
            if input_comp.fire and player.shoot_cooldown <= 0:
                self._spawn_bullet(world, entity)
                player.shoot_cooldown = 0.2  # Reset cooldown
            
            # Update cooldown
            if player.shoot_cooldown > 0:
                player.shoot_cooldown -= dt
    
    def _spawn_bullet(self, world: 'World', player_entity: int) -> None:
        """Spawn a bullet from the player's position."""
        pos = world.get_component(player_entity, Position)
        if not pos:
            return
        
        # Create bullet entity
        bullet_entity = world.create_entity()
        
        # Calculate bullet direction and position
        angle = math.radians(pos.rotation)
        direction = pygame.Vector2(math.cos(angle), -math.sin(angle))
        
        # Add components
        world.add_component(bullet_entity, Position(
            x=pos.x + direction.x * 20,  # Offset from player
            y=pos.y + direction.y * 20,
            rotation=pos.rotation
        ))
        
        world.add_component(bullet_entity, Velocity(
            x=direction.x * 800,  # Bullet speed
            y=direction.y * 800
        ))
        
        world.add_component(bullet_entity, Bullet())
        world.add_component(bullet_entity, Collider(radius=2))
        
        # Add renderable with bullet shape
        render = Renderable(
            sprite_name="bullet",
            color=(255, 255, 0),  # Yellow
            line_width=2
        )
        world.add_component(bullet_entity, render)

class BulletSystem:
    """Handles bullet behavior and lifetime."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update all bullets."""
        for entity, (bullet,) in world.get_components(Bullet):
            # Update lifetime
            bullet.lifetime -= dt
            
            # Destroy if expired
            if bullet.lifetime <= 0:
                world.destroy_entity(entity)

class AsteroidSystem:
    """Handles asteroid behavior and spawning."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update all asteroids."""
        # Count existing asteroids
        asteroid_count = sum(1 for _ in world.get_components(Asteroid))
        
        # Spawn new asteroids if needed
        if asteroid_count < 4:
            self._spawn_asteroid(world, "large")
    
    def _spawn_asteroid(self, world: 'World', size: str) -> None:
        """Spawn a new asteroid."""
        window = world.resources.get(WindowInfo)
        if not window:
            return
        
        # Create asteroid entity
        asteroid_entity = world.create_entity()
        
        # Randomize position at screen edge
        if random.random() < 0.5:
            # Spawn on left/right edge
            x = 0 if random.random() < 0.5 else window.width
            y = random.uniform(0, window.height)
        else:
            # Spawn on top/bottom edge
            x = random.uniform(0, window.width)
            y = 0 if random.random() < 0.5 else window.height
        
        # Random velocity
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(50, 100)
        vel_x = math.cos(angle) * speed
        vel_y = math.sin(angle) * speed
        
        # Add components
        world.add_component(asteroid_entity, Position(x=x, y=y))
        world.add_component(asteroid_entity, Velocity(x=vel_x, y=vel_y))
        world.add_component(asteroid_entity, Asteroid(size=size))
        
        # Size-based properties
        if size == "large":
            radius = 40
            points = 20
        elif size == "medium":
            radius = 20
            points = 50
        else:  # small
            radius = 10
            points = 100
        
        world.add_component(asteroid_entity, Collider(radius=radius))
        
        # Add renderable with asteroid shape
        variant = random.randint(1, 3)
        render = Renderable(
            sprite_name=f"asteroid_{size}_{variant}",
            color=(255, 255, 255),  # White
            line_width=2
        )
        world.add_component(asteroid_entity, render)

class CollisionHandlingSystem:
    """Handles collision responses between entities."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Process collision events."""
        for event in world.events.get(CollisionEvent):
            entity1, entity2 = event.entity1, event.entity2
            
            # Handle bullet-asteroid collisions
            if (world.has_component(entity1, Bullet) and world.has_component(entity2, Asteroid) or
                world.has_component(entity2, Bullet) and world.has_component(entity1, Asteroid)):
                self._handle_bullet_asteroid_collision(world, entity1, entity2)
            
            # Handle player-asteroid collisions
            elif (world.has_component(entity1, Player) and world.has_component(entity2, Asteroid) or
                  world.has_component(entity2, Player) and world.has_component(entity1, Asteroid)):
                self._handle_player_asteroid_collision(world, entity1, entity2)
    
    def _handle_bullet_asteroid_collision(self, world: 'World', entity1: int, entity2: int) -> None:
        """Handle collision between bullet and asteroid."""
        # Determine which is which
        bullet = entity1 if world.has_component(entity1, Bullet) else entity2
        asteroid = entity2 if world.has_component(entity2, Asteroid) else entity1
        
        # Get asteroid info
        asteroid_comp = world.get_component(asteroid, Asteroid)
        if not asteroid_comp:
            return
        
        # Award points
        world.events.emit(ScoreEvent(asteroid_comp.points))
        
        # Split asteroid if not smallest
        if asteroid_comp.size != "small":
            self._split_asteroid(world, asteroid)
        
        # Destroy both entities
        world.destroy_entity(bullet)
        world.destroy_entity(asteroid)
    
    def _handle_player_asteroid_collision(self, world: 'World', entity1: int, entity2: int) -> None:
        """Handle collision between player and asteroid."""
        # Determine which is which
        player = entity1 if world.has_component(entity1, Player) else entity2
        asteroid = entity2 if world.has_component(entity2, Asteroid) else entity1
        
        # Get player component
        player_comp = world.get_component(player, Player)
        if not player_comp or player_comp.invulnerable:
            return
        
        # Reduce player lives and make temporarily invulnerable
        player_comp.lives -= 1
        player_comp.invulnerable = True
        player_comp.invulnerable_timer = 3.0  # 3 seconds of invulnerability
        
        # Destroy asteroid
        world.destroy_entity(asteroid)
    
    def _split_asteroid(self, world: 'World', asteroid: int) -> None:
        """Split an asteroid into smaller pieces."""
        pos = world.get_component(asteroid, Position)
        asteroid_comp = world.get_component(asteroid, Asteroid)
        if not pos or not asteroid_comp:
            return
        
        # Determine new size
        new_size = "medium" if asteroid_comp.size == "large" else "small"
        
        # Create two new asteroids
        for _ in range(2):
            # Random direction
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 150)
            vel_x = math.cos(angle) * speed
            vel_y = math.sin(angle) * speed
            
            # Spawn new asteroid
            self._spawn_asteroid(world, new_size)
            # Set position and velocity
            new_asteroid = world.create_entity()
            world.add_component(new_asteroid, Position(x=pos.x, y=pos.y))
            world.add_component(new_asteroid, Velocity(x=vel_x, y=vel_y))
            world.add_component(new_asteroid, Asteroid(size=new_size))
