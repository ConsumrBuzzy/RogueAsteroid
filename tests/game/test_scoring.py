"""Integration tests for scoring system."""
import pytest
from datetime import datetime

@pytest.mark.game
class TestScoreSystem:
    """Test cases for the scoring system."""
    
    @pytest.fixture(autouse=True)
    def setup_scoring(self, game):
        """Setup fresh scoring system for each test."""
        game.new_game()
        game.scoring.reset_score()
        game.scoring.scores = []  # Clear existing high scores
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
        assert game.scoring.is_high_score()
        
        # Add high score and verify
        player_name = "TEST"
        assert game.scoring.add_score(player_name)
        
        # Verify high score entry
        assert len(game.scoring.scores) == 1
        high_score = game.scoring.scores[0]
        assert high_score.score == test_score
        assert high_score.name == player_name
        assert high_score.date == datetime.now().strftime('%Y-%m-%d')
    
    def test_score_reset(self, game):
        """Test score reset functionality."""
        # Setup test state
        game.scoring.add_points(500)
        
        # Reset and verify
        game.scoring.reset_score()
        assert game.scoring.current_score == 0
    
    def test_high_score_persistence(self, game):
        """Test high score saving and loading."""
        # Setup test data
        test_score = 10000
        player_name = "TEST"
        
        # Add and save high score
        game.scoring.add_points(test_score)
        game.scoring.add_score(player_name)
        
        # Verify persistence
        high_scores = game.scoring.get_scores()
        assert len(high_scores) > 0
        
        top_score = high_scores[0]
        assert top_score.score >= test_score
        assert top_score.name == player_name 