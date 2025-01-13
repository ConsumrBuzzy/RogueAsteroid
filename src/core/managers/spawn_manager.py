"""Handles spawning of game entities."""
import random
import pygame
from src.entities.ship import Ship
from src.core.entities.components import (
    TransformComponent,
    PhysicsComponent,
    CollisionComponent
)
from src.core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    SHIP_INVULNERABLE_TIME
)
from src.core.logging import get_logger

class SpawnManager:
    def __init__(self, game):
        """Initialize the spawn manager.
        
        Args:
            game: Reference to the main game instance
        """
        self.game = game
        self.logger = get_logger()
        self.wave = 1
        self.asteroids_per_wave = 4
        self.spawn_timer = 0.0
        self.spawn_delay = 0.5  # seconds between asteroid spawns
        self.spawning_wave = False
        self.asteroids_to_spawn = 0

    def spawn_ship(self, invulnerable: bool = False) -> None:
        """Spawn the player's ship.
        
        Args:
            invulnerable: Whether the ship should spawn with invulnerability
        """
        # Remove old ship if it exists
        if self.game.entity_manager.ship in self.game.entity_manager.entities:
            self.game.entity_manager.remove_entity(self.game.entity_manager.ship)
        
        # Create new ship
        ship = Ship(self.game)
        
        # Set invulnerability if requested
        if invulnerable:
            ship.invulnerable = True
            ship.invulnerable_timer = SHIP_INVULNERABLE_TIME
        
        # Find safe spawn position
        ship_transform = ship.get_component(TransformComponent)
        if ship_transform:
            self._set_safe_ship_position(ship)
        
        # Add ship to game
        self.game.entity_manager.add_entity(ship)
        print("Ship spawned successfully")

    def _set_safe_ship_position(self, ship: Ship) -> None:
        """Find and set a safe spawn position for the ship.
        
        Args:
            ship: The ship entity to position
        """
        ship_transform = ship.get_component(TransformComponent)
        if not ship_transform:
            return
            
        # Try to find a safe spawn position
        for attempt in range(10):  # Limit attempts
            ship_transform.position = pygame.Vector2(
                random.randint(100, WINDOW_WIDTH - 100),
                random.randint(100, WINDOW_HEIGHT - 100)
            )
            
            # Check if position is safe from asteroids
            ship_collision = ship.get_component(CollisionComponent)
            if not ship_collision:
                continue
                
            # Check distance to all asteroids
            safe_position = True
            for asteroid in self.game.entity_manager.asteroids:
                asteroid_transform = asteroid.get_component(TransformComponent)
                if asteroid_transform:
                    distance = (asteroid_transform.position - ship_transform.position).length()
                    if distance < 100:  # Minimum safe distance
                        safe_position = False
                        break
            
            if safe_position:
                return
        
        # If no safe position found, use center
        ship_transform.position = pygame.Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
        print("No safe position found, spawning ship at center")

    def respawn_ship(self) -> None:
        """Respawn the ship after death."""
        self.logger.info("Respawning ship")
        
        # Create new ship if none exists
        if not self.game.entity_manager.ship:
            self.spawn_ship(invulnerable=True)
            return
            
        # Reset existing ship
        ship = self.game.entity_manager.ship
        
        # Reset position to center
        transform = ship.get_component(TransformComponent)
        if transform:
            transform.position = pygame.Vector2(self.game.width // 2, self.game.height // 2)
            transform.rotation = 0
        
        # Reset physics
        physics = ship.get_component(PhysicsComponent)
        if physics:
            physics.velocity = pygame.Vector2(0, 0)
            physics.angular_velocity = 0
        
        # Make ship invulnerable
        ship.invulnerable = True
        ship.invulnerable_timer = SHIP_INVULNERABLE_TIME

    def update(self, dt: float) -> None:
        """Update spawning logic.
        
        Args:
            dt: Delta time in seconds
        """
        if self.spawning_wave:
            self.spawn_timer += dt
            if self.spawn_timer >= self.spawn_delay and self.asteroids_to_spawn > 0:
                self._spawn_asteroid()
                self.asteroids_to_spawn -= 1
                self.spawn_timer = 0.0
                
                if self.asteroids_to_spawn <= 0:
                    self.spawning_wave = False 