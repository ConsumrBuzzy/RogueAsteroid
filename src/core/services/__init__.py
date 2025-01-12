"""Service initialization and management."""
from typing import Dict, Optional
import pygame

from .game_service import GameService
from .input_service import InputService
from .physics_service import PhysicsService
from .render_service import RenderService
from .collision_service import CollisionService
from .particle_service import ParticleService
from .ui_service import UIService
from .state_service import StateService
from .menu_service import MenuService
from .high_score_service import HighScoreService
from .settings_service import SettingsService
from .achievement_service import AchievementService
from .statistics_service import StatisticsService
from .entity_factory_service import EntityFactoryService
from .event_manager_service import EventManagerService
from .resource_manager_service import ResourceManagerService

class ServiceManager:
    """Manages all game services."""
    
    _instance = None
    
    def __new__(cls):
        """Ensure singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
    
    def __init__(self):
        """Initialize service manager."""
        if self._initialized:
            return
            
        self._services: Dict[str, object] = {}
        self._initialized = True
        print("ServiceManager initialized")
        
    def init_services(self, screen: pygame.Surface, settings: Dict) -> None:
        """Initialize all game services.
        
        Args:
            screen: Pygame surface to render to
            settings: Game settings
        """
        try:
            # Initialize system services first (no dependencies)
            self._services['settings'] = SettingsService()
            self._services['events'] = EventManagerService()
            self._services['resources'] = ResourceManagerService()
            
            # Get service references
            settings_service = self._services['settings']
            event_manager = self._services['events']
            
            # Initialize core services (depend on system services)
            self._services['state'] = StateService()
            self._services['input'] = InputService()
            self._services['entity_factory'] = EntityFactoryService()
            
            # Initialize rendering services (depend on resources)
            self._services['render'] = RenderService(screen)
            self._services['particle'] = ParticleService(screen)
            self._services['ui'] = UIService(screen)
            
            # Initialize gameplay services (depend on core and rendering)
            self._services['physics'] = PhysicsService(
                settings['window']['width'], 
                settings['window']['height']
            )
            self._services['collision'] = CollisionService()
            
            # Initialize menu and data services
            self._services['menu'] = MenuService(self._services['ui'])
            self._services['high_score'] = HighScoreService(
                settings_service=settings_service,
                event_manager=event_manager
            )
            self._services['achievement'] = AchievementService(
                settings_service=settings_service,
                event_manager=event_manager
            )
            self._services['statistics'] = StatisticsService(
                settings_service=settings_service,
                event_manager=event_manager
            )
            
            # Initialize game service last (depends on all others)
            self._services['game'] = GameService(screen, settings, self)
            
        except Exception as e:
            print(f"Error initializing services: {e}")
            self.cleanup()
            raise
            
    def get_service(self, name: str) -> Optional[object]:
        """Get a service by name.
        
        Args:
            name: Service name
            
        Returns:
            Service instance or None if not found
        """
        return self._services.get(name)
        
    def cleanup(self) -> None:
        """Clean up all services."""
        # Clean up in reverse dependency order
        for service_name in reversed(list(self._services.keys())):
            service = self._services[service_name]
            if hasattr(service, 'cleanup'):
                service.cleanup()
                print(f"Cleaned up {service_name} service")
        self._services.clear()
        print("All services cleaned up") 