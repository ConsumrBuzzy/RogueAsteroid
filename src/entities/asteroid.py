"""Asteroid entity using component system."""
import numpy as np
from typing import List, TYPE_CHECKING
from random import uniform, randint
from src.core.entities.base import Entity, TransformComponent, RenderComponent, CollisionComponent
from src.core.entities.components import (
    ScreenWrapComponent,
    PhysicsComponent
)
from src.core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WHITE
)

if TYPE_CHECKING:
    from src.core.game import Game

class AsteroidConfig:
    """Configuration for different asteroid sizes."""
    
    SIZES = {
        'large': {
            'radius': 40.0,
            'points': 20,
            'splits': 2,
            'speed_range': (50.0, 100.0),
            'vertices_range': (10, 14),
            'mass': 3.0
        },
        'medium': {
            'radius': 20.0,
            'points': 50,
            'splits': 2,
            'speed_range': (75.0, 150.0),
            'vertices_range': (8, 12),
            'mass': 2.0
        },
        'small': {
            'radius': 10.0,
            'points': 100,
            'splits': 0,
            'speed_range': (100.0, 200.0),
            'vertices_range': (6, 10),
            'mass': 1.0
        }
    }

class Asteroid(Entity):
    """Asteroid entity that can split into smaller pieces."""
    
    def __init__(self, game: 'Game', x: float, y: float, size: str = 'large', 
                 velocity: np.ndarray = None):
        super().__init__(game)
        self.size_category = size
        self.config = AsteroidConfig.SIZES[size]
        
        # Add components
        self._init_transform(x, y)
        self._init_physics(velocity)
        self._init_render()
        self._init_collision()
        self._init_screen_wrap()
    
    def _init_transform(self, x: float, y: float) -> None:
        """Initialize transform component."""
        transform = self.add_component(TransformComponent, x, y)
        transform.rotation = uniform(0, 360)  # Random initial rotation
    
    def _init_physics(self, velocity: np.ndarray = None) -> None:
        """Initialize physics component."""
        physics = self.add_component(PhysicsComponent, 
                                   mass=self.config['mass'],
                                   max_speed=self.config['speed_range'][1])
        
        # Set initial velocity
        if velocity is None:
            speed = uniform(*self.config['speed_range'])
            angle = uniform(0, 2 * np.pi)
            velocity = np.array([
                speed * np.cos(angle),
                speed * np.sin(angle)
            ])
        
        transform = self.get_component('transform')
        if transform:
            transform.velocity = velocity
            transform.rotation_speed = uniform(-90, 90)  # Random rotation speed
    
    def _init_render(self) -> None:
        """Initialize render component."""
        render = self.add_component(RenderComponent)
        render.color = WHITE
        
        # Generate random polygon shape
        num_vertices = randint(*self.config['vertices_range'])
        vertices = []
        
        for i in range(num_vertices):
            angle = (i / num_vertices) * 2 * np.pi
            # Add some randomness to the radius
            radius_variance = uniform(0.8, 1.2)
            x = np.cos(angle) * self.config['radius'] * radius_variance
            y = np.sin(angle) * self.config['radius'] * radius_variance
            vertices.append((x, y))
        
        render.vertices = vertices
    
    def _init_collision(self) -> None:
        """Initialize collision component."""
        self.add_component(CollisionComponent, radius=self.config['radius'])
    
    def _init_screen_wrap(self) -> None:
        """Initialize screen wrapping component."""
        self.add_component(ScreenWrapComponent, WINDOW_WIDTH, WINDOW_HEIGHT)
    
    def split(self) -> list['Asteroid']:
        """Split asteroid into smaller pieces."""
        new_asteroids = []
        
        # Only split if not already smallest
        if self.size_category != 'small':
            # Determine new size
            new_size = 'medium' if self.size_category == 'large' else 'small'
            
            # Create new asteroids
            for _ in range(self.config['splits']):
                # Calculate random velocity direction
                angle = np.random.uniform(0, 2 * np.pi)
                direction = np.array([np.cos(angle), np.sin(angle)])
                
                # Get random speed in range for new size
                speed = np.random.uniform(*AsteroidConfig.SIZES[new_size]['speed_range'])
                velocity = direction * speed
                
                # Create new asteroid at current position
                transform = self.get_component('transform')
                if transform:
                    new_asteroid = Asteroid(
                        self.game,
                        transform.position[0],
                        transform.position[1],
                        new_size,
                        velocity
                    )
                    new_asteroids.append(new_asteroid)
        
        # Remove self from game
        if self in self.game.asteroids:
            self.game.asteroids.remove(self)
        if self in self.game.entities:
            self.game.entities.remove(self)
        
        print(f"Split {self.size_category} asteroid into {len(new_asteroids)} {new_size} asteroids")  # Debug info
        return new_asteroids 