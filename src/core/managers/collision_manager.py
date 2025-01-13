"""Handles all collision detection and resolution."""
import pygame
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.core.entities.components import (
    CollisionComponent,
    TransformComponent,
    PhysicsComponent
)
from src.core.constants.asteroids import ASTEROID_SIZES
from src.core.logging import get_logger

class CollisionManager:
    def __init__(self, game):
        """Initialize the collision manager.
        
        Args:
            game: Reference to the main game instance
        """
        self.game = game
        self.logger = get_logger()

    def handle_collisions(self):
        """Handle collisions between entities."""
        # Get all entities with collision components
        collidable_entities = [
            entity for entity in self.game.entity_manager.entities 
            if entity.get_component(CollisionComponent)
        ]
        
        # Check each pair of entities
        for i, entity1 in enumerate(collidable_entities):
            for entity2 in collidable_entities[i + 1:]:
                if self._check_collision(entity1, entity2):
                    self._handle_collision(entity1, entity2)

    def _check_collision(self, entity1, entity2) -> bool:
        """Check if two entities are colliding.
        
        Returns:
            bool: True if entities are colliding, False otherwise
        """
        collision1 = entity1.get_component(CollisionComponent)
        collision2 = entity2.get_component(CollisionComponent)
        transform1 = entity1.get_component(TransformComponent)
        transform2 = entity2.get_component(TransformComponent)
        
        if not (collision1 and collision2 and transform1 and transform2):
            return False
            
        # Get positions and calculate distance
        pos1 = pygame.Vector2(transform1.position)
        pos2 = pygame.Vector2(transform2.position)
        distance = pos1.distance_to(pos2)
        combined_radius = collision1.radius + collision2.radius
        
        return distance < combined_radius

    def _handle_collision(self, entity1, entity2):
        """Handle collision between two entities."""
        # Handle collision based on entity types
        if isinstance(entity1, Ship) and isinstance(entity2, Asteroid):
            self._handle_ship_asteroid_collision(entity1, entity2)
        elif isinstance(entity1, Asteroid) and isinstance(entity2, Ship):
            self._handle_ship_asteroid_collision(entity2, entity1)
        elif isinstance(entity1, Bullet) and isinstance(entity2, Asteroid):
            self._handle_bullet_asteroid_collision(entity1, entity2)
        elif isinstance(entity1, Asteroid) and isinstance(entity2, Bullet):
            self._handle_bullet_asteroid_collision(entity2, entity1)
        elif isinstance(entity1, Asteroid) and isinstance(entity2, Asteroid):
            self._handle_asteroid_asteroid_collision(entity1, entity2)

    def _handle_ship_asteroid_collision(self, ship: Ship, asteroid: Asteroid):
        """Handle collision between ship and asteroid."""
        if not ship.invulnerable:
            self.logger.info("Ship hit by asteroid")
            # Create explosion before losing life
            transform = ship.get_component(TransformComponent)
            if transform:
                self.game.create_explosion(transform.position, 'medium')
            self.game.lose_life()

    def _handle_bullet_asteroid_collision(self, bullet: Bullet, asteroid: Asteroid):
        """Handle collision between bullet and asteroid."""
        self.logger.debug(f"Bullet hit asteroid size {asteroid.size}")
        
        # Award points based on asteroid size
        points = {'large': 3, 'medium': 2, 'small': 1}
        self.game.scoring.add_points(points[asteroid.size])
        self.logger.debug(f"Hit asteroid size {asteroid.size}, awarded {points[asteroid.size]} points")
        
        # Create explosion effect
        transform = asteroid.get_component(TransformComponent)
        if transform:
            self.game.create_explosion(transform.position, asteroid.size)
        
        # Split asteroid
        pieces = asteroid.split()
        
        # Add new pieces to game
        for piece in pieces:
            self.game.entity_manager.add_entity(piece)
        
        # Remove bullet and asteroid
        self.game.entity_manager.remove_entity(bullet)
        self.game.entity_manager.remove_entity(asteroid)

    def _handle_asteroid_asteroid_collision(self, asteroid1: 'Asteroid', asteroid2: 'Asteroid'):
        """Handle collision between two asteroids."""
        # Get components
        transform1 = asteroid1.get_component(TransformComponent)
        transform2 = asteroid2.get_component(TransformComponent)
        physics1 = asteroid1.get_component(PhysicsComponent)
        physics2 = asteroid2.get_component(PhysicsComponent)
        
        if not all([transform1, transform2, physics1, physics2]):
            return
            
        # Get positions and velocities
        pos1 = pygame.Vector2(transform1.position)
        pos2 = pygame.Vector2(transform2.position)
        vel1 = pygame.Vector2(physics1.velocity)
        vel2 = pygame.Vector2(physics2.velocity)
        
        # Calculate collision normal and relative velocity
        normal = (pos1 - pos2)
        distance = normal.length()
        if distance == 0:  # Prevent division by zero
            normal = pygame.Vector2(1, 0)
        else:
            normal = normal / distance
            
        rel_vel = vel1 - vel2
        
        # Get masses from asteroid sizes
        mass1 = ASTEROID_SIZES[asteroid1.size]['mass']
        mass2 = ASTEROID_SIZES[asteroid2.size]['mass']
        
        # Calculate impulse
        restitution = 0.8  # Bouncy collisions
        vel_along_normal = rel_vel.dot(normal)
        
        # Only resolve if objects are moving toward each other
        if vel_along_normal > 0:
            return
            
        # Calculate impulse scalar
        j = -(1 + restitution) * vel_along_normal
        j /= (1/mass1 + 1/mass2)
        
        # Apply impulse
        impulse = normal * j
        physics1.velocity = vel1 + (impulse / mass1)
        physics2.velocity = vel2 - (impulse / mass2)
        
        # Separate the asteroids (prevent overlap)
        collision1 = asteroid1.get_component(CollisionComponent)
        collision2 = asteroid2.get_component(CollisionComponent)
        if collision1 and collision2:
            combined_radius = collision1.radius + collision2.radius
            overlap = combined_radius - distance
            if overlap > 0:
                separation = normal * (overlap * 0.5)  # Move each asteroid half the overlap
                transform1.position += separation
                transform2.position -= separation
        
        # Add some spin based on collision angle and impulse magnitude
        spin_factor = 0.1  # Reduced spin factor for more stable rotations
        tangent = pygame.Vector2(-normal.y, normal.x)
        physics1.angular_velocity += rel_vel.dot(tangent) * spin_factor
        physics2.angular_velocity -= rel_vel.dot(tangent) * spin_factor 