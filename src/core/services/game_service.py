"""Game service for core game management."""
from typing import Dict, Optional, List
import pygame

from ..entity import Entity, EntityFactory
from . import ServiceManager

class GameService:
    """Service for core game management.
    
    Provides:
    - Game loop management
    - Service coordination
    - State management
    - Entity lifecycle
    - Performance monitoring
    """
    
    def __init__(self, screen: pygame.Surface, settings: Dict):
        """Initialize the game service.
        
        Args:
            screen: Pygame surface to render to
            settings: Game settings dictionary
        """
        self._screen = screen
        self._settings = settings
        self._running = False
        self._paused = False
        self._dt = 0
        
        # Get required services
        service_manager = ServiceManager()
        self._input_service = service_manager.get_service('input')
        self._physics_service = service_manager.get_service('physics')
        self._render_service = service_manager.get_service('render')
        self._collision_service = service_manager.get_service('collision')
        self._particle_service = service_manager.get_service('particle')
        self._ui_service = service_manager.get_service('ui')
        self._state_service = service_manager.get_service('state')
        self._menu_service = service_manager.get_service('menu')
        self._high_score_service = service_manager.get_service('high_score')
        self._achievement_service = service_manager.get_service('achievement')
        self._statistics_service = service_manager.get_service('statistics')
        
        # Initialize entity factory
        self._entity_factory = EntityFactory()
        
        # Entity tracking
        self._entities: List[Entity] = []
        
        print("GameService initialized")
    
    def start(self) -> None:
        """Start the game loop."""
        self._running = True
        self._state_service.change_state('MAIN_MENU')
        print("Game loop started")
    
    def stop(self) -> None:
        """Stop the game loop."""
        self._running = False
        print("Game loop stopped")
    
    def pause(self) -> None:
        """Pause the game."""
        self._paused = True
        print("Game paused")
    
    def resume(self) -> None:
        """Resume the game."""
        self._paused = False
        print("Game resumed")
    
    def is_running(self) -> bool:
        """Check if game is running.
        
        Returns:
            True if game is running
        """
        return self._running
    
    def is_paused(self) -> bool:
        """Check if game is paused.
        
        Returns:
            True if game is paused
        """
        return self._paused
    
    def update(self, dt: float) -> None:
        """Update game state.
        
        Args:
            dt: Delta time in seconds
        """
        self._dt = dt
        
        if not self._paused:
            # Update all services
            self._input_service.update()
            self._physics_service.update(dt)
            self._collision_service.update()
            self._particle_service.update(dt)
            self._state_service.update(dt)
            self._menu_service.update(dt)
            self._achievement_service.update(dt)
            self._statistics_service.update(dt)
            
            # Update all entities
            for entity in self._entities[:]:  # Copy list to allow removal
                entity.update(dt)
    
    def draw(self) -> None:
        """Draw the current game state."""
        # Clear screen
        self._screen.fill((0, 0, 0))
        
        # Draw in layers
        self._particle_service.draw()
        self._render_service.render()
        self._ui_service.draw()
        
        # Update display
        pygame.display.flip()
    
    def add_entity(self, entity: Entity) -> None:
        """Add an entity to the game.
        
        Args:
            entity: Entity to add
        """
        self._entities.append(entity)
        
        # Register with services as needed
        if entity.get_component('RenderComponent'):
            self._render_service.register_entity(entity)
        if entity.get_component('PhysicsComponent'):
            self._physics_service.register_entity(entity)
        if entity.get_component('CollisionComponent'):
            self._collision_service.register_entity(entity)
        
        print(f"Added entity {entity.id} to game")
    
    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the game.
        
        Args:
            entity: Entity to remove
        """
        if entity in self._entities:
            self._entities.remove(entity)
            
            # Unregister from services
            self._render_service.unregister_entity(entity)
            self._physics_service.unregister_entity(entity)
            self._collision_service.unregister_entity(entity)
            
            print(f"Removed entity {entity.id} from game")
    
    def clear(self) -> None:
        """Clear all game state."""
        # Clear all entities
        self._entities.clear()
        
        # Clear all services
        self._render_service.clear()
        self._physics_service.clear()
        self._collision_service.clear()
        self._particle_service.clear()
        self._ui_service.clear()
        
        print("Game state cleared") 