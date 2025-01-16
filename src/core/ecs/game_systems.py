"""
Game-specific systems for the ECS architecture.
"""

import math
import random
import pygame
from typing import List, Tuple, Optional
from .components import (
    Position, Velocity, Input, Renderable, Collider,
    Physics, Player, Bullet, Asteroid, Particle, Sound
)
from .resources import WindowInfo, GameState
from .events import CollisionEvent, ScoreEvent
from .systems import System
from src.core.constants import (
    SHIP_ACCELERATION, SHIP_MAX_SPEED, SHIP_ROTATION_SPEED,
    BULLET_SPEED, BULLET_LIFETIME,
    ASTEROID_RADIUS, ASTEROID_SPEED, ASTEROID_POINTS,
    PARTICLE_COLORS, EXPLOSION_PARTICLE_COUNT, EXPLOSION_PARTICLE_LIFETIME
)

class PlayerControlSystem(System):
    """Handles player ship control."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update player based on input."""
        for entity, (pos, vel, input_comp, physics, player) in world.get_components(
            Position, Velocity, Input, Physics, Player
        ):
            # Handle rotation
            if input_comp.left:
                pos.rotation += SHIP_ROTATION_SPEED * dt
            if input_comp.right:
                pos.rotation -= SHIP_ROTATION_SPEED * dt
            
            # Handle thrust
            if input_comp.up:
                # Calculate thrust vector
                angle = math.radians(pos.rotation)
                thrust_x = math.cos(angle) * SHIP_ACCELERATION
                thrust_y = -math.sin(angle) * SHIP_ACCELERATION
                
                # Apply thrust
                vel.x += thrust_x * dt
                vel.y += thrust_y * dt
                
                # Create thrust particles
                self._create_thrust_particles(world, pos)
            
            # Handle shooting
            if input_comp.fire and player.shoot_cooldown <= 0:
                self._create_bullet(world, pos)
                player.shoot_cooldown = player.max_shoot_cooldown
            
            # Update cooldown
            if player.shoot_cooldown > 0:
                player.shoot_cooldown -= dt
            
            # Update invulnerability
            if player.invulnerable:
                player.invulnerable_timer -= dt
                if player.invulnerable_timer <= 0:
                    player.invulnerable = False
    
    def _create_bullet(self, world: 'World', player_pos: Position) -> None:
        """Create a bullet entity."""
        bullet = world.create_entity()
        
        # Calculate bullet direction and position
        angle = math.radians(player_pos.rotation)
        direction = pygame.Vector2(math.cos(angle), -math.sin(angle))
        
        # Add components
        world.add_component(bullet, Position(
            x=player_pos.x + direction.x * 20,
            y=player_pos.y + direction.y * 20,
            rotation=player_pos.rotation
        ))
        
        world.add_component(bullet, Velocity(
            x=direction.x * BULLET_SPEED,
            y=direction.y * BULLET_SPEED
        ))
        
        world.add_component(bullet, Bullet(lifetime=BULLET_LIFETIME))
        world.add_component(bullet, Collider(radius=2))
        world.add_component(bullet, Renderable(
            sprite_name="bullet",
            color=(255, 255, 0),
            layer=3  # Bullet layer
        ))
    
    def _create_thrust_particles(self, world: 'World', pos: Position) -> None:
        """Create thrust particle effects."""
        angle = math.radians(pos.rotation)
        base_direction = pygame.Vector2(-math.cos(angle), math.sin(angle))
        
        for _ in range(2):
            particle = world.create_entity()
            
            # Randomize direction slightly
            spread = math.radians(random.uniform(-15, 15))
            direction = pygame.Vector2(
                base_direction.x * math.cos(spread) - base_direction.y * math.sin(spread),
                base_direction.x * math.sin(spread) + base_direction.y * math.cos(spread)
            )
            
            # Add components
            world.add_component(particle, Position(
                x=pos.x - direction.x * 20,
                y=pos.y - direction.y * 20
            ))
            
            world.add_component(particle, Velocity(
                x=direction.x * random.uniform(50, 150),
                y=direction.y * random.uniform(50, 150)
            ))
            
            world.add_component(particle, Particle(
                lifetime=random.uniform(0.2, 0.4),
                fade=True,
                shrink=True
            ))
            
            world.add_component(particle, Renderable(
                color=(200, 200, 200),
                size=random.uniform(1, 2),
                layer=1  # Particle layer
            ))

class BulletSystem(System):
    """Handles bullet behavior."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update bullets."""
        for entity, (bullet,) in world.get_components(Bullet):
            # Update lifetime
            bullet.lifetime -= dt
            if bullet.lifetime <= 0:
                world.destroy_entity(entity)

