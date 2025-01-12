"""Scoring service for tracking points and high scores."""
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
    
    def __init__(self, save_file: str = 'highscores.json'):
        """Initialize the scoring system.
        
        Args:
            save_file: Path to the high scores save file
        """
        self.current_score = 0
        self.score_multiplier = 1.0
        self.combo_timer = 0.0
        self.combo_count = 0
        self.MAX_SCORE = 999999  # Maximum possible score
        
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
            Total points added after multiplier
        """
        points = int(base_points * self.score_multiplier)
        self.current_score = min(self.current_score + points, self.MAX_SCORE)
        
        # Increase combo
        self.combo_count += 1
        self.combo_timer = 2.0  # Reset combo timer
        
        # Update multiplier based on combo
        if self.combo_count >= 10:
            self.score_multiplier = 4.0
        elif self.combo_count >= 5:
            self.score_multiplier = 2.0
        elif self.combo_count >= 3:
            self.score_multiplier = 1.5
        
        return points
    
    def update(self, dt: float) -> None:
        """Update scoring system state.
        
        Args:
            dt: Time delta in seconds
        """
        # Update combo timer
        if self.combo_timer > 0:
            self.combo_timer -= dt
            if self.combo_timer <= 0:
                # Reset combo
                self.combo_count = 0
                self.score_multiplier = 1.0
    
    def get_high_scores(self, limit: int = 10) -> List[ScoreEntry]:
        """Get list of high scores.
        
        Args:
            limit: Maximum number of scores to return
            
        Returns:
            List of high score entries, sorted by score
        """
        # Sort by score and return limited number
        sorted_scores = sorted(
            self.high_scores,
            key=lambda x: x.score,
            reverse=True
        )
        return sorted_scores[:limit]
    
    def check_high_score(self) -> bool:
        """Check if current score qualifies as a high score.
        
        Returns:
            True if current score is a high score
        """
        if len(self.high_scores) < 10:
            return True
        return self.current_score > min(s.score for s in self.high_scores)
    
    def add_high_score(self, name: str, level: int) -> bool:
        """Add current score as a high score.
        
        Args:
            name: Player name
            level: Level reached
            
        Returns:
            True if score was added as a high score
        """
        if not self.check_high_score():
            return False
        
        # Create new entry
        entry = ScoreEntry(
            name=name,
            score=self.current_score,
            level=level,
            date=datetime.now().strftime('%Y-%m-%d')
        )
        
        # Add to list
        self.high_scores.append(entry)
        
        # Sort and trim to top 10
        self.high_scores.sort(key=lambda x: x.score, reverse=True)
        if len(self.high_scores) > 10:
            self.high_scores = self.high_scores[:10]
        
        # Save to file
        self.save_high_scores()
        return True
    
    def reset(self) -> None:
        """Reset current score and multiplier."""
        self.current_score = 0
        self.score_multiplier = 1.0
        self.combo_count = 0
        self.combo_timer = 0.0
    
    def load_high_scores(self) -> None:
        """Load high scores from save file."""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r') as f:
                    data = json.load(f)
                    self.high_scores = [
                        ScoreEntry(**entry)
                        for entry in data
                    ]
                print(f"Loaded {len(self.high_scores)} high scores")  # Debug info
            else:
                print("No high scores file found, starting fresh")  # Debug info
        except (json.JSONDecodeError, KeyError) as e:
            print(f"Error loading high scores: {e}")  # Debug info
            self.high_scores = []
    
    def save_high_scores(self) -> bool:
        """Save high scores to file.
        
        Returns:
            True if save was successful
        """
        try:
            with open(self.save_file, 'w') as f:
                json.dump(
                    [entry.to_dict() for entry in self.high_scores],
                    f,
                    indent=2
                )
            print(f"Saved {len(self.high_scores)} high scores")  # Debug info
            return True
        except IOError as e:
            print(f"Error saving high scores: {e}")  # Debug info
            return False 