"""High score service for tracking and saving scores."""
import os
import json
from typing import List, Dict, Optional
from datetime import datetime
from src.core.logging import get_logger

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
        self.logger = get_logger()
        self.max_scores = max_scores
        self.scores: List[HighScoreEntry] = []
        self.scores_file = os.path.join('data', 'highscores.json')
        self.current_score = 0  # Track current game score
        
        # Create data directory if it doesn't exist
        os.makedirs('data', exist_ok=True)
        self.logger.debug("Ensured data directory exists")
        
        # Load existing scores
        self.load_scores()
        self.logger.info(f"High score manager initialized with {len(self.scores)} scores")
    
    def add_points(self, points: int) -> None:
        """Add points to the current score."""
        self.current_score += points
        self.logger.debug(f"Score updated: {self.current_score} (+{points})")
    
    def reset_score(self) -> None:
        """Reset the current score to 0."""
        old_score = self.current_score
        self.current_score = 0
        self.logger.debug(f"Score reset from {old_score} to 0")
    
    def add_score(self, name: str, score: Optional[int] = None) -> bool:
        """Add a new score and return True if it's a high score.
        
        Args:
            name: Player name
            score: Score to add. If None, uses current_score.
        """
        score = score if score is not None else self.current_score
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
            self.logger.info(f"Added high score: {name} - {score} ({entry.date})")
        else:
            self.logger.debug(f"Score not high enough: {name} - {score}")
        
        return is_high_score
    
    def get_scores(self) -> List[HighScoreEntry]:
        """Get list of high scores."""
        return self.scores.copy()
    
    def is_high_score(self, score: Optional[int] = None) -> bool:
        """Check if a score would qualify as a high score.
        
        Args:
            score: Score to check. If None, uses current_score.
        """
        score = score if score is not None else self.current_score
        
        if len(self.scores) < self.max_scores:
            self.logger.debug(f"Score {score} qualifies (fewer than {self.max_scores} scores)")
            return True
        min_score = min(s.score for s in self.scores)
        is_high = score > min_score
        if is_high:
            self.logger.debug(f"Score {score} qualifies (beats lowest score {min_score})")
        return is_high
    
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
                    self.logger.info(f"Loaded {len(self.scores)} high scores from {self.scores_file}")
            else:
                self.logger.info(f"No high scores file found at {self.scores_file}")
                self.scores = []
        except (json.JSONDecodeError, KeyError) as e:
            self.logger.error(f"Could not load high scores file: {e}")
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
            self.logger.debug(f"Saved {len(self.scores)} high scores to {self.scores_file}")
        except IOError as e:
            self.logger.error(f"Could not save high scores file: {e}")
    
    def clear_scores(self) -> None:
        """Clear all high scores."""
        count = len(self.scores)
        self.scores.clear()
        self.save_scores()
        self.logger.info(f"Cleared {count} high scores")
    
    def add_high_score(self, player_name: str) -> None:
        """Add a new high score entry."""
        self.logger.info(f"Adding high score: {self.current_score} by {player_name}")
        # Create new score entry
        new_score = {
            'name': player_name,
            'score': self.current_score,
            'date': datetime.now().strftime('%Y-%m-%d %H:%M')
        }
        
        # Add to list and sort
        self.high_scores.append(new_score)
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        
        # Keep only top 10
        self.high_scores = self.high_scores[:10]
        
        # Save to file
        self.save_scores()
        self.logger.info("High score saved successfully") 