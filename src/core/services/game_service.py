"""Game service for core game management."""
from typing import Dict, Optional, List
import pygame

from ..entity import Entity
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
        
        # Get system services
        self._event_manager = service_manager.get_service('events')
        self._resource_manager = service_manager.get_service('resources')
        self._entity_factory = service_manager.get_service('entity_factory')
        
        # Subscribe to events
        self._event_manager.subscribe('game_start', self._on_game_start)
        self._event_manager.subscribe('game_over', self._on_game_over)
        self._event_manager.subscribe('level_complete', self._on_level_complete)
        
        print("GameService initialized")
    
    def start(self) -> None:
        """Start the game loop."""
        self._running = True
        self._event_manager.publish('game_start')
        self._state_service.change_state('MAIN_MENU')
        print("Game loop started")
    
    def stop(self) -> None:
        """Stop the game loop."""
        self._running = False
        self._event_manager.publish('game_stop')
        print("Game loop stopped")
    
    def pause(self) -> None:
        """Pause the game."""
        self._paused = True
        self._event_manager.publish('game_pause')
        print("Game paused")
    
    def resume(self) -> None:
        """Resume the game."""
        self._paused = False
        self._event_manager.publish('game_resume')
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
            
            # Update entity factory
            self._entity_factory.update(dt)
            
            # Process events
            self._event_manager.process_events()
    
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
    
    def add_entity(self, entity_type: str, x: float = 0, y: float = 0, **kwargs) -> Optional[Entity]:
        """Add an entity to the game.
        
        Args:
            entity_type: Type of entity to create
            x: Initial x position
            y: Initial y position
            **kwargs: Additional entity parameters
            
        Returns:
            Created entity or None if creation failed
        """
        entity = self._entity_factory.create_entity(entity_type, x, y, **kwargs)
        if entity:
            self._event_manager.publish('entity_created', entity=entity)
            print(f"Created entity of type {entity_type}")
        return entity
    
    def remove_entity(self, entity: Entity) -> None:
        """Remove an entity from the game.
        
        Args:
            entity: Entity to remove
        """
        self._entity_factory.remove_entity(entity)
        self._event_manager.publish('entity_destroyed', entity=entity)
        print(f"Removed entity {entity.id}")
    
    def clear(self) -> None:
        """Clear all game state."""
        # Clear all entities
        self._entity_factory.clear_all()
        
        # Clear all services
        self._render_service.clear()
        self._physics_service.clear()
        self._collision_service.clear()
        self._particle_service.clear()
        self._ui_service.clear()
        
        # Publish clear event
        self._event_manager.publish('game_clear')
        print("Game state cleared")
        
    def _on_game_start(self, **kwargs) -> None:
        """Handle game start event."""
        self._resource_manager.preload_resources()
        print("Game started - resources loaded")
        
    def _on_game_over(self, **kwargs) -> None:
        """Handle game over event."""
        score = kwargs.get('score', 0)
        self._high_score_service.add_score(score)
        print(f"Game over - score: {score}")
        
    def _on_level_complete(self, **kwargs) -> None:
        """Handle level complete event."""
        level = kwargs.get('level', 1)
        self._statistics_service.record_level_complete(level)
        print(f"Level {level} completed") 