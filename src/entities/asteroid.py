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
from src.entities.particle import Particle

class Asteroid(Entity):
    """Asteroid entity that can be destroyed by bullets and split into smaller pieces."""
    
    def __init__(self, game, size: str, position: Union[pygame.Vector2, Tuple[float, float]], velocity: Optional[pygame.Vector2] = None):
        """Initialize the asteroid."""
        super().__init__(game)
        self.size = size
        self.is_destroyed = False  # Track if asteroid is destroyed
        
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
        
        # Generate velocity that's not directly toward or away from ship
        velocity_angle = random.uniform(0, 2 * math.pi)  # Any direction
        min_speed = ASTEROID_SIZES['large']['speed_range'][0]
        max_speed = ASTEROID_SIZES['large']['speed_range'][1]
        speed = random.uniform(min_speed, max_speed)
        
        velocity = pygame.Vector2(
            math.cos(velocity_angle) * speed,
            math.sin(velocity_angle) * speed
        )
        
        # Ensure minimum velocity magnitude
        if velocity.length() < min_speed:
            velocity = velocity.normalize() * min_speed
            
        print(f"Spawning asteroid at {position} with velocity {velocity} (speed={velocity.length():.2f})")
        return cls(game, 'large', position, velocity)
    
    def _init_components(self, position: pygame.Vector2, velocity: pygame.Vector2):
        """Initialize asteroid components."""
        # Transform component
        transform = self.add_component(TransformComponent)
        transform.position = position
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
        screen_wrap = self.add_component(ScreenWrapComponent)
        screen_wrap.width = WINDOW_WIDTH
        screen_wrap.height = WINDOW_HEIGHT
        
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
        transform = self.get_component('transform')
        if not transform:
            return []
        
        if self.size == 'small':
            # Award points for destroying small asteroid
            self.game.scoring.add_points(100)
            # Create small explosion for final destruction
            self._create_destruction_particles()
            return []
            
        # Create split effect particles
        self._create_split_particles()
            
        # Determine new size
        new_size = 'medium' if self.size == 'large' else 'small'
        
        # Get speed range for new size
        min_speed, max_speed = ASTEROID_SIZES[new_size]['speed_range']
        
        # Create split pieces with near-opposite velocities
        pieces = []
        # For small pieces, use exact opposite directions with slight variation
        if new_size == 'small':
            base_angles = [0, 180]  # Opposite directions
            speed_multiplier = 1.5  # 50% faster for small pieces
            angle_variation = 15  # Less variation for small pieces
            offset_distance = 15  # Smaller offset for small pieces
        else:
            base_angles = [-120, 120]  # Wide but not exactly opposite for medium pieces
            speed_multiplier = 1.2  # 20% faster for medium pieces
            angle_variation = 20  # More variation for medium pieces
            offset_distance = 25  # Larger offset for medium pieces
        
        # Get original velocity angle
        orig_angle = math.degrees(math.atan2(transform.velocity.y, transform.velocity.x))
        orig_speed = transform.velocity.length()
        
        for base_angle in base_angles:
            # Add controlled randomness to the split angle
            angle = orig_angle + base_angle + random.uniform(-angle_variation, angle_variation)
            angle_rad = math.radians(angle)
            
            # Calculate new velocity with size-based speed scaling
            # Use the larger of: minimum speed for size, or original speed * multiplier
            new_speed = max(min_speed, orig_speed * speed_multiplier)
            # Cap at maximum speed for size
            new_speed = min(new_speed, max_speed)
            
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
            
            print(f"Created split piece: size={new_size}, angle={angle:.1f}° (base={base_angle}°), speed={new_speed:.1f}, pos={spawn_pos}")
        
        return pieces
    
    def destroy(self):
        """Destroy the asteroid and create particle effects."""
        if self.is_destroyed:
            return
            
        self.is_destroyed = True
        
        # Create explosion particles
        transform = self.get_component('transform')
        if transform:
            for _ in range(8):  # Create 8 particles
                # Create particle with base parameters
                particle = Particle(
                    self.game,
                    lifetime=random.uniform(0.3, 0.7),  # Random lifetime between 0.3 and 0.7 seconds
                    color=WHITE
                )
                
                # Set position and velocity through transform component
                particle_transform = particle.get_component('transform')
                if particle_transform:
                    particle_transform.position = transform.position.copy()
                    particle_transform.velocity = pygame.Vector2(
                        random.uniform(-100, 100),
                        random.uniform(-100, 100)
                    )
                
                self.game.particles.append(particle)
        
        # Split into smaller asteroids if possible
        if self.size != 'small':
            new_pieces = self.split()
            for piece in new_pieces:
                self.game.asteroids.append(piece)
            
    def _create_destruction_particles(self):
        """Create explosion particles when asteroid is destroyed."""
        transform = self.get_component('transform')
        if not transform:
            return
            
        # Number of particles based on size
        num_particles = 24 if self.size == 'large' else 16 if self.size == 'medium' else 12
        
        # Get current position as Vector2
        pos = pygame.Vector2(transform.position.x if hasattr(transform.position, 'x') 
                           else transform.position[0],
                           transform.position.y if hasattr(transform.position, 'y')
                           else transform.position[1])
        
        for _ in range(num_particles):
            # Create particle with orange/yellow color for explosion
            particle = Particle(
                self.game,
                lifetime=random.uniform(0.3, 0.6),
                color=(255, random.randint(165, 220), 0)
            )
            
            # Set particle position
            particle_transform = particle.get_component('transform')
            if particle_transform:
                particle_transform.position = pos.copy()
            
            # Set particle velocity
            physics = particle.get_component('physics')
            if physics:
                angle = random.uniform(0, 2 * math.pi)
                speed = random.uniform(100, 200)
                physics.velocity = pygame.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                )
            
            # Add particle to game
            self.game.entities.append(particle)

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
            self.game.entities.append(particle)

    def update(self, dt: float):
        """Update the asteroid's state."""
        super().update(dt)
        # Add any asteroid-specific update logic here
        pass 
        pass