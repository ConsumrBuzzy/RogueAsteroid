"""High score system for tracking and saving scores."""
import os
import json
from typing import List, Dict, Optional
from datetime import datetime

class HighScoreEntry:
    """Individual high score entry."""
    
    def __init__(self, score: int, name: str, date: Optional[str] = None):
        self.score = score
        self.name = name
        self.date = date or datetime.now().strftime('%Y-%m-%d')
    
    def to_dict(self) -> Dict:
        """Convert entry to dictionary for saving."""
        return {
            'score': self.score,
            'name': self.name,
            'date': self.date
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'HighScoreEntry':
        """Create entry from dictionary."""
        return cls(
            score=data['score'],
            name=data['name'],
            date=data['date']
        )

class HighScoreManager:
    """Manages high score tracking and persistence."""
    
    def __init__(self, max_scores: int = 10):
        self.max_scores = max_scores
        self.scores: List[HighScoreEntry] = []
        self.scores_file = os.path.join('data', 'highscores.json')
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        
        # Load existing scores
        self.load_scores()
    
    def add_score(self, score: int, name: str) -> bool:
        """Add a new score and return True if it's a high score."""
        entry = HighScoreEntry(score, name)
        
        # Check if it's a high score
        is_high_score = (
            len(self.scores) < self.max_scores or
            score > min(s.score for s in self.scores)
        )
        
        if is_high_score:
            self.scores.append(entry)
            self.scores.sort(key=lambda x: x.score, reverse=True)
            
            # Trim to max scores
            if len(self.scores) > self.max_scores:
                self.scores = self.scores[:self.max_scores]
            
            # Save updated scores
            self.save_scores()
        
        return is_high_score
    
    def get_scores(self) -> List[HighScoreEntry]:
        """Get list of high scores."""
        return self.scores.copy()
    
    def is_high_score(self, score: int) -> bool:
        """Check if a score would qualify as a high score."""
        return (
            len(self.scores) < self.max_scores or
            score > min(s.score for s in self.scores)
        )
    
    def load_scores(self) -> None:
        """Load scores from file."""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r') as f:
                    data = json.load(f)
                    self.scores = [
                        HighScoreEntry.from_dict(entry)
                        for entry in data
                    ]
                    # Sort scores in case file was modified
                    self.scores.sort(key=lambda x: x.score, reverse=True)
        except (json.JSONDecodeError, KeyError):
            print("Warning: Could not load high scores file")
            self.scores = []
    
    def save_scores(self) -> None:
        """Save scores to file."""
        try:
            with open(self.scores_file, 'w') as f:
                json.dump(
                    [s.to_dict() for s in self.scores],
                    f,
                    indent=2
                )
        except IOError:
            print("Warning: Could not save high scores file")
    
    def clear_scores(self) -> None:
        """Clear all high scores."""
        self.scores.clear()
        self.save_scores() 