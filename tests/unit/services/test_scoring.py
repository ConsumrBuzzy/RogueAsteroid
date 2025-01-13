"""Unit tests for scoring system."""
import pytest
from datetime import datetime
from src.core.services.highscores import HighScoreManager, HighScoreEntry

@pytest.fixture
def scoring_system(tmp_path):
    """Create a scoring system instance for testing."""
    # Use a temporary file for testing
    save_file = tmp_path / "test_highscores.json"
    return HighScoreManager(max_scores=10)

@pytest.mark.unit
@pytest.mark.services
class TestHighScoreManager:
    """Test cases for the high score manager."""
    
    def test_score_tracking(self, scoring_system):
        """Test basic score functionality."""
        initial_score = scoring_system.current_score
        points = [100, 200, 300]
        
        # Add points incrementally
        total = 0
        for points_to_add in points:
            total += points_to_add
            scoring_system.add_points(points_to_add)
            assert scoring_system.current_score == total
    
    def test_high_score_tracking(self, scoring_system):
        """Test high score functionality."""
        # Add points and verify score
        test_score = 10000
        scoring_system.add_points(test_score)
        assert scoring_system.current_score == test_score
        
        # Should be a high score since list is empty
        assert scoring_system.is_high_score()
        
        # Add high score and verify
        player_name = "TEST"
        assert scoring_system.add_score(player_name)
        
        # Verify score was added
        scores = scoring_system.get_scores()
        assert len(scores) == 1
        assert scores[0].name == player_name
        assert scores[0].score == test_score
        assert scores[0].date == datetime.now().strftime('%Y-%m-%d')
    
    def test_score_reset(self, scoring_system):
        """Test score reset functionality."""
        # Add some points
        scoring_system.add_points(1000)
        assert scoring_system.current_score > 0
        
        # Reset and verify
        scoring_system.reset_score()
        assert scoring_system.current_score == 0
    
    def test_high_score_persistence(self, scoring_system):
        """Test saving and loading high scores."""
        # Add some high scores
        scores = [
            (1000, "Player1"),
            (2000, "Player2"),
            (3000, "Player3")
        ]
        
        for score, name in scores:
            scoring_system.current_score = score
            scoring_system.add_score(name)
        
        # Save and create new instance
        scoring_system.save_scores()
        new_system = HighScoreManager()
        new_system.scores_file = scoring_system.scores_file
        new_system.load_scores()
        
        # Verify loaded scores
        loaded_scores = new_system.get_scores()
        assert len(loaded_scores) == len(scores)
        for i, (score, name) in enumerate(reversed(scores)):  # Reversed because highest scores first
            assert loaded_scores[i].score == score
            assert loaded_scores[i].name == name
    
    def test_high_score_entry(self):
        """Test HighScoreEntry class."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        entry = HighScoreEntry(1000, "Player", date_str)
        
        # Test to_dict
        entry_dict = entry.to_dict()
        assert entry_dict['name'] == "Player"
        assert entry_dict['score'] == 1000
        assert entry_dict['date'] == date_str
        
        # Test from_dict
        new_entry = HighScoreEntry.from_dict(entry_dict)
        assert new_entry.name == entry.name
        assert new_entry.score == entry.score
        assert new_entry.date == entry.date 