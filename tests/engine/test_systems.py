"""Test suite for core game systems."""
import pytest
import pygame
import numpy as np
from src.core.game_state import GameState, StateManager
from src.core.scoring import ScoringSystem
from src.core.game import Game
from src.core.constants import *

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.fixture
def system_setup(game):
    """Setup a fresh game state for system testing."""
    game.new_game()
    return game

@pytest.mark.engine
class TestGameSystems:
    """Test cases for core game systems."""
    
    def test_game_initialization(self, game, system_setup):
        """Test game initialization."""
        # Test screen setup
        assert game.screen is not None, "Game screen should be initialized"
        assert game.width == WINDOW_WIDTH, "Game width should match window width"
        assert game.height == WINDOW_HEIGHT, "Game height should match window height"
        
        # Test system initialization
        assert game.state_manager is not None, "State manager should be initialized"
        assert game.scoring is not None, "Scoring system should be initialized"
        assert game.entities is not None, "Entity system should be initialized"
        
        # Test initial game state
        assert game.level == 1, "Game should start at level 1"
        assert game.lives == STARTING_LIVES, "Game should start with correct lives"
        assert len(game.entities) > 0, "Game should have initial entities"
    
    def test_game_reset(self, game, system_setup):
        """Test game reset functionality."""
        # Setup game state
        game.scoring.add_points(1000)
        game.level = 5
        game.lives = 1
        
        # Reset game
        game.reset_game()
        
        # Verify reset state
        assert game.scoring.current_score == 0, "Score should be reset to 0"
        assert game.level == 1, "Level should be reset to 1"
        assert game.lives == STARTING_LIVES, "Lives should be reset to starting value"
        assert len(game.asteroids) > 0, "New asteroid wave should be spawned"
        
    def test_entity_management(self, game, system_setup):
        """Test entity management system."""
        initial_count = len(game.entities)
        
        # Test entity addition
        test_entity = game.create_entity()
        assert len(game.entities) == initial_count + 1, "Entity should be added to game"
        assert test_entity in game.entities, "Entity should be in entity list"
        
        # Test entity removal
        game.remove_entity(test_entity)
        assert len(game.entities) == initial_count, "Entity should be removed from game"
        assert test_entity not in game.entities, "Entity should not be in entity list"
    
    def test_update_cycle(self, game, system_setup):
        """Test game update cycle."""
        # Track initial state
        initial_positions = {
            entity: entity.get_component('transform').position.copy()
            for entity in game.entities
            if entity.has_component('transform')
        }
        
        # Update game
        dt = 1/60  # One frame at 60 FPS
        game.update(dt)
        
        # Verify entities were updated
        for entity, initial_pos in initial_positions.items():
            if entity in game.entities:  # Entity might have been destroyed
                current_pos = entity.get_component('transform').position
                if entity.has_component('physics'):
                    assert current_pos != initial_pos, f"Entity {entity} should move if it has physics"
    
    def test_system_order(self, game, system_setup):
        """Test that systems are updated in correct order."""
        update_order = []
        
        class TestSystem:
            def __init__(self, name):
                self.name = name
            
            def update(self, dt):
                update_order.append(self.name)
        
        # Add test systems
        game.systems = [
            TestSystem("Physics"),
            TestSystem("Collision"),
            TestSystem("Render")
        ]
        
        # Update game
        game.update(1/60)
        
        # Verify order
        assert update_order == ["Physics", "Collision", "Render"], "Systems should update in correct order"
    
    def test_delta_time(self, game, system_setup):
        """Test that delta time is handled correctly."""
        test_dts = [1/60, 1/30, 1/120]  # Various frame rates
        
        for dt in test_dts:
            # Track initial state
            initial_positions = {
                entity: entity.get_component('transform').position.copy()
                for entity in game.entities
                if entity.has_component('transform') and entity.has_component('physics')
            }
            
            # Update with specific dt
            game.update(dt)
            
            # Verify movement scales with dt
            for entity, initial_pos in initial_positions.items():
                if entity in game.entities:
                    current_pos = entity.get_component('transform').position
                    velocity = entity.get_component('physics').velocity
                    expected_pos = initial_pos + velocity * dt
                    assert (current_pos - expected_pos).length() < 0.1, f"Movement should scale with dt={dt}"
    
    def test_system_pause(self, game, system_setup):
        """Test system behavior when game is paused."""
        # Get initial state
        initial_positions = {
            entity: entity.get_component('transform').position.copy()
            for entity in game.entities
            if entity.has_component('transform')
        }
        
        # Pause and update
        game.pause()
        game.update(1/60)
        
        # Verify no movement during pause
        for entity, initial_pos in initial_positions.items():
            if entity in game.entities:
                current_pos = entity.get_component('transform').position
                assert current_pos == initial_pos, "Entities should not move while paused" 