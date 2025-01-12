"""Test suite for scoring system."""
import pytest
import pygame
from src.core.game import Game
from src.core.scoring import ScoringSystem

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.mark.game
class TestScoreSystem:
    """Test cases for the scoring system."""
    
    @pytest.fixture(autouse=True)
    def setup_scoring(self, game):
        """Setup fresh scoring system for each test."""
        game.new_game()
        game.scoring.reset()
        game.scoring.high_scores = []  # Clear existing high scores
        return game.scoring
    
    def test_score_tracking(self, game):
        """Test basic score functionality."""
        initial_score = game.scoring.current_score
        points = [100, 200, 300]
        
        # Add points incrementally
        for points_to_add in points:
            game.scoring.add_points(points_to_add)
            assert game.scoring.current_score == initial_score + sum(points[:points.index(points_to_add) + 1])
    
    def test_high_score_tracking(self, game):
        """Test that adding points correctly updates high score."""
        # Add points and verify score
        test_score = 10000
        game.scoring.add_points(test_score)
        assert game.scoring.current_score == test_score
        
        # Should be a high score since we cleared the list
        assert game.scoring.check_high_score()
        
        # Add high score and verify
        player_name = "TEST"
        player_level = 1
        assert game.scoring.add_high_score(player_name, player_level)
        
        # Verify high score entry
        assert len(game.scoring.high_scores) == 1
        high_score = game.scoring.high_scores[0]
        assert high_score.score == test_score
        assert high_score.name == player_name
        assert high_score.level == player_level
        
    def test_score_reset(self, game):
        """Test score reset functionality."""
        # Setup test state
        game.scoring.add_points(500)
        game.scoring.score_multiplier = 2.0
        
        # Reset and verify
        game.scoring.reset()
        assert game.scoring.current_score == 0
        assert game.scoring.score_multiplier == 1.0
        
    def test_high_score_persistence(self, game):
        """Test high score saving and loading."""
        # Setup test data
        test_score = 10000
        player_name = "TEST"
        player_level = 1
        
        # Add and save high score
        game.scoring.add_points(test_score)
        game.scoring.add_high_score(player_name, player_level)
        
        # Verify persistence
        high_scores = game.scoring.get_high_scores()
        assert len(high_scores) > 0
        
        top_score = high_scores[0]
        assert top_score.score >= test_score
        assert top_score.name == player_name
        assert top_score.level == player_level
        
    def test_score_multiplier(self, game):
        """Test score multiplier functionality."""
        # Setup test multiplier
        test_multiplier = 2.0
        base_points = 100
        
        game.scoring.score_multiplier = test_multiplier
        game.scoring.add_points(base_points)
        
        assert game.scoring.current_score == base_points * test_multiplier
        
    def test_combo_system(self, game):
        """Test combo system functionality."""
        initial_multiplier = game.scoring.score_multiplier
        
        # Build combo
        for _ in range(3):
            game.scoring.add_points(100)
            game.update(0.1)  # Short update to keep combo alive
        
        # Verify combo multiplier increased
        assert game.scoring.score_multiplier > initial_multiplier
        
        # Let combo expire
        game.update(2.0)  # Update longer than combo timer
        assert game.scoring.score_multiplier == initial_multiplier
        
    def test_score_formatting(self, game):
        """Test score formatting for display."""
        test_scores = [
            (0, "000000"),
            (100, "000100"),
            (999999, "999999"),
            (1000000, "999999")  # Test max score capping
        ]
        
        for score, expected in test_scores:
            game.scoring.current_score = score
            assert game.scoring.format_score() == expected 