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
        # Initialize system services first
        self._services['settings'] = SettingsService()
        self._services['events'] = EventManagerService()
        self._services['resources'] = ResourceManagerService()
        
        # Initialize core services
        self._services['state'] = StateService()
        self._services['input'] = InputService()
        self._services['entity_factory'] = EntityFactoryService()
        
        # Initialize rendering and graphics services
        self._services['render'] = RenderService(screen)
        self._services['particle'] = ParticleService(screen)
        self._services['ui'] = UIService(screen)
        
        # Initialize gameplay services
        self._services['physics'] = PhysicsService(settings['window']['width'], 
                                                 settings['window']['height'])
        self._services['collision'] = CollisionService()
        self._services['menu'] = MenuService()
        self._services['high_score'] = HighScoreService()
        self._services['achievement'] = AchievementService()
        self._services['statistics'] = StatisticsService()
        
        # Initialize game service last as it depends on others
        self._services['game'] = GameService(screen, settings)
        
        print("All services initialized")
    
    def get_service(self, service_name: str) -> Optional[object]:
        """Get a service by name.
        
        Args:
            service_name: Name of service to get
            
        Returns:
            Service instance if found, None otherwise
        """
        return self._services.get(service_name)
    
    def cleanup(self) -> None:
        """Clean up all services."""
        # Clean up in reverse dependency order
        cleanup_order = [
            'game',
            'statistics', 'achievement', 'high_score',
            'menu', 'collision', 'physics',
            'ui', 'particle', 'render',
            'entity_factory', 'input', 'state',
            'resources', 'events', 'settings'
        ]
        
        for service_name in cleanup_order:
            service = self._services.get(service_name)
            if service and hasattr(service, 'cleanup'):
                service.cleanup()
                print(f"Cleaned up {service_name} service")
                
        self._services.clear()
        print("All services cleaned up") 