class AsteroidSystem(System):
    """Handles asteroid behavior."""
    
    def update(self, world: 'World', dt: float) -> None:
        """Update asteroids and spawn new ones."""
        # Count existing asteroids
        asteroid_count = sum(1 for _ in world.get_components(Asteroid))
        
        # Spawn new asteroids if needed
        window = world.resources.get(WindowInfo)
        if window and asteroid_count < 4:
            self._create_asteroid(world, "large", window)
    
    def _create_asteroid(self, world: 'World', size: str, window: WindowInfo) -> None:
        """Create an asteroid entity."""
        asteroid = world.create_entity()
        
        # Random position at screen edge
        if random.random() < 0.5:
            x = 0 if random.random() < 0.5 else window.width
            y = random.uniform(0, window.height)
        else:
            x = random.uniform(0, window.width)
            y = 0 if random.random() < 0.5 else window.height
        
        # Random velocity
        speed_range = ASTEROID_SPEED[size]
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(*speed_range)
        
        # Add components
        world.add_component(asteroid, Position(x=x, y=y))
        world.add_component(asteroid, Velocity(
            x=math.cos(angle) * speed,
            y=math.sin(angle) * speed,
            rotation=random.uniform(-45, 45)  # Random rotation
        ))
        
        world.add_component(asteroid, Asteroid(
            size=size,
            points=ASTEROID_POINTS[size]
        ))
        
        world.add_component(asteroid, Collider(
            radius=ASTEROID_RADIUS[size]
        ))
        
        variant = random.randint(1, 3)
        world.add_component(asteroid, Renderable(
            sprite_name=f"asteroid_{size}_{variant}",
            layer=2  # Asteroid layer
        ))

class CollisionHandlingSystem(System):
    """Handles collision responses."""
    
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
        bullet = entity1 if world.has_component(entity1, Bullet) else entity2
        asteroid = entity2 if world.has_component(entity2, Asteroid) else entity1
        
        # Get components
        asteroid_comp = world.get_component(asteroid, Asteroid)
        asteroid_pos = world.get_component(asteroid, Position)
        if not asteroid_comp or not asteroid_pos:
            return
        
        # Award points
        world.events.emit(ScoreEvent(asteroid_comp.points))
        
        # Create explosion particles
        self._create_explosion(world, asteroid_pos)
        
        # Split asteroid if not smallest
        if asteroid_comp.size != "small":
            self._split_asteroid(world, asteroid)
        
        # Destroy entities
        world.destroy_entity(bullet)
        world.destroy_entity(asteroid)
    
    def _handle_player_asteroid_collision(self, world: 'World', entity1: int, entity2: int) -> None:
        """Handle collision between player and asteroid."""
        player = entity1 if world.has_component(entity1, Player) else entity2
        asteroid = entity2 if world.has_component(entity2, Asteroid) else entity1
        
        # Get player component
        player_comp = world.get_component(player, Player)
        if not player_comp or player_comp.invulnerable:
            return
        
        # Get asteroid position for explosion
        asteroid_pos = world.get_component(asteroid, Position)
        if asteroid_pos:
            self._create_explosion(world, asteroid_pos)
        
        # Reduce player lives and make temporarily invulnerable
        player_comp.lives -= 1
        player_comp.invulnerable = True
        player_comp.invulnerable_timer = 3.0
        
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
        
        # Create new asteroids
        for _ in range(2):
            angle = random.uniform(0, 2 * math.pi)
            speed_range = ASTEROID_SPEED[new_size]
            speed = random.uniform(*speed_range)
            
            new_asteroid = world.create_entity()
            world.add_component(new_asteroid, Position(x=pos.x, y=pos.y))
            world.add_component(new_asteroid, Velocity(
                x=math.cos(angle) * speed,
                y=math.sin(angle) * speed,
                rotation=random.uniform(-45, 45)
            ))
            
            world.add_component(new_asteroid, Asteroid(
                size=new_size,
                points=ASTEROID_POINTS[new_size]
            ))
            
            world.add_component(new_asteroid, Collider(
                radius=ASTEROID_RADIUS[new_size]
            ))
            
            variant = random.randint(1, 3)
            world.add_component(new_asteroid, Renderable(
                sprite_name=f"asteroid_{new_size}_{variant}",
                layer=2
            ))
    
    def _create_explosion(self, world: 'World', pos: Position) -> None:
        """Create explosion particle effects."""
        for _ in range(EXPLOSION_PARTICLE_COUNT):
            particle = world.create_entity()
            
            # Random direction and speed
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(100, 200)
            
            # Add components
            world.add_component(particle, Position(x=pos.x, y=pos.y))
            world.add_component(particle, Velocity(
                x=math.cos(angle) * speed,
                y=math.sin(angle) * speed
            ))
            
            world.add_component(particle, Particle(
                lifetime=random.uniform(0.5, EXPLOSION_PARTICLE_LIFETIME),
                fade=True,
                shrink=True
            ))
            
            world.add_component(particle, Renderable(
                color=random.choice(PARTICLE_COLORS),
                size=random.uniform(2, 4),
                layer=1
            ))
