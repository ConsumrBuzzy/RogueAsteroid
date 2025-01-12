"""Test suite for input system."""
import pytest
import pygame
from src.core.game import Game
from src.core.entities.base import Entity
from src.core.entities.components import InputComponent
from src.core.constants import *

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.fixture
def input_entity(game):
    """Create an entity with input component."""
    entity = Entity(game)
    input_comp = entity.add_component(InputComponent)
    return entity, input_comp

@pytest.mark.engine
class TestInputSystem:
    """Test cases for the input system."""
    
    def test_key_binding(self, game, input_entity):
        """Test basic key binding and event handling."""
        entity, input_comp = input_entity
        
        # Track action calls
        action_called = False
        def test_action():
            nonlocal action_called
            action_called = True
        
        # Bind key and simulate press
        input_comp.bind_key(pygame.K_SPACE, test_action)
        input_comp.handle_keydown(pygame.K_SPACE)
        
        assert action_called, "Bound action should be called on key press"
    
    def test_continuous_action(self, game, input_entity):
        """Test continuous action handling."""
        entity, input_comp = input_entity
        
        # Track continuous action calls
        call_count = 0
        def continuous_action():
            nonlocal call_count
            call_count += 1
        
        # Bind continuous action
        input_comp.bind_key(pygame.K_UP, continuous_action, continuous=True)
        
        # Simulate held key
        input_comp.handle_keydown(pygame.K_UP)
        
        # Update multiple frames
        for _ in range(5):
            input_comp.update(1/60)
        
        assert call_count == 5, "Continuous action should be called each frame"
        
        # Release key
        input_comp.handle_keyup(pygame.K_UP)
        input_comp.update(1/60)
        
        assert call_count == 5, "Action should not be called after key release"
    
    def test_multiple_bindings(self, game, input_entity):
        """Test multiple key bindings."""
        entity, input_comp = input_entity
        
        # Track different actions
        actions_called = set()
        def create_action(name):
            def action():
                actions_called.add(name)
            return action
        
        # Bind multiple keys
        bindings = {
            pygame.K_UP: "up",
            pygame.K_DOWN: "down",
            pygame.K_LEFT: "left",
            pygame.K_RIGHT: "right"
        }
        
        for key, name in bindings.items():
            input_comp.bind_key(key, create_action(name))
        
        # Test each binding
        for key in bindings:
            input_comp.handle_keydown(key)
            input_comp.update(1/60)
            input_comp.handle_keyup(key)
        
        assert actions_called == set(bindings.values()), "All bound actions should be called"
    
    def test_key_combinations(self, game, input_entity):
        """Test handling of multiple simultaneous keys."""
        entity, input_comp = input_entity
        
        # Track combination state
        combo_active = False
        def combo_action():
            nonlocal combo_active
            combo_active = True
        
        # Bind combination
        input_comp.bind_key_combination([pygame.K_LSHIFT, pygame.K_SPACE], combo_action)
        
        # Test partial combination
        input_comp.handle_keydown(pygame.K_LSHIFT)
        input_comp.update(1/60)
        assert not combo_active, "Combo should not trigger with partial keys"
        
        # Complete combination
        input_comp.handle_keydown(pygame.K_SPACE)
        input_comp.update(1/60)
        assert combo_active, "Combo should trigger with all keys pressed"
    
    def test_input_priority(self, game, input_entity):
        """Test input handling priority."""
        entity, input_comp = input_entity
        
        # Track action execution order
        execution_order = []
        def create_priority_action(name):
            def action():
                execution_order.append(name)
            return action
        
        # Bind actions with different priorities
        input_comp.bind_key(pygame.K_SPACE, create_priority_action("low"), priority=1)
        input_comp.bind_key(pygame.K_SPACE, create_priority_action("high"), priority=2)
        
        # Trigger actions
        input_comp.handle_keydown(pygame.K_SPACE)
        input_comp.update(1/60)
        
        assert execution_order == ["high", "low"], "Actions should execute in priority order"
    
    def test_input_blocking(self, game, input_entity):
        """Test input blocking functionality."""
        entity, input_comp = input_entity
        
        # Track action execution
        actions_called = set()
        def create_blocking_action(name, should_block=False):
            def action():
                actions_called.add(name)
                return should_block  # Return True to block further processing
            return action
        
        # Bind blocking and non-blocking actions
        input_comp.bind_key(pygame.K_SPACE, create_blocking_action("first", True))
        input_comp.bind_key(pygame.K_SPACE, create_blocking_action("second"))
        
        # Trigger actions
        input_comp.handle_keydown(pygame.K_SPACE)
        input_comp.update(1/60)
        
        assert actions_called == {"first"}, "Blocking action should prevent further execution"
    
    def test_input_state_tracking(self, game, input_entity):
        """Test input state tracking."""
        entity, input_comp = input_entity
        
        # Press multiple keys
        test_keys = [pygame.K_UP, pygame.K_RIGHT, pygame.K_SPACE]
        for key in test_keys:
            input_comp.handle_keydown(key)
        
        # Verify active keys
        for key in test_keys:
            assert input_comp.is_key_pressed(key), f"Key {key} should be marked as pressed"
        
        # Release keys
        for key in test_keys:
            input_comp.handle_keyup(key)
            assert not input_comp.is_key_pressed(key), f"Key {key} should be marked as released"
    
    def test_input_event_propagation(self, game, input_entity):
        """Test input event propagation through the system."""
        entity, input_comp = input_entity
        
        # Track event propagation
        events_received = []
        def event_handler(event):
            events_received.append(event)
        
        # Register handler
        input_comp.add_event_handler(event_handler)
        
        # Create test events
        test_events = [
            pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE}),
            pygame.event.Event(pygame.KEYUP, {'key': pygame.K_SPACE}),
            pygame.event.Event(pygame.MOUSEBUTTONDOWN, {'button': 1}),
        ]
        
        # Process events
        for event in test_events:
            input_comp.handle_event(event)
        
        assert len(events_received) == len(test_events), "All events should be propagated"
        assert all(e1.type == e2.type for e1, e2 in zip(events_received, test_events)), \
            "Events should maintain their types" 