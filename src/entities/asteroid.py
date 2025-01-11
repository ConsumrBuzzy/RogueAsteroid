"""Asteroid entity for the game."""
import random
import math
from typing import List, Tuple, Union, Optional
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
    
    def __init__(self, game, size: str, position: Union[pygame.Vector2, Tuple[float, float]], velocity: Optional[pygame.Vector2] = None):
        """Initialize the asteroid."""
        super().__init__(game)
        self.size = size
        
        # Convert position tuple to Vector2 if needed
        if isinstance(position, tuple):
            position = pygame.Vector2(position[0], position[1])
        
        # Default velocity if none provided
        if velocity is None:
            min_speed, max_speed = ASTEROID_SIZES[size]['speed_range']
            speed = random.uniform(min_speed, max_speed)
            angle = random.uniform(0, 2 * math.pi)
            velocity = pygame.Vector2(
                math.cos(angle) * speed,
                math.sin(angle) * speed
            )
        
        self._init_components(position, velocity)
        print(f"Asteroid created: size={size}, pos={position}, vel={velocity}")  # Debug info
    
    @classmethod
    def spawn_random(cls, game, ship_pos: pygame.Vector2) -> 'Asteroid':
        """Create a new asteroid at a random position away from the ship."""
        print("Creating new Asteroid")  # Debug info
        
        # Choose a random angle and distance from the ship
        angle = random.uniform(0, 2 * math.pi)
        min_distance = 150  # Increased minimum safe distance
        max_distance = 250  # Increased maximum spawn distance
        distance = random.uniform(min_distance, max_distance)
        
        # Calculate spawn position
        spawn_x = (ship_pos.x + math.cos(angle) * distance) % WINDOW_WIDTH
        spawn_y = (ship_pos.y + math.sin(angle) * distance) % WINDOW_HEIGHT
        position = pygame.Vector2(spawn_x, spawn_y)
        
        # Calculate direction to ship
        to_ship = pygame.Vector2(
            ship_pos.x - spawn_x,
            ship_pos.y - spawn_y
        ).normalize()
        
        # Generate velocity angle that's not toward the ship
        # Calculate forbidden angle range (toward ship ±45 degrees)
        ship_angle = math.atan2(to_ship.y, to_ship.x)
        min_allowed = ship_angle + math.pi/4  # +45 degrees
        max_allowed = ship_angle + 7*math.pi/4  # +315 degrees
        
        # Choose a random angle outside the forbidden range
        velocity_angle = random.uniform(min_allowed, max_allowed)
        speed = random.uniform(50, 100)
        
        velocity = pygame.Vector2(
            math.cos(velocity_angle) * speed,
            math.sin(velocity_angle) * speed
        )
        
        print(f"Spawning asteroid at {position} with velocity {velocity}")  # Debug info
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
    
    def split(self):
        """Split asteroid into smaller pieces."""
        if self.size == 'small':
            return []
            
        # Get current properties
        transform = self.get_component('transform')
        if not transform:
            return []
            
        # Determine new size
        new_size = 'medium' if self.size == 'large' else 'small'
        
        # Create split pieces with near-opposite velocities
        pieces = []
        # For small pieces, use exact opposite directions with slight variation
        if new_size == 'small':
            base_angles = [0, 180]  # Opposite directions
            speed_multiplier = 2.0  # Double speed for small pieces
            angle_variation = 10  # Less variation for small pieces
            offset_distance = 15  # Smaller offset for small pieces
        else:
            base_angles = [-150, 150]  # Wide but not exactly opposite for medium pieces
            speed_multiplier = 1.5  # 50% faster for medium pieces
            angle_variation = 20  # More variation for medium pieces
            offset_distance = 25  # Larger offset for medium pieces
        
        # Get original velocity angle
        orig_angle = math.degrees(math.atan2(transform.velocity.y, transform.velocity.x))
        
        for base_angle in base_angles:
            # Add controlled randomness to the split angle
            angle = orig_angle + base_angle + random.uniform(-angle_variation, angle_variation)
            angle_rad = math.radians(angle)
            
            # Calculate new velocity with size-based speed scaling
            min_speed, max_speed = ASTEROID_SIZES[new_size]['speed_range']
            base_speed = random.uniform(min_speed, max_speed)
            new_speed = base_speed * speed_multiplier
            
            # Create velocity vector at the split angle
            new_velocity = pygame.Vector2(
                math.cos(angle_rad) * new_speed,
                math.sin(angle_rad) * new_speed
            )
            
            # Offset the spawn position in the direction of travel
            spawn_pos = pygame.Vector2(transform.position)
            spawn_pos += pygame.Vector2(
                math.cos(angle_rad) * offset_distance,
                math.sin(angle_rad) * offset_distance
            )
            
            # Create new asteroid with offset position and calculated velocity
            piece = Asteroid(self.game, new_size, spawn_pos, new_velocity)
            pieces.append(piece)
            
            print(f"Created split piece: size={new_size}, angle={angle} (base={base_angle}), speed={new_speed}, offset={offset_distance}")  # Debug info
        
        return pieces

    def update(self, dt: float):
        """Update the asteroid's state."""
        super().update(dt)
        # Add any asteroid-specific update logic here
        pass 