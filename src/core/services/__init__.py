"""Service management for game systems."""
from typing import Dict, Optional, Type, TypeVar
import pygame

from .settings_service import SettingsService
from .event_manager_service import EventManagerService
from .resource_manager_service import ResourceManagerService
from .state_service import StateService
from .menu_service import MenuService
from .ui_service import UIService
from .entity_factory_service import EntityFactoryService
from .game_service import GameService
from .achievement_service import AchievementService
from .statistics_service import StatisticsService
from .input_service import InputService
from .physics_service import PhysicsService
from .render_service import RenderService
from .collision_service import CollisionService
from .particle_service import ParticleService
from .high_score_service import HighScoreService

T = TypeVar('T')

class ServiceManager:
    """Manager for game services.
    
    Provides:
    - Service registration
    - Service access
    - Service lifecycle management
    """
    
    _instance = None
    
    def __new__(cls):
        """Create or return singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        """Initialize the service manager."""
        if self._initialized:
            return
            
        self._services: Dict[str, object] = {}
        self._initialized = True
        print("ServiceManager initialized")
        
    def register_service(self, name: str, service: object) -> None:
        """Register a service.
        
        Args:
            name: Service name
            service: Service instance
        """
        if not name:
            raise ValueError("Service name cannot be empty")
        if service is None:
            raise ValueError("Service instance cannot be None")
            
        self._services[name] = service
        print(f"Registered service: {name}")
        
    def get_service(self, name: str, service_type: Optional[Type[T]] = None) -> Optional[T]:
        """Get a service by name.
        
        Args:
            name: Service name
            service_type: Optional type to cast service to
            
        Returns:
            Service instance or None if not found
        """
        service = self._services.get(name)
        if service is None:
            print(f"Warning: Service '{name}' not found")
            return None
            
        if service_type is not None:
            try:
                return service_type(service)
            except (TypeError, ValueError) as e:
                print(f"Warning: Could not cast service '{name}' to type {service_type.__name__}: {e}")
                return None
                
        return service
        
    def init_services(self, screen: pygame.Surface) -> bool:
        """Initialize all game services.
        
        Args:
            screen: Pygame surface for rendering
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Core services (no dependencies)
            settings = SettingsService()
            self.register_service("settings", settings)
            
            events = EventManagerService()
            self.register_service("events", events)
            
            resources = ResourceManagerService()
            self.register_service("resources", resources)
            
            # Input service (needed by many services)
            input_service = InputService()
            self.register_service("input", input_service)
            
            # State service (needed by menu)
            state = StateService()
            self.register_service("state", state)
            
            # Rendering stack
            render = RenderService(screen)
            self.register_service("render", render)
            
            ui = UIService(screen)
            self.register_service("ui", ui)
            
            menu = MenuService(ui_service=ui, state_service=state, input_service=input_service)
            self.register_service("menu", menu)
            
            # Physics stack
            physics = PhysicsService(screen.get_width(), screen.get_height())
            self.register_service("physics", physics)
            
            collision = CollisionService()
            self.register_service("collision", collision)
            
            particle = ParticleService(screen)
            self.register_service("particle", particle)
            
            # Entity system (depends on many services)
            entity_factory = EntityFactoryService(service_manager=self)
            self.register_service("entity_factory", entity_factory)
            
            # Data services (depend on settings and events)
            high_score = HighScoreService(settings, events)
            self.register_service("high_score", high_score)
            
            achievements = AchievementService(settings, events)
            self.register_service("achievement", achievements)
            
            statistics = StatisticsService(settings, events)
            self.register_service("statistics", statistics)
            
            # Game service (depends on everything)
            game = GameService(screen=screen, settings=settings.get_all(), service_manager=self)
            self.register_service("game", game)
            
            print("All services initialized")
            return True
            
        except Exception as e:
            print(f"Error initializing services: {e}")
            self.cleanup()
            return False
            
    def cleanup(self) -> None:
        """Clean up all services."""
        # Clean up in reverse order of initialization
        services = list(self._services.items())
        for name, service in reversed(services):
            if hasattr(service, "cleanup"):
                service.cleanup()
            print(f"Cleaned up {name} service")
        self._services.clear()
        print("All services cleaned up") 