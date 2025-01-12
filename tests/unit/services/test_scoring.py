"""Unit tests for scoring service."""
import pytest
from datetime import datetime
from src.core.services.scoring import ScoringSystem, ScoreEntry

@pytest.fixture
def scoring_system(tmp_path):
    """Create a scoring system instance for testing."""
    save_file = tmp_path / "test_scores.json"
    system = ScoringSystem(str(save_file))
    return system

@pytest.mark.unit
@pytest.mark.services
class TestScoringSystem:
    """Test cases for the scoring system service."""
    
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
        assert scoring_system.check_high_score()
        
        # Add high score and verify
        player_name = "TEST"
        player_level = 1
        assert scoring_system.add_high_score(player_name, player_level)
        
        # Verify score was added
        scores = scoring_system.get_high_scores()
        assert len(scores) == 1
        assert scores[0].name == player_name
        assert scores[0].score == test_score
        assert scores[0].level == player_level
    
    def test_score_reset(self, scoring_system):
        """Test score reset functionality."""
        # Add some points
        scoring_system.add_points(1000)
        assert scoring_system.current_score > 0
        
        # Reset and verify
        scoring_system.reset()
        assert scoring_system.current_score == 0
        assert scoring_system.score_multiplier == 1.0
        assert scoring_system.combo_count == 0
        assert scoring_system.combo_timer == 0.0
    
    def test_high_score_persistence(self, scoring_system):
        """Test saving and loading high scores."""
        # Add some high scores
        scores = [
            (1000, "Player1", 1),
            (2000, "Player2", 2),
            (3000, "Player3", 3)
        ]
        
        for score, name, level in scores:
            scoring_system.current_score = score
            scoring_system.add_high_score(name, level)
        
        # Save and create new instance
        scoring_system.save_high_scores()
        new_system = ScoringSystem(scoring_system.save_file)
        
        # Verify loaded scores
        loaded_scores = new_system.get_high_scores()
        assert len(loaded_scores) == len(scores)
        for i, (score, name, level) in enumerate(reversed(scores)):  # Reversed because highest scores first
            assert loaded_scores[i].score == score
            assert loaded_scores[i].name == name
            assert loaded_scores[i].level == level
    
    def test_score_multiplier(self, scoring_system):
        """Test score multiplier mechanics."""
        base_points = 100
        
        # Test different combo levels
        combos_and_multipliers = [
            (2, 1.0),   # Below first threshold
            (3, 1.5),   # First threshold
            (5, 2.0),   # Second threshold
            (10, 4.0),  # Max threshold
        ]
        
        for combo_count, expected_multiplier in combos_and_multipliers:
            scoring_system.reset()
            for _ in range(combo_count):
                scoring_system.add_points(base_points)
            assert scoring_system.score_multiplier == expected_multiplier
    
    def test_combo_system(self, scoring_system):
        """Test combo system mechanics."""
        # Build up combo
        scoring_system.add_points(100)
        assert scoring_system.combo_count == 1
        assert scoring_system.combo_timer > 0
        
        # Let combo timer expire
        scoring_system.update(2.1)  # Just over combo timer
        assert scoring_system.combo_count == 0
        assert scoring_system.score_multiplier == 1.0
        
        # Test combo maintenance
        scoring_system.add_points(100)
        initial_timer = scoring_system.combo_timer
        scoring_system.update(1.0)  # Update but don't expire
        assert scoring_system.combo_timer == initial_timer - 1.0
        scoring_system.add_points(100)  # Should reset timer
        assert scoring_system.combo_timer == 2.0
    
    def test_max_score_limit(self, scoring_system):
        """Test that score cannot exceed maximum."""
        scoring_system.add_points(scoring_system.MAX_SCORE + 1000)
        assert scoring_system.current_score == scoring_system.MAX_SCORE
    
    def test_high_score_entry(self):
        """Test ScoreEntry data class."""
        date_str = datetime.now().strftime('%Y-%m-%d')
        entry = ScoreEntry("Player", 1000, 5, date_str)
        
        # Test to_dict
        entry_dict = entry.to_dict()
        assert entry_dict['name'] == "Player"
        assert entry_dict['score'] == 1000
        assert entry_dict['level'] == 5
        assert entry_dict['date'] == date_str 