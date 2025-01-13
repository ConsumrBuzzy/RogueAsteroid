"""Handles entity management and tracking."""
from typing import List, Optional
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.core.entities.base import Entity

class EntityManager:
    def __init__(self, game):
        """Initialize the entity manager.
        
        Args:
            game: Reference to the main game instance
        """
        self.game = game
        self.entities: List[Entity] = []
        self.bullets: List[Bullet] = []
        self.asteroids: List[Asteroid] = []
        self.ship: Optional[Ship] = None

    def update(self, dt: float) -> None:
        """Update all entities.
        
        Args:
            dt: Delta time in seconds
        """
        for entity in self.entities[:]:  # Copy list to allow removal
            entity.update(dt)
            
        # Check for level completion
        if self.ship and not any(isinstance(entity, Asteroid) for entity in self.entities):
            self.game._complete_level()

    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the game.
        
        Args:
            entity: The entity to add
        """
        if entity not in self.entities:
            self.entities.append(entity)
            print(f"Added entity: {entity}")
            
            # Add to specific lists based on type
            if isinstance(entity, Bullet):
                self.bullets.append(entity)
            elif isinstance(entity, Asteroid):
                self.asteroids.append(entity)
            elif isinstance(entity, Ship):
                self.ship = entity

    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the game.
        
        Args:
            entity: The entity to remove
        """
        if entity in self.entities:
            self.entities.remove(entity)
            print(f"Removed entity: {entity}")
            
            # Remove from specific lists if present
            if entity in self.bullets:
                self.bullets.remove(entity)
            if entity in self.asteroids:
                self.asteroids.remove(entity)
            if entity == self.ship:
                self.ship = None

    def clear_all(self) -> None:
        """Clear all entities."""
        self.entities.clear()
        self.bullets.clear()
        self.asteroids.clear()
        self.ship = None 