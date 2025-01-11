"""Asteroid entity for the game."""
import random
import math
from typing import List, Tuple
import pygame
from src.core.entities.base import Entity, TransformComponent, RenderComponent, CollisionComponent
from src.core.entities.components import PhysicsComponent, ScreenWrapComponent
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE

class Asteroid(Entity):
    """Asteroid entity that can be destroyed by bullets and split into smaller pieces."""
    
    # Size categories with corresponding radius and points
    SIZES = {
        'large': {'radius': 40.0, 'points': 20},
        'medium': {'radius': 20.0, 'points': 50},
        'small': {'radius': 10.0, 'points': 100}
    }
    
    def __init__(self, game, size='large', position=None, velocity=None):
        """Initialize the asteroid with the given size and optional position/velocity."""
        super().__init__(game)
        self.size = size
        self._init_components(position, velocity)
    
    @classmethod
    def spawn_random(cls, game, ship_pos: Tuple[float, float]) -> 'Asteroid':
        """Create a new asteroid at a random position away from the ship."""
        print("Creating new Asteroid")  # Debug info
        
        # Choose a random angle and distance from the ship
        angle = random.uniform(0, 2 * math.pi)
        min_distance = 100  # Minimum safe distance from ship
        max_distance = 200  # Maximum spawn distance
        distance = random.uniform(min_distance, max_distance)
        
        # Calculate spawn position
        spawn_x = (ship_pos[0] + math.cos(angle) * distance) % WINDOW_WIDTH
        spawn_y = (ship_pos[1] + math.sin(angle) * distance) % WINDOW_HEIGHT
        position = (spawn_x, spawn_y)
        
        # Random velocity
        speed = random.uniform(50, 100)
        velocity_angle = random.uniform(0, 2 * math.pi)
        velocity = (math.cos(velocity_angle) * speed, math.sin(velocity_angle) * speed)
        
        return cls(game, 'large', position, velocity)
    
    def _init_components(self, position=None, velocity=None):
        """Initialize all components for the asteroid."""
        # Default position if none provided
        if position is None:
            position = (random.uniform(0, WINDOW_WIDTH), random.uniform(0, WINDOW_HEIGHT))
            
        # Default velocity if none provided
        if velocity is None:
            speed = random.uniform(50, 100)
            angle = random.uniform(0, 2 * math.pi)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
        
        # Initialize transform
        transform = self.add_component(TransformComponent)
        transform.position = position
        transform.rotation = random.uniform(0, 360)
        
        # Initialize physics
        physics = self.add_component(PhysicsComponent)
        physics.velocity = velocity
        physics.max_speed = 200
        physics.friction = 0
        
        # Initialize render with polygon shape
        render = self.add_component(RenderComponent)
        render.color = WHITE
        render.vertices = self._generate_vertices()
        render.visible = True
        
        # Initialize collision
        collision = self.add_component(CollisionComponent)
        collision.radius = self.SIZES[self.size]['radius']
        
        # Initialize screen wrap
        self.add_component(ScreenWrapComponent)
    
    def _generate_vertices(self) -> List[Tuple[float, float]]:
        """Generate vertices for the asteroid's shape."""
        num_vertices = random.randint(8, 12)
        radius = self.SIZES[self.size]['radius']
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
        num_pieces = 2
        new_asteroids = []
        
        transform = self.get_component('transform')
        if not transform:
            return []
            
        for _ in range(num_pieces):
            # Random velocity for new pieces
            speed = random.uniform(100, 150)
            angle = random.uniform(0, 2 * math.pi)
            velocity = (math.cos(angle) * speed, math.sin(angle) * speed)
            
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