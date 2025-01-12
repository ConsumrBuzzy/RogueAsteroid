"""Service management system for RogueAsteroid."""
from typing import Dict, Type, Optional, List, Set
import inspect

from .event_manager_service import EventManagerService
from .state_service import StateService
from .resource_manager_service import ResourceManagerService
from .input_service import InputService
from .render_service import RenderService
from .physics_service import PhysicsService
from .entity_manager_service import EntityManagerService
from .particle_service import ParticleService
from .audio_service import AudioService
from .menu_service import MenuService
from .game_service import GameService
from .collision_service import CollisionService
from .achievement_service import AchievementService
from .high_score_service import HighScoreService
from .statistics_service import StatisticsService
from .settings_service import SettingsService
from .logging_service import LoggingService
from .ui_service import UIService

__all__ = [
    'ServiceManager',
    'EventManagerService',
    'StateService',
    'ResourceManagerService',
    'InputService',
    'RenderService',
    'PhysicsService',
    'EntityManagerService',
    'ParticleService',
    'AudioService',
    'MenuService',
    'GameService',
    'CollisionService',
    'AchievementService',
    'HighScoreService',
    'StatisticsService',
    'SettingsService',
    'LoggingService',
    'UIService'
]

class ServiceManager:
    """Manages game services and their dependencies."""
    
    def __init__(self):
        """Initialize the service manager."""
        self._services: Dict[str, object] = {}
        self._service_types: Dict[str, Type] = {}
        self._initialization_order: List[Type] = []
        
    def register_service(self, name: str, service_type: Type) -> None:
        """Register a new service.
        
        Args:
            name: Unique identifier for the service.
            service_type: The class of the service to register.
        
        Raises:
            RuntimeError: If service initialization fails or dependencies are invalid.
        """
        if name in self._services:
            raise RuntimeError(f"Service {name} already registered")
            
        # Check dependencies before instantiation
        dependencies = self._get_dependencies(service_type)
        for dependency in dependencies:
            if not any(isinstance(service, dependency) for service in self._services.values()):
                raise RuntimeError(f"Service {name} requires {dependency.__name__} which is not registered")
        
        try:
            # Create service instance
            if callable(service_type) and not isinstance(service_type, type):
                service = service_type()
            else:
                service = service_type()
                
            self._services[name] = service
            self._service_types[name] = service_type if isinstance(service_type, type) else type(service)
            self._initialization_order.append(self._service_types[name])
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize service {name}: {str(e)}")
            
    def get_service(self, service_type: Type) -> Optional[object]:
        """Get a service instance by type.
        
        Args:
            service_type: The type of service to retrieve.
            
        Returns:
            The service instance if found, None otherwise.
        """
        for service in self._services.values():
            if isinstance(service, service_type):
                return service
        return None
        
    def cleanup(self) -> None:
        """Clean up all services in reverse initialization order."""
        # Create a list of cleanup errors
        cleanup_errors = []
        
        # Clean up services in reverse order
        for service_type in reversed(self._initialization_order):
            service = self.get_service(service_type)
            if service and hasattr(service, 'cleanup'):
                try:
                    service.cleanup()
                except Exception as e:
                    cleanup_errors.append(f"Error cleaning up {service_type.__name__}: {str(e)}")
        
        # Clear service collections
        self._services.clear()
        self._service_types.clear()
        self._initialization_order.clear()
        
        # Report any cleanup errors
        if cleanup_errors:
            print("Errors during service cleanup:")
            for error in cleanup_errors:
                print(f"  {error}")
                
    def _get_dependencies(self, service_type: Type) -> Set[Type]:
        """Get the service dependencies for a service type.
        
        Args:
            service_type: The service type to check.
            
        Returns:
            Set of service types that this service depends on.
        """
        dependencies = set()
        
        # Check constructor parameters
        if isinstance(service_type, type):
            sig = inspect.signature(service_type.__init__)
            for param in sig.parameters.values():
                if param.annotation != inspect.Parameter.empty:
                    if isinstance(param.annotation, type):
                        dependencies.add(param.annotation)
                        
        return dependencies 