"""Scoring system for tracking and managing game scores."""
import json
import os
from pathlib import Path

class ScoringSystem:
    def __init__(self, save_file: str = None):
        """Initialize the scoring system.
        
        Args:
            save_file: Optional path to high scores save file
        """
        self.current_score = 0
        self.high_scores = []
        self.save_file = save_file or str(Path(__file__).parent / '../../data/highscores.json')
        print(f"Scoring system initialized with save file: {self.save_file}")
        self._load_high_scores()
        
    def add_points(self, points: int) -> None:
        """Add points to the current score."""
        self.current_score += points
        print(f"Score: {self.current_score}")
        
    def reset(self) -> None:
        """Reset the current score to 0."""
        self.current_score = 0
        
    def is_high_score(self) -> bool:
        """Check if current score qualifies as a high score.
        
        Returns:
            bool: True if current score is a high score
        """
        if len(self.high_scores) < 10:
            return True
        return self.current_score > min(self.high_scores)
        
    def add_high_score(self, score: int) -> None:
        """Add a new high score to the list.
        
        Args:
            score: The score to add
        """
        self.high_scores.append(score)
        self.high_scores.sort(reverse=True)  # Sort in descending order
        if len(self.high_scores) > 10:
            self.high_scores = self.high_scores[:10]  # Keep only top 10
        self.save_high_scores()
        
    def _load_high_scores(self) -> None:
        """Load high scores from file."""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    self.high_scores = json.load(f)
                    # Ensure scores are sorted
                    self.high_scores.sort(reverse=True)
            else:
                print("No high scores file found, starting fresh")
                self.high_scores = []
        except Exception as e:
            print(f"Error loading high scores: {e}")
            self.high_scores = []
            
    def save_high_scores(self) -> None:
        """Save high scores to file."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            
            with open(self.save_file, 'w') as f:
                json.dump(self.high_scores, f)
            print(f"High scores saved: {self.high_scores}")
        except Exception as e:
            print(f"Error saving high scores: {e}") 