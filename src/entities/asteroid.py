"""Asteroid entity for the game."""
import random
import math
from typing import List, Tuple, Union, Optional
import pygame
from src.core.entities.base import Entity
from src.core.entities.components import (
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    PhysicsComponent,
    ScreenWrapComponent
)
from src.core.constants import (
    WINDOW_WIDTH, 
    WINDOW_HEIGHT, 
    WHITE,
    ASTEROID_SIZES
)
from src.entities.particle import Particle

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
        transform = self.add_component(TransformComponent)
        transform.position = position
        
        # Physics component
        physics = self.add_component(PhysicsComponent)
        physics.velocity = velocity  # Set velocity in physics component
        physics.max_speed = ASTEROID_SIZES[self.size]['speed_range'][1]  # Use max speed from range
        physics.friction = 0.0     # No friction for asteroids
        physics.mass = ASTEROID_SIZES[self.size]['mass']  # Set mass based on size
        physics.angular_velocity = random.uniform(-math.pi/2, math.pi/2)  # Random initial spin

        # Render component
        render = self.add_component(RenderComponent)
        render.color = WHITE
        render.vertices = self._generate_vertices()
        render.visible = True

        # Collision component with radius based on size
        radius = ASTEROID_SIZES[self.size]['radius']
        collision = self.add_component(CollisionComponent, radius=radius)

        # Screen wrap component
        screen_wrap = self.add_component(ScreenWrapComponent)
        
        print(f"Asteroid components initialized: transform={transform}, render={render}, collision={collision}, screen_wrap={screen_wrap}")  # Debug info
    
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
        transform = self.get_component(TransformComponent)
        physics = self.get_component(PhysicsComponent)
        if not transform or not physics:
            return []
            
        # Get original velocity (ensure non-zero)
        orig_velocity = pygame.Vector2(physics.velocity)
        if orig_velocity.length_squared() < 0.0001:  # If almost zero velocity
            orig_velocity = pygame.Vector2(random.uniform(-1, 1), random.uniform(-1, 1))
        orig_speed = orig_velocity.length()
        
        # Determine new size
        if self.size == 'large':
            new_size = 'medium'
            num_pieces = 2
        elif self.size == 'medium':
            new_size = 'small'
            num_pieces = 2
        else:
            return []  # Can't split small asteroids
            
        # Create new pieces
        pieces = []
        for i in range(num_pieces):
            # Calculate new direction (perpendicular to original velocity)
            perpendicular = pygame.Vector2(-orig_velocity.y, orig_velocity.x).normalize()
            spread_dir = perpendicular if i == 0 else -perpendicular
            
            # Create new velocity vector (maintain some forward momentum plus sideways spread)
            speed_range = ASTEROID_SIZES[new_size]['speed_range']
            new_speed = random.uniform(speed_range[0], speed_range[1])
            
            # Mix original direction with perpendicular direction
            new_vel = (orig_velocity.normalize() * (orig_speed * 0.5) + 
                      spread_dir * new_speed)
            
            # Calculate offset position (move pieces apart perpendicular to velocity)
            offset_distance = ASTEROID_SIZES[new_size]['radius'] * 2  # Double the offset
            new_pos = pygame.Vector2(transform.position) + (spread_dir * offset_distance)
            
            # Create new asteroid with offset position and new velocity
            new_asteroid = Asteroid(
                self.game,
                new_size,
                new_pos,
                new_vel
            )
            pieces.append(new_asteroid)
            
        return pieces
    
    def _create_destruction_particles(self):
        """Create explosion particles when asteroid is destroyed."""
        transform = self.get_component(TransformComponent)
        if not transform:
            return
            
        # Number of particles based on size
        num_particles = 24 if self.size == 'large' else 16 if self.size == 'medium' else 12
        
        # Get current position
        pos = pygame.Vector2(transform.position)
        
        for _ in range(num_particles):
            # Create particle with orange/yellow color for explosion
            particle = Particle(
                self.game,
                lifetime=random.uniform(0.3, 0.6),
                color=(255, random.randint(165, 220), 0)
            )
            
            # Set particle position
            particle_transform = particle.get_component(TransformComponent)
            if particle_transform:
                particle_transform.position = pos.copy()
            
            # Set particle velocity
            physics = particle.get_component(PhysicsComponent)
            if physics:
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(100, 200)
                physics.velocity = pygame.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                )
            
            # Add particle to game
            self.game.entity_manager.add_entity(particle)

    def _create_split_particles(self):
        """Create particles when asteroid splits."""
        transform = self.get_component('transform')
        if not transform:
            return
            
        # Fewer particles for splits
        num_particles = 12 if self.size == 'large' else 8 if self.size == 'medium' else 6
        
        for _ in range(num_particles):
            # Create particle with random velocity
            particle = Particle(self.game)
            
            # Set particle properties
            particle_transform = particle.get_component('transform')
            if particle_transform:
                particle_transform.position = pygame.Vector2(transform.position)
                
                # Random direction and speed
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(50, 150)
                particle_transform.velocity = pygame.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                )
            
            # Add particle to game
            self.game.entity_manager.add_entity(particle)

    def update(self, dt: float):
        """Update the asteroid's state."""
        super().update(dt)
        # Add any asteroid-specific update logic here
        pass 
        pass 