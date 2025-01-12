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
        self._services[name] = service
        print(f"Registered service: {name}")
        
    def get_service(self, name: str) -> Optional[object]:
        """Get a service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance or None if not found
        """
        return self._services.get(name)
        
    def init_services(self, screen: pygame.Surface) -> bool:
        """Initialize all game services.
        
        Args:
            screen: Pygame surface for rendering
            
        Returns:
            True if initialization successful, False otherwise
        """
        try:
            # Core services
            settings = SettingsService()
            self.register_service("settings", settings)
            
            events = EventManagerService()
            self.register_service("events", events)
            
            resources = ResourceManagerService()
            self.register_service("resources", resources)
            
            # Physics service
            physics = PhysicsService(screen.get_width(), screen.get_height())
            self.register_service("physics", physics)
            
            # Render service
            render = RenderService(screen)
            self.register_service("render", render)
            
            # Input service
            input_service = InputService()
            self.register_service("input", input_service)
            
            # UI services
            ui = UIService(screen)
            self.register_service("ui", ui)
            
            state = StateService()
            self.register_service("state", state)
            
            menu = MenuService(ui_service=ui, state_service=state)
            self.register_service("menu", menu)
            
            # Game services
            entity_factory = EntityFactoryService(service_manager=self)
            self.register_service("entity_factory", entity_factory)
            
            game = GameService(screen=screen, settings=settings.get_all(), service_manager=self)
            self.register_service("game", game)
            
            # Data services
            achievements = AchievementService(settings, events)
            self.register_service("achievements", achievements)
            
            statistics = StatisticsService(settings, events)
            self.register_service("statistics", statistics)
            
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