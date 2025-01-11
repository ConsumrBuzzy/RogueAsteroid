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
        self.current_score = 0
        self.score_multiplier = 1.0
        self.combo_timer = 0.0
        self.combo_count = 0
        self.save_file = save_file
        self.high_scores: List[ScoreEntry] = []
        self.load_high_scores()
    
    def add_points(self, base_points: int) -> int:
        """Add points to current score with multiplier.
        
        Args:
            base_points: Base points to add before multiplier
            
        Returns:
            Actual points added after multiplier
        """
        points = int(base_points * self.score_multiplier)
        self.current_score += points
        
        # Update combo
        self.combo_count += 1
        self.combo_timer = 2.0  # Reset combo timer
        self.score_multiplier = min(4.0, 1.0 + (self.combo_count * 0.1))
        
        return points
    
    def update(self, dt: float) -> None:
        """Update scoring state."""
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                # Reset combo
                self.combo_count = 0
                self.score_multiplier = 1.0
    
    def get_high_scores(self, limit: int = 10) -> List[ScoreEntry]:
        """Get the top high scores."""
        return sorted(
            self.high_scores,
            key=lambda x: x.score,
            reverse=True
        )[:limit]
    
    def check_high_score(self) -> bool:
        """Check if current score qualifies as high score."""
        if len(self.high_scores) < 10:
            return True
            
        return self.current_score > min(
            entry.score for entry in self.high_scores
        )
    
    def add_high_score(self, name: str, level: int):
        """Add a new high score entry."""
        print(f"Adding high score: {self.current_score} by {name} (Level {level})")  # Debug info
        
        # Create new entry with current date
        new_entry = ScoreEntry(
            name=name,
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
        self.save_high_scores()
        print("High scores updated and saved")  # Debug info
    
    def reset(self) -> None:
        """Reset current score and multiplier."""
        self.current_score = 0
        self.score_multiplier = 1.0
        self.combo_timer = 0.0
        self.combo_count = 0
    
    def load_high_scores(self) -> None:
        """Load high scores from file."""
        if not os.path.exists(self.save_file):
            self.high_scores = []
            return
            
        try:
            with open(self.save_file, 'r') as f:
                data = json.load(f)
                self.high_scores = [
                    ScoreEntry(**entry) for entry in data
                ]
        except (json.JSONDecodeError, FileNotFoundError):
            self.high_scores = []
    
    def save_high_scores(self) -> None:
        """Save high scores to file."""
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
            with open(self.save_file, 'w') as f:
                json.dump(data, f, indent=2)
        except IOError:
            pass  # Silently fail if we can't save 