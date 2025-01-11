"""Scoring system for tracking points and high scores."""
import json
import os
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime

@dataclass
class ScoreEntry:
    """High score entry with player name and score."""
    name: str
    score: int
    level: int
    date: str

class ScoringSystem:
    """Manages game scoring and high scores."""
    
    def __init__(self, save_file: str = 'highscores.json'):
        """Initialize the scoring system.
        
        Args:
            save_file: Path to the high scores save file
        """
        self.current_score = 0
        self.score_multiplier = 1.0
        self.combo_timer = 0.0
        self.combo_count = 0
        
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
    
    def check_high_score(self) -> bool:
        """Check if current score qualifies as high score."""
        if len(self.high_scores) < 5:  # Changed from 10 to 5
            return True
            
        return self.current_score > min(
            entry.score for entry in self.high_scores
        )
    
    def add_high_score(self, name: str, level: int):
        """Add a new high score entry.
        
        Args:
            name: Player name
            level: Level reached
            
        Raises:
            ValueError: If name is empty or level is not positive
        """
        if not name.strip():
            raise ValueError("Player name cannot be empty")
        if level <= 0:
            raise ValueError("Level must be positive")
            
        print(f"Adding high score: {self.current_score} by {name} (Level {level})")  # Debug info
        
        # Create new entry with current date
        new_entry = ScoreEntry(
            name=name.strip()[:10],  # Limit name length
            score=self.current_score,
            level=level,
            date=datetime.now().strftime("%Y-%m-%d")
        )
        
        # Add to list and sort
        self.high_scores.append(new_entry)
        self.high_scores.sort(key=lambda x: x.score, reverse=True)
        
        # Keep only top 5 scores
        self.high_scores = self.high_scores[:5]
        
        # Save to file
        if not self.save_high_scores():
            print("Warning: Failed to save high scores")  # Debug info
    
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
        data = [
            {
                'name': entry.name,
                'score': entry.score,
                'level': entry.level,
                'date': entry.date
            }
            for entry in self.high_scores
        ]
        
        try:
            # Write to temporary file first
            temp_file = self.save_file + '.tmp'
            with open(temp_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            # Rename temporary file to actual file
            os.replace(temp_file, self.save_file)
            print(f"Saved {len(self.high_scores)} high scores")  # Debug info
            return True
            
        except IOError as e:
            print(f"Error saving high scores: {e}")  # Debug info
            return False
        except Exception as e:
            print(f"Unexpected error saving high scores: {e}")  # Debug info
            return False 