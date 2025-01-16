"""Scoring system for tracking points and high scores."""
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime

@dataclass
class ScoreEntry:
    """High score entry with player name and score."""
    name: str
    score: int
    level: int
    date: str
    
    def to_dict(self):
        """Convert entry to dictionary for serialization."""
        return asdict(self)

class ScoringSystem:
    """Manages game scoring and high scores."""
    
    def __init__(self, save_file: str = 'highscores.json', max_scores: int = 5):
        """Initialize the scoring system.
        
        Args:
            save_file: Path to the high scores save file
            max_scores: Maximum number of high scores to keep
        """
        self.current_score = 0
        self.score_multiplier = 1.0
        self.combo_timer = 0.0
        self.combo_count = 0
        self.MAX_SCORE = 999999  # Maximum possible score
        self.max_scores = max_scores
        
        # Ensure save file path is absolute
        if not os.path.isabs(save_file):
            save_file = os.path.join(os.path.dirname(__file__), '..', '..', 'data', save_file)
        self.save_file = save_file
        
        # Ensure data directory exists
        os.makedirs(os.path.dirname(self.save_file), exist_ok=True)
        
        self.high_scores: List[ScoreEntry] = []
        self.load_high_scores()
        print(f"Scoring system initialized with save file: {self.save_file}")  # Debug info
    
    def add_points(self, base_points: int) -> int:
        """Add points to current score with multiplier.
        
        Args:
            base_points: Base points to add before multiplier
            
        Returns:
            Actual points added after multiplier
            
        Raises:
            ValueError: If base_points is negative
        """
        if base_points < 0:
            raise ValueError("Cannot add negative points")
            
        points = int(base_points * self.score_multiplier)
        
        # Check if adding points would exceed max score
        if self.current_score + points > self.MAX_SCORE:
            points = self.MAX_SCORE - self.current_score
            self.current_score = self.MAX_SCORE
            print(f"Score capped at maximum: {self.MAX_SCORE}")  # Debug info
            return points
            
        self.current_score += points
        
        # Update combo
        self.combo_count += 1
        self.combo_timer = 2.0  # Reset combo timer
        self.score_multiplier = min(4.0, 1.0 + (self.combo_count * 0.1))
        
        print(f"Added {points} points (base: {base_points}, multiplier: {self.score_multiplier:.1f})")  # Debug info
        return points
    
    def update(self, dt: float) -> None:
        """Update scoring state.
        
        Args:
            dt: Time delta in seconds
            
        Raises:
            ValueError: If dt is negative
        """
        if dt < 0:
            raise ValueError("Time delta cannot be negative")
            
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                # Reset combo
                self.combo_count = 0
                self.score_multiplier = 1.0
                print("Combo reset")  # Debug info
    
    def get_high_scores(self, limit: int = 10) -> List[ScoreEntry]:
        """Get the top high scores.
        
        Args:
            limit: Maximum number of scores to return
            
        Returns:
            List of high score entries
            
        Raises:
            ValueError: If limit is not positive
        """
        if limit <= 0:
            raise ValueError("Score limit must be positive")
            
        return sorted(
            self.high_scores,
            key=lambda x: x.score,
            reverse=True
        )[:limit]
    
    def get_lowest_high_score(self):
        """Get the lowest score from the high scores list."""
        if not self.high_scores:
            return 0
        return min(score.score for score in self.high_scores)
    
    def is_high_score(self, score):
        """Check if a score qualifies as a high score."""
        if len(self.high_scores) < self.max_scores:
            return True
        return score > self.get_lowest_high_score()
    
    def add_high_score(self, name: str, level: int) -> bool:
        """Add a new high score entry.
        
        Args:
            name: Player name
            level: Level reached
            
        Returns:
            bool: True if score was added, False if it wasn't high enough
            
        Raises:
            ValueError: If name is empty or level is invalid
        """
        if not name.strip():
            raise ValueError("Player name cannot be empty")
        if level < 1:
            raise ValueError("Level must be positive")
            
        # Create new score entry
        new_score = ScoreEntry(
            name=name.strip()[:10],  # Limit name length
            score=self.current_score,
            level=level,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Add to list and sort
        self.high_scores.append(new_score)
        self.high_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Keep only top scores
        self.high_scores = self.high_scores[:self.max_scores]
        
        # Save updated scores
        return self.save_high_scores()
    
    def reset(self) -> None:
        """Reset current score and multiplier."""
        self.current_score = 0
        self.score_multiplier = 1.0
        self.combo_timer = 0.0
        self.combo_count = 0
        print("Score system reset")  # Debug info
    
    def load_high_scores(self) -> None:
        """Load high scores from file."""
        if not os.path.exists(self.save_file):
            print(f"No high scores file found at: {self.save_file}")  # Debug info
            self.high_scores = []
            return
            
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                self.high_scores = [
                    ScoreEntry(**entry) for entry in data
                ]
            print(f"Loaded {len(self.high_scores)} high scores")  # Debug info
        except json.JSONDecodeError as e:
            print(f"Error decoding high scores file: {e}")  # Debug info
            self.high_scores = []
        except FileNotFoundError:
            print(f"High scores file not found: {self.save_file}")  # Debug info
            self.high_scores = []
        except Exception as e:
            print(f"Unexpected error loading high scores: {e}")  # Debug info
            self.high_scores = []
    
    def save_high_scores(self) -> bool:
        """Save high scores to file.
        
        Returns:
            bool: True if save was successful, False otherwise
        """
        try:
            # Create a temporary file
            temp_file = self.save_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump([score.to_dict() for score in self.high_scores], f)
            
            # Rename temp file to actual file
            os.replace(temp_file, self.save_file)
            print(f"High scores saved successfully to {self.save_file}")  # Debug info
            return True
        except Exception as e:
            print(f"Error saving high scores: {e}")  # Debug info
            return False 