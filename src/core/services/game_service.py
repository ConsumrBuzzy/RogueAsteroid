"""Game service for core game management."""
from typing import Dict, Optional, List
import pygame
from ..entity import Entity, EntityFactory
from .input_service import InputService
from .physics_service import PhysicsService
from .render_service import RenderService
from .collision_service import CollisionService
from .particle_service import ParticleService
from .ui_service import UIService

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
        
        # Initialize services
        self._entity_factory = EntityFactory()
        self._input_service = InputService()
        self._physics_service = PhysicsService(settings['screen_width'], settings['screen_height'])
        self._render_service = RenderService(screen)
        self._collision_service = CollisionService()
        self._particle_service = ParticleService(screen)
        self._ui_service = UIService(screen)
        
        # Entity tracking
        self._entities: List[Entity] = []
        
        print("GameService initialized")
        
    def start(self) -> None:
        """Start the game loop."""
        self._running = True
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
            
            # Update all entities
            for entity in self._entities:
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
            
    def get_service(self, service_type: str) -> Optional[object]:
        """Get a service by type.
        
        Args:
            service_type: Type of service to get
            
        Returns:
            Service instance if found, None otherwise
        """
        services = {
            'input': self._input_service,
            'physics': self._physics_service,
            'render': self._render_service,
            'collision': self._collision_service,
            'particle': self._particle_service,
            'ui': self._ui_service
        }
        return services.get(service_type)
        
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