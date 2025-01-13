"""Scoring system for tracking and managing game scores."""
import json
import os
from pathlib import Path
from typing import List, Tuple
from src.core.logging import get_logger

class ScoringSystem:
    def __init__(self, save_file: str = None):
        """Initialize the scoring system.
        
        Args:
            save_file: Optional path to high scores save file
        """
        self.logger = get_logger()
        self.current_score = 0
        self.high_scores: List[Tuple[str, int]] = []  # List of (name, score) tuples
        self.save_file = save_file or str(Path(__file__).parent / '../../data/highscores.json')
        self.logger.info(f"Scoring system initialized with save file: {self.save_file}")
        self._load_high_scores()
        
    def add_points(self, points: int) -> None:
        """Add points to the current score."""
        self.current_score += points
        self.logger.debug(f"Score updated: {self.current_score} (+{points})")
        
    def reset(self) -> None:
        """Reset the current score to 0."""
        old_score = self.current_score
        self.current_score = 0
        self.logger.debug(f"Score reset from {old_score} to 0")
        
    def is_high_score(self, score: int = None) -> bool:
        """Check if score qualifies as a high score.
        
        Args:
            score: Score to check. If None, uses current_score.
        """
        score = score if score is not None else self.current_score
        
        # If we have fewer than 10 scores, any score is a high score
        if len(self.high_scores) < 10:
            self.logger.info(f"New high score {score} (fewer than 10 scores)")
            return True
            
        # Otherwise, check if score beats the lowest high score
        lowest_high_score = min(score for _, score in self.high_scores) if self.high_scores else 0
        is_high = score > lowest_high_score
        if is_high:
            self.logger.info(f"New high score {score} (beats {lowest_high_score})")
        return is_high
        
    def add_high_score(self, name: str, score: int = None) -> None:
        """Add a new high score to the list.
        
        Args:
            name: Player name
            score: Score to add. If None, uses current_score.
        """
        score = score if score is not None else self.current_score
        self.high_scores.append((name, score))
        # Sort by score in descending order
        self.high_scores.sort(key=lambda x: x[1], reverse=True)
        if len(self.high_scores) > 10:
            self.high_scores = self.high_scores[:10]  # Keep only top 10
        self.logger.info(f"Added high score: {name} - {score}")
        self.save_high_scores()
        
    def get_scores(self) -> List[Tuple[str, int]]:
        """Get list of high scores.
        
        Returns:
            List of (name, score) tuples, sorted by score descending.
        """
        return self.high_scores
        
    def _load_high_scores(self) -> None:
        """Load high scores from file."""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    # Convert to list of tuples if old format
                    if isinstance(data, list) and (not data or isinstance(data[0], (int, float))):
                        self.high_scores = [("???", score) for score in data]
                    else:
                        self.high_scores = data
                    # Ensure scores are sorted
                    self.high_scores.sort(key=lambda x: x[1], reverse=True)
                    self.logger.info(f"Loaded {len(self.high_scores)} high scores")
            else:
                self.logger.info("No high scores file found, starting fresh")
                self.high_scores = []
        except Exception as e:
            self.logger.error(f"Error loading high scores: {e}")
            self.high_scores = []
            
    def save_high_scores(self) -> None:
        """Save high scores to file."""
        try:
            # Ensure data directory exists
            os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
            
            with open(self.save_file, 'w') as f:
                json.dump(self.high_scores, f)
            self.logger.debug(f"High scores saved: {self.high_scores}")
        except Exception as e:
            self.logger.error(f"Error saving high scores: {e}") 