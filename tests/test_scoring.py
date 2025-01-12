"""Test suite for scoring system."""
import pytest
import pygame
from src.core.game import Game
from src.core.scoring import ScoringSystem

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame for all tests."""
    pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    if not pygame.display.get_init():
        pygame.display.init()
    yield
    pygame.quit()

@pytest.fixture
def game():
    """Create a game instance for testing."""
    game = Game()
    yield game
    # Clean up game resources
    if hasattr(game, 'screen'):
        pygame.display.quit()

class TestScoreSystem:
    def test_score_tracking(self, game):
        """Test basic score functionality"""
        initial_score = game.scoring.current_score
        game.scoring.add_points(100)
        assert game.scoring.current_score == initial_score + 100
    
    def test_high_score_tracking(self, game):
        """Test that adding points correctly updates high score."""
        # Start new game and reset scoring
        game.new_game()
        game.scoring.reset()
        
        # Clear existing high scores
        game.scoring.high_scores = []
        
        # Add points and verify score
        game.scoring.add_points(10000)
        assert game.scoring.current_score == 10000
        
        # Should be a high score since we cleared the list
        assert game.scoring.check_high_score()
        
        # Add high score and verify
        assert game.scoring.add_high_score("TEST", 1)
        assert len(game.scoring.high_scores) == 1
        assert game.scoring.high_scores[0].score == 10000
        assert game.scoring.high_scores[0].name == "TEST"
        
    def test_score_reset(self, game):
        """Test score reset functionality"""
        game.scoring.add_points(500)
        game.scoring.reset()
        assert game.scoring.current_score == 0
        assert game.scoring.score_multiplier == 1.0
        
    def test_high_score_persistence(self, game):
        """Test high score saving and loading"""
        game.scoring.add_points(10000)
        name = "TEST"
        level = 1
        game.scoring.add_high_score(name, level)
        high_scores = game.scoring.get_high_scores()
        assert len(high_scores) > 0
        assert high_scores[0].score >= 10000
        assert high_scores[0].name == name
        
    def test_score_multiplier(self, game):
        """Test score multiplier functionality."""
        game.scoring.reset()
        game.scoring.score_multiplier = 2.0
        game.scoring.add_points(100)
        assert game.scoring.current_score == 200
        
    def test_combo_system(self, game):
        """Test combo system functionality."""
        game.scoring.reset()
        initial_multiplier = game.scoring.score_multiplier
        
        # Add points quickly to build combo
        game.scoring.add_points(100)
        game.scoring.add_points(100)
        assert game.scoring.score_multiplier > initial_multiplier
        
        # Wait for combo to expire
        game.update(2.0)  # Update longer than combo timer
        assert game.scoring.score_multiplier == initial_multiplier 