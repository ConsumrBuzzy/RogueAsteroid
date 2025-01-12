"""Bullet entity fired by the player ship."""
import numpy as np
from typing import TYPE_CHECKING
from src.core.entities.base import Entity, TransformComponent, RenderComponent, CollisionComponent
from src.core.entities.components import PhysicsComponent, ScreenWrapComponent, ParticleComponent
from src.core.constants import WHITE, WINDOW_WIDTH, WINDOW_HEIGHT, ASTEROID_SIZES
from src.entities.asteroid import Asteroid
from src.entities.particle import Particle
import random
import math
import pygame

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
        # Transform component
        transform = self.add_component(TransformComponent, x=position.x, y=position.y)
        transform.velocity = direction * 1200  # Fixed bullet speed
        print(f"Bullet velocity: {transform.velocity}")  # Debug info
        
        # Physics component
        physics = self.add_component(PhysicsComponent)
        physics.max_speed = 1200  # Match bullet speed
        physics.friction = 0.0  # No friction for bullets
        
        # Render component
        render = self.add_component(RenderComponent)
        render.vertices = [(0, 0), (0, 2)]  # Simple 2-pixel line
        render.color = (255, 255, 255)  # White
        render.visible = True
        
        # Collision component
        self.add_component(CollisionComponent, radius=1.0)
        
        # Screen wrap component
        self.add_component(ScreenWrapComponent, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    
    def _create_impact_particles(self, hit_pos):
        """Create particles for bullet impact effect"""
        print(f"Creating impact particles at {hit_pos}")  # Debug info
        num_particles = random.randint(4, 6)
        for i in range(num_particles):
            # Create particle with proper initial position
            particle = Particle(
                self.game,
                lifetime=0.2,
                color=(255, 220, 50)
            )
            
            # Set initial position
            transform = particle.get_component('transform')
            if transform:
                # Convert hit_pos to proper format if needed
                if isinstance(hit_pos, pygame.Vector2):
                    transform.position = pygame.Vector2(hit_pos)
                else:
                    transform.position = pygame.Vector2(hit_pos[0], hit_pos[1])
                
                # Add random offset
                offset = pygame.Vector2(random.uniform(-2, 2), random.uniform(-2, 2))
                transform.position += offset
                print(f"Particle {i} position: {transform.position}")  # Debug info
            
            # Set velocity through physics component
            physics = particle.get_component('physics')
            if physics:
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(50, 100)
                velocity = pygame.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                )
                physics.velocity = velocity
                print(f"Particle {i} velocity: {velocity}")  # Debug info
            
            # Add to game entities
            self.game.entities.append(particle)
            print(f"Created impact particle {i}")  # Debug info
    
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
        collision = self.get_component('collision')
        if collision:
            for entity in self.game.entities[:]:  # Copy list to allow removal
                if isinstance(entity, Asteroid):
                    other_collision = entity.get_component('collision')
                    if other_collision and collision.check_collision(other_collision):
                        # Get position before removing asteroid
                        transform = entity.get_component('transform')
                        if transform:
                            hit_pos = pygame.Vector2(transform.position)
                            # Create impact particles first
                            self._create_impact_particles(hit_pos)
                            print(f"Created impact particles at {hit_pos}")  # Debug info
                        
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