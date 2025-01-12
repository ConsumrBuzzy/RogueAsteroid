"""Service management for game systems."""
from typing import Dict, Optional, Type, TypeVar, Set
import pygame

# Service name constants
SERVICE_SETTINGS = "settings"
SERVICE_EVENTS = "events"
SERVICE_RESOURCES = "resources"
SERVICE_INPUT = "input"
SERVICE_STATE = "state"
SERVICE_RENDER = "render"
SERVICE_UI = "ui"
SERVICE_MENU = "menu"
SERVICE_PHYSICS = "physics"
SERVICE_COLLISION = "collision"
SERVICE_PARTICLE = "particle"
SERVICE_ENTITY_FACTORY = "entity_factory"
SERVICE_HIGH_SCORE = "high_score"
SERVICE_ACHIEVEMENT = "achievement"
SERVICE_STATISTICS = "statistics"
SERVICE_GAME = "game"

# Import services
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
        self._dependencies: Dict[str, Set[str]] = {
            SERVICE_MENU: {SERVICE_UI, SERVICE_STATE, SERVICE_INPUT},
            SERVICE_GAME: {SERVICE_INPUT, SERVICE_PHYSICS, SERVICE_RENDER, SERVICE_COLLISION,
                          SERVICE_PARTICLE, SERVICE_UI, SERVICE_STATE, SERVICE_MENU,
                          SERVICE_HIGH_SCORE, SERVICE_ACHIEVEMENT, SERVICE_STATISTICS,
                          SERVICE_EVENTS, SERVICE_RESOURCES, SERVICE_ENTITY_FACTORY},
            SERVICE_HIGH_SCORE: {SERVICE_SETTINGS, SERVICE_EVENTS},
            SERVICE_ACHIEVEMENT: {SERVICE_SETTINGS, SERVICE_EVENTS},
            SERVICE_STATISTICS: {SERVICE_SETTINGS, SERVICE_EVENTS},
            SERVICE_ENTITY_FACTORY: {SERVICE_PHYSICS, SERVICE_COLLISION, SERVICE_PARTICLE}
        }
        self._initialized = True
        print("ServiceManager initialized")

    def _validate_dependencies(self, service_name: str) -> None:
        """Validate service dependencies are registered.
        
        Args:
            service_name: Service to validate
            
        Raises:
            ValueError: If dependencies are missing
        """
        if service_name not in self._dependencies:
            return
            
        missing = [dep for dep in self._dependencies[service_name] 
                  if dep not in self._services]
        if missing:
            raise ValueError(f"Missing dependencies for {service_name}: {missing}")

    def register_service(self, name: str, service: object) -> None:
        """Register a service.
        
        Args:
            name: Service name
            service: Service instance
            
        Raises:
            ValueError: If service name is empty or instance is None
        """
        if not name:
            raise ValueError("Service name cannot be empty")
        if service is None:
            raise ValueError("Service instance cannot be None")
            
        # Validate dependencies before registration
        self._validate_dependencies(name)
            
        self._services[name] = service
        print(f"Registered service: {name}")
        
        # Special handling for StateService and EventManager
        if name == SERVICE_STATE and hasattr(service, 'set_event_manager'):
            event_manager = self.get_service(SERVICE_EVENTS)
            if event_manager:
                service.set_event_manager(event_manager)
                print("Set event manager for state service")

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
            self.register_service(SERVICE_SETTINGS, settings)
            
            events = EventManagerService()
            self.register_service(SERVICE_EVENTS, events)
            
            # State service (needed by many services)
            state = StateService()
            self.register_service(SERVICE_STATE, state)
            
            # Resource service
            resources = ResourceManagerService()
            self.register_service(SERVICE_RESOURCES, resources)
            
            # Input service
            input_service = InputService()
            self.register_service(SERVICE_INPUT, input_service)
            
            # Rendering stack
            render = RenderService(screen)
            self.register_service(SERVICE_RENDER, render)
            
            ui = UIService(screen)
            self.register_service(SERVICE_UI, ui)
            
            # Physics stack
            physics = PhysicsService(screen.get_width(), screen.get_height())
            self.register_service(SERVICE_PHYSICS, physics)
            
            collision = CollisionService()
            self.register_service(SERVICE_COLLISION, collision)
            
            particle = ParticleService(screen)
            self.register_service(SERVICE_PARTICLE, particle)
            
            # Entity system
            entity_factory = EntityFactoryService(service_manager=self)
            self.register_service(SERVICE_ENTITY_FACTORY, entity_factory)
            
            # Data services
            high_score = HighScoreService(settings, events)
            self.register_service(SERVICE_HIGH_SCORE, high_score)
            
            achievements = AchievementService(settings, events)
            self.register_service(SERVICE_ACHIEVEMENT, achievements)
            
            statistics = StatisticsService(settings, events)
            self.register_service(SERVICE_STATISTICS, statistics)
            
            # Menu service (depends on UI and State)
            menu = MenuService(ui_service=ui, state_service=state, input_service=input_service)
            self.register_service(SERVICE_MENU, menu)
            
            # Game service (depends on everything)
            game = GameService(screen=screen, settings=settings.get_all(), service_manager=self)
            self.register_service(SERVICE_GAME, game)
            
            print("All services initialized")
            return True
            
        except Exception as e:
            print(f"Error initializing services: {e}")
            self.cleanup()
            return False

    def cleanup(self) -> None:
        """Clean up all services.
        
        Ensures each service is cleaned up properly, even if errors occur.
        Services are cleaned up in reverse order of initialization.
        """
        cleanup_errors = []
        services = list(self._services.items())
        
        # Clean up in reverse order of initialization
        for name, service in reversed(services):
            try:
                if hasattr(service, "cleanup"):
                    service.cleanup()
                print(f"Cleaned up {name} service")
            except Exception as e:
                error_msg = f"Error cleaning up {name} service: {e}"
                print(error_msg)
                cleanup_errors.append(error_msg)
                # Continue cleanup despite errors
                continue
                
        # Clear service registry
        self._services.clear()
        
        # Report any cleanup errors
        if cleanup_errors:
            print("\nService cleanup completed with errors:")
            for error in cleanup_errors:
                print(f"- {error}")
        else:
            print("All services cleaned up successfully") 