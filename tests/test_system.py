"""Tests for game systems."""
import pytest
import pygame
from pygame import Surface
from typing import Tuple

from src.core.entities.base import Entity
from src.core.components import (
    TransformComponent,
    PhysicsComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)
from src.core.game import Game
from src.core.services import ServiceManager
from src.core.constants import TARGET_FPS

@pytest.mark.system
class TestGameInitialization:
    """Test game system initialization and shutdown."""
    
    def test_game_creation(self, game_env):
        """Test game object creation and basic initialization."""
        game = Game()
        assert game is not None
        assert game.running is False
        assert game.services is not None
        
    def test_service_initialization_order(self, game_env):
        """Test services are initialized in correct dependency order."""
        game = Game()
        service_manager = game.services
        
        # Get initialization order
        init_order = service_manager._initialization_order
        
        # Verify core services are initialized first
        assert init_order[0] == EventManagerService
        assert init_order[1] == StateService
        assert init_order[2] == ResourceManagerService
        
        # Verify dependent services come after core services
        core_services = {EventManagerService, StateService, ResourceManagerService}
        for service_type in init_order[3:]:
            for dependency in service_manager._get_dependencies(service_type):
                assert dependency in core_services or init_order.index(dependency) < init_order.index(service_type)
    
    def test_service_dependencies(self, game_env):
        """Test service dependency resolution."""
        game = Game()
        service_manager = game.services
        
        # Test core service dependencies
        state_service = service_manager.get_service(StateService)
        event_manager = service_manager.get_service(EventManagerService)
        assert event_manager in service_manager._get_dependencies(StateService)
        
        # Test rendering dependencies
        render_service = service_manager.get_service(RenderService)
        resource_manager = service_manager.get_service(ResourceManagerService)
        assert resource_manager in service_manager._get_dependencies(RenderService)
        
        # Test entity service dependencies
        entity_service = service_manager.get_service(EntityService)
        physics_service = service_manager.get_service(PhysicsService)
        assert physics_service in service_manager._get_dependencies(EntityService)

@pytest.mark.system
class TestGameLoop:
    """Test game loop functionality."""
    
    def test_game_loop_timing(self, game_env):
        """Test game loop maintains correct timing."""
        game = Game()
        frame_times = []
        
        def mock_update(dt):
            frame_times.append(dt)
            if len(frame_times) >= 60:  # Collect 60 frames worth of data
                game.running = False
        
        # Replace update method with mock
        game.update = mock_update
        
        # Run game loop for 60 frames
        game.running = True
        game.run()
        
        # Verify frame timing
        avg_dt = sum(frame_times) / len(frame_times)
        target_dt = 1.0 / TARGET_FPS
        assert abs(avg_dt - target_dt) < 0.002  # Allow 2ms variance
        
    def test_game_state_transitions(self, game_env):
        """Test game state transitions during runtime."""
        game = Game()
        state_service = game.services.get_service(StateService)
        transitions = []
        
        def state_change_handler(old_state, new_state):
            transitions.append((old_state, new_state))
            if len(transitions) >= 3:  # After 3 transitions
                game.running = False
        
        # Subscribe to state changes
        state_service.subscribe(state_change_handler)
        
        # Start game and trigger state changes
        game.running = True
        game.run()
        
        # Verify state transitions
        assert len(transitions) == 3
        assert all(old != new for old, new in transitions)  # States should change
        
    def test_service_interaction(self, game_env):
        """Test interaction between services during runtime."""
        game = Game()
        event_manager = game.services.get_service(EventManagerService)
        state_service = game.services.get_service(StateService)
        events_processed = []
        
        def event_handler(event):
            events_processed.append(event)
            if len(events_processed) >= 10:  # After 10 events
                game.running = False
        
        # Subscribe to game events
        event_manager.subscribe("game_event", event_handler)
        
        # Start game
        game.running = True
        game.run()
        
        # Verify event processing
        assert len(events_processed) == 10
        
    def test_cleanup_order(self, game_env):
        """Test services are cleaned up in correct order."""
        game = Game()
        service_manager = game.services
        cleanup_order = []
        
        # Replace cleanup methods with tracking versions
        for service in service_manager._services.values():
            original_cleanup = service.cleanup
            def make_cleanup_tracker(service_type, original):
                def tracked_cleanup():
                    cleanup_order.append(service_type)
                    return original()
                return tracked_cleanup
            service.cleanup = make_cleanup_tracker(type(service), original_cleanup)
        
        # Run game briefly then cleanup
        game.running = True
        game.run()
        game.cleanup()
        
        # Verify cleanup order (reverse of initialization)
        init_order = service_manager._initialization_order
        expected_cleanup = list(reversed(init_order))
        assert cleanup_order == expected_cleanup

@pytest.mark.system
class TestErrorHandling:
    """Test system-level error handling."""
    
    def test_service_failure_handling(self, game_env):
        """Test handling of service initialization failures."""
        game = Game()
        service_manager = game.services
        
        # Inject failing service
        class FailingService:
            def __init__(self):
                raise RuntimeError("Service failed to initialize")
        
        with pytest.raises(RuntimeError):
            service_manager.register_service("failing", FailingService)
        
        # Verify other services are still functional
        assert service_manager.get_service(StateService) is not None
        
    def test_error_recovery(self, game_env):
        """Test system recovery from non-fatal errors."""
        game = Game()
        error_count = 0
        
        def error_prone_update(dt):
            nonlocal error_count
            error_count += 1
            if error_count <= 3:  # First 3 updates raise error
                raise ValueError("Test error")
            if error_count > 5:  # Stop after 5 updates
                game.running = False
        
        # Replace update method with error-prone version
        game.update = error_prone_update
        
        # Run game - should handle errors and continue
        game.running = True
        game.run()
        
        assert error_count > 3  # Should survive first 3 errors
        assert game.services.get_service(StateService) is not None  # Services should remain functional 