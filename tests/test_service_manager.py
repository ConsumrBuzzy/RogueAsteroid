"""Tests for ServiceManager."""
import pytest
from typing import Optional

from src.core.services.service_manager import ServiceManager

# Mock services for testing
class MockService:
    """A basic mock service."""
    def __init__(self):
        self.initialized = True

class MockGameDependentService:
    """A mock service that requires game instance."""
    def __init__(self, game):
        self.game = game
        self.initialized = True

class MockDependentService:
    """A mock service that depends on MockService."""
    def __init__(self, mock_service: MockService):
        self.mock_service = mock_service
        self.initialized = True

@pytest.fixture
def mock_game():
    """Create a mock game instance."""
    class MockGame:
        def __init__(self):
            self.initialized = True
    return MockGame()

@pytest.fixture
def service_manager(mock_game):
    """Create a service manager instance."""
    return ServiceManager(game=mock_game)

@pytest.mark.unit
class TestServiceManager:
    """Test cases for ServiceManager."""
    
    def test_service_manager_init(self, service_manager):
        """Test service manager initialization."""
        assert service_manager is not None
        assert service_manager.game is not None
        
    def test_register_basic_service(self, service_manager):
        """Test registering a basic service."""
        service_manager.register_service("mock", MockService)
        service = service_manager.get_service(MockService)
        assert service is not None
        assert isinstance(service, MockService)
        assert service.initialized
        
    def test_register_game_dependent_service(self, service_manager):
        """Test registering a service that requires game instance."""
        service_manager.register_service("game_dependent", MockGameDependentService)
        service = service_manager.get_service(MockGameDependentService)
        assert service is not None
        assert isinstance(service, MockGameDependentService)
        assert service.game == service_manager.game
        
    def test_register_dependent_service(self, service_manager):
        """Test registering a service with dependencies."""
        # Register the dependency first
        service_manager.register_service("mock", MockService)
        # Register the dependent service
        service_manager.register_service("dependent", MockDependentService)
        
        service = service_manager.get_service(MockDependentService)
        assert service is not None
        assert isinstance(service, MockDependentService)
        assert isinstance(service.mock_service, MockService)
        
    def test_duplicate_service_registration(self, service_manager):
        """Test that registering a duplicate service raises an error."""
        service_manager.register_service("mock", MockService)
        with pytest.raises(RuntimeError):
            service_manager.register_service("mock", MockService)
            
    def test_cleanup(self, service_manager):
        """Test service cleanup."""
        service_manager.register_service("mock", MockService)
        service_manager.cleanup()
        assert service_manager.get_service(MockService) is None 