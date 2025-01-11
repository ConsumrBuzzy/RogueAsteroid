"""Asteroid entity for the game."""
import random
import math
from typing import List, Tuple
import pygame
from src.core.entities.base import Entity, TransformComponent, RenderComponent, CollisionComponent
from src.core.entities.components import PhysicsComponent, ScreenWrapComponent
from src.core.constants import (
    WINDOW_WIDTH, 
    WINDOW_HEIGHT, 
    WHITE,
    ASTEROID_SIZES
)

class Asteroid(Entity):
    """Asteroid entity that can be destroyed by bullets and split into smaller pieces."""
    
    def __init__(self, game, size='large', position=None, velocity=None):
        """Initialize the asteroid with the given size and optional position/velocity."""
        super().__init__(game)
        self.size = size
        if position is None:
            position = pygame.Vector2(WINDOW_WIDTH / 2, WINDOW_HEIGHT / 2)
        if velocity is None:
            velocity = pygame.Vector2(0, 0)
        self._init_components(position, velocity)
    
    @classmethod
    def spawn_random(cls, game, ship_pos: pygame.Vector2) -> 'Asteroid':
        """Create a new asteroid at a random position away from the ship."""
        print("Creating new Asteroid")  # Debug info
        
        # Choose a random angle and distance from the ship
        angle = random.uniform(0, 2 * math.pi)
        min_distance = 100  # Minimum safe distance from ship
        max_distance = 200  # Maximum spawn distance
        distance = random.uniform(min_distance, max_distance)
        
        # Calculate spawn position
        spawn_x = (ship_pos.x + math.cos(angle) * distance) % WINDOW_WIDTH
        spawn_y = (ship_pos.y + math.sin(angle) * distance) % WINDOW_HEIGHT
        position = pygame.Vector2(spawn_x, spawn_y)
        
        # Random velocity
        speed = random.uniform(50, 100)
        velocity_angle = random.uniform(0, 2 * math.pi)
        velocity = pygame.Vector2(
            math.cos(velocity_angle) * speed,
            math.sin(velocity_angle) * speed
        )
        
        return cls(game, 'large', position, velocity)
    
    def _init_components(self, position: pygame.Vector2, velocity: pygame.Vector2):
        """Initialize asteroid components."""
        # Transform component
        transform = self.add_component(TransformComponent, x=position.x, y=position.y)
        transform.velocity = velocity

        # Render component
        render = self.add_component(RenderComponent)
        render.color = WHITE
        render.vertices = self._generate_vertices()
        render.visible = True

        # Physics component
        physics = self.add_component(PhysicsComponent)
        physics.max_speed = ASTEROID_SIZES[self.size]['speed_range'][1]  # Use max speed from range
        physics.friction = 0.0     # No friction for asteroids

        # Collision component with radius based on size
        radius = ASTEROID_SIZES[self.size]['radius']
        collision = self.add_component(CollisionComponent, radius=radius)

        # Screen wrap component
        self.add_component(ScreenWrapComponent, width=WINDOW_WIDTH, height=WINDOW_HEIGHT)
    
    def _generate_vertices(self) -> List[Tuple[float, float]]:
        """Generate vertices for the asteroid's shape."""
        min_vertices, max_vertices = ASTEROID_SIZES[self.size]['vertices_range']
        num_vertices = random.randint(min_vertices, max_vertices)
        radius = ASTEROID_SIZES[self.size]['radius']
        vertices = []
        
        for i in range(num_vertices):
            angle = (i / num_vertices) * 2 * math.pi
            # Add some randomness to the radius
            vertex_radius = radius * random.uniform(0.8, 1.2)
            x = math.cos(angle) * vertex_radius
            y = math.sin(angle) * vertex_radius
            vertices.append((x, y))
        
        return vertices
    
    def split(self) -> List['Asteroid']:
        """Split the asteroid into smaller pieces."""
        if self.size == 'small':
            return []
            
        new_size = 'medium' if self.size == 'large' else 'small'
        num_pieces = ASTEROID_SIZES[self.size]['splits']
        new_asteroids = []
        
        transform = self.get_component('transform')
        if not transform:
            return []
            
        for _ in range(num_pieces):
            # Random velocity for new pieces
            min_speed, max_speed = ASTEROID_SIZES[new_size]['speed_range']
            speed = random.uniform(min_speed, max_speed)
            angle = random.uniform(0, 2 * math.pi)
            velocity = pygame.Vector2(
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
            
            # Create new asteroid
            new_asteroid = Asteroid(self.game, new_size, transform.position, velocity)
            new_asteroids.append(new_asteroid)
        
        print(f"Split asteroid into {len(new_asteroids)} pieces")  # Debug info
        return new_asteroids

    def update(self, dt: float):
        """Update the asteroid's state."""
        super().update(dt)
        # Add any asteroid-specific update logic here
        pass 