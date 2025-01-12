"""Game service for core game management."""
from typing import Dict, Optional, List
import pygame

from ..entity.entity import Entity
from .state_service import GameState

class GameService:
    """Service for core game management.
    
    Provides:
    - Game loop management
    - Service coordination
    - State management
    - Entity lifecycle
    - Performance monitoring
    """
    
    def __init__(self, screen: pygame.Surface, settings: Dict, service_manager):
        """Initialize the game service.
        
        Args:
            screen: Pygame surface to render to
            settings: Game settings dictionary
            service_manager: ServiceManager instance for accessing other services
            
        Raises:
            ValueError: If required services are not available
        """
        self._screen = screen
        self._settings = settings
        self._running = False
        self._paused = False
        self._dt = 0
        
        try:
            # Get required services
            self._input_service = self._get_required_service(service_manager, 'input')
            self._physics_service = self._get_required_service(service_manager, 'physics')
            self._render_service = self._get_required_service(service_manager, 'render')
            self._collision_service = self._get_required_service(service_manager, 'collision')
            self._particle_service = self._get_required_service(service_manager, 'particle')
            self._ui_service = self._get_required_service(service_manager, 'ui')
            self._state_service = self._get_required_service(service_manager, 'state')
            self._menu_service = self._get_required_service(service_manager, 'menu')
            self._high_score_service = self._get_required_service(service_manager, 'high_score')
            self._achievement_service = self._get_required_service(service_manager, 'achievement')
            self._statistics_service = self._get_required_service(service_manager, 'statistics')
            
            # Get system services
            self._event_manager = self._get_required_service(service_manager, 'events')
            self._resource_manager = self._get_required_service(service_manager, 'resources')
            self._entity_factory = self._get_required_service(service_manager, 'entity_factory')
            
            # Subscribe to events
            self._event_manager.subscribe('game_start', self._on_game_start)
            self._event_manager.subscribe('game_over', self._on_game_over)
            self._event_manager.subscribe('level_complete', self._on_level_complete)
            
            print("GameService initialized")
            
        except Exception as e:
            print(f"Error initializing GameService: {e}")
            raise
            
    def _get_required_service(self, service_manager, name: str) -> object:
        """Get a required service.
        
        Args:
            service_manager: ServiceManager instance
            name: Service name
            
        Returns:
            Service instance
            
        Raises:
            ValueError: If service is not available
        """
        service = service_manager.get_service(name)
        if service is None:
            raise ValueError(f"Required service '{name}' not available")
        return service
        
    def start(self) -> None:
        """Start the game loop."""
        self._running = True
        self._event_manager.publish('game_start')
        print("Game loop started")
    
    def stop(self) -> None:
        """Stop the game loop."""
        self._running = False
        self._event_manager.publish('game_stop')
        print("Game loop stopped")
    
    def pause(self) -> None:
        """Pause the game."""
        if self._state_service.get_current_state() == GameState.PLAYING:
            self._paused = True
            self._state_service.change_state(GameState.PAUSED)
            self._event_manager.publish('game_pause')
            print("Game paused")
    
    def resume(self) -> None:
        """Resume the game."""
        if self._state_service.get_current_state() == GameState.PAUSED:
            self._paused = False
            self._state_service.change_state(GameState.PLAYING)
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
        if not self._running:
            return
            
        self._dt = dt
        
        # Check for quit state
        if self._state_service.get_current_state() == GameState.QUIT:
            self.stop()
            return
        
        if not self._paused:
            try:
                # Update all services
                self._input_service.update()
                self._physics_service.update(dt)
                self._collision_service.update()
                self._particle_service.update(dt)
                self._state_service.update(dt)
                self._menu_service.update(dt)
                
                # Update entity factory
                self._entity_factory.update(dt)
                
                # Process events
                self._event_manager.process_events()
                
            except Exception as e:
                print(f"Error updating game state: {e}")
                self.pause()  # Pause game on error
                
    def draw(self) -> None:
        """Draw the current frame."""
        if not self._running:
            return
            
        try:
            # Clear the screen
            self._screen.fill((0, 0, 0))  # Black background
            
            # Draw game elements in order
            self._render_service.draw()
            self._particle_service.draw()
            self._ui_service.draw()
            
            # Update the display
            pygame.display.flip()
            
        except Exception as e:
            print(f"Error drawing game frame: {e}")
            # Continue running but log the error
            
    def clear(self) -> None:
        """Clear all game state."""
        try:
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
            
        except Exception as e:
            print(f"Error clearing game state: {e}")
            # Continue cleanup despite errors
        
    def _on_game_start(self, **kwargs) -> None:
        """Handle game start event."""
        self._resource_manager.preload_resources()
        print("Game started - resources loaded")
        
    def _on_game_over(self, **kwargs) -> None:
        """Handle game over event."""
        score = kwargs.get('score', 0)
        self._high_score_service.add_score(score)
        self._state_service.change_state(GameState.GAME_OVER)
        print(f"Game over - score: {score}")
        
    def _on_level_complete(self, **kwargs) -> None:
        """Handle level complete event."""
        level = kwargs.get('level', 1)
        print(f"Level {level} completed")
        
    def cleanup(self) -> None:
        """Clean up the service."""
        self.clear()
        self._running = False
        self._paused = False
        print("GameService cleaned up") 