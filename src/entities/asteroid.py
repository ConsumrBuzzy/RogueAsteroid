"""Asteroid entity module."""
import random
import math
from typing import Optional, Dict, Any, List, Tuple
import pygame
from pygame import Vector2

from src.core.entities.base import Entity
from src.core.components import (
    TransformComponent,
    PhysicsComponent,
    RenderComponent,
    CollisionComponent,
    ScreenWrapComponent,
    ScoreComponent,
    AudioComponent,
    EffectComponent
)
from src.core.constants import (
    SCREEN_WIDTH,
    SCREEN_HEIGHT,
    ASTEROID_SPEED_MIN,
    ASTEROID_SPEED_MAX,
    ASTEROID_ROTATION_MIN,
    ASTEROID_ROTATION_MAX,
    ASTEROID_LARGE_SIZE,
    ASTEROID_MEDIUM_SIZE,
    ASTEROID_SMALL_SIZE,
    ASTEROID_LARGE_POINTS,
    ASTEROID_MEDIUM_POINTS,
    ASTEROID_SMALL_POINTS
)

class Asteroid(Entity):
    """Asteroid entity class."""

    def __init__(self, size: str = "large", position: Optional[Vector2] = None, ship_pos: Optional[Vector2] = None) -> None:
        """Initialize the asteroid.
        
        Args:
            size: Size of the asteroid ("large", "medium", or "small")
            position: Optional position to spawn at. If None, spawns at random position.
            ship_pos: Optional ship position to avoid spawning too close.
        """
        super().__init__()
        self.size = size
        self._init_components(position, ship_pos)

    def _init_components(self, position: Optional[Vector2], ship_pos: Optional[Vector2]) -> None:
        """Initialize the asteroid's components."""
        # Transform component
        transform = self.add_component(TransformComponent)
        
        # Set position based on parameters
        if position is not None:
            transform.position = position
        elif ship_pos is not None:
            # Spawn at a random angle and distance from the ship
            angle = random.uniform(0, 2 * math.pi)
            distance = random.uniform(100, 300)  # Adjust these values as needed
            
            # Calculate spawn position
            spawn_x = (ship_pos.x + math.cos(angle) * distance) % SCREEN_WIDTH
            spawn_y = (ship_pos.y + math.sin(angle) * distance) % SCREEN_HEIGHT
            transform.position = Vector2(spawn_x, spawn_y)
        else:
            # Random position
            transform.position = Vector2(
                random.randint(0, SCREEN_WIDTH),
                random.randint(0, SCREEN_HEIGHT)
            )

        # Set size-based properties
        if self.size == "large":
            size = ASTEROID_LARGE_SIZE
            points = ASTEROID_LARGE_POINTS
        elif self.size == "medium":
            size = ASTEROID_MEDIUM_SIZE
            points = ASTEROID_MEDIUM_POINTS
        else:  # small
            size = ASTEROID_SMALL_SIZE
            points = ASTEROID_SMALL_POINTS

        # Random rotation and velocity
        transform.rotation = random.uniform(0, 360)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(ASTEROID_SPEED_MIN, ASTEROID_SPEED_MAX)
        transform.velocity = Vector2(
            math.cos(angle) * speed,
            math.sin(angle) * speed
        )

        # Render component
        render = self.add_component(RenderComponent)
        render.radius = size
        render.points = points

        # Physics component
        physics = self.add_component(PhysicsComponent)
        physics.rotation_speed = random.uniform(ASTEROID_ROTATION_MIN, ASTEROID_ROTATION_MAX)

        # Collision component
        collision = self.add_component(CollisionComponent)
        collision.radius = size

        # Screen wrap component
        screen_wrap = self.add_component(ScreenWrapComponent)
        screen_wrap.width = SCREEN_WIDTH
        screen_wrap.height = SCREEN_HEIGHT

        print(f"Asteroid components initialized: transform={transform}, render={render}, collision={collision}, screen_wrap={screen_wrap}")  # Debug info

    def split(self) -> list['Asteroid']:
        """Split the asteroid into smaller pieces.
        
        Returns:
            A list of new smaller asteroids.
        """
        if self.size == "small":
            return []
            
        new_size = "medium" if self.size == "large" else "small"
        transform = self.get_component(TransformComponent)
        
        # Create 2-3 smaller asteroids
        num_pieces = random.randint(2, 3)
        new_asteroids = []
        
        for _ in range(num_pieces):
            # Create new asteroid at current position
            new_asteroid = Asteroid(size=new_size, position=transform.position.copy())
            new_asteroids.append(new_asteroid)
            
        return new_asteroids 