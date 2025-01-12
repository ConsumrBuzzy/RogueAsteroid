"""High score service for managing and persisting high scores."""
from typing import List, Dict, Optional
import json
import os

class HighScoreService:
    """Service for managing high scores.
    
    Provides:
    - High score tracking
    - Score persistence
    - High score validation
    - Score sorting and ranking
    """
    
    def __init__(self, settings_service, event_manager, save_path: str = "data/high_scores.json"):
        """Initialize the high score service.
        
        Args:
            settings_service: Settings service for configuration
            event_manager: Event manager for notifications
            save_path: Path to save high scores file
        """
        self._settings = settings_service
        self._event_manager = event_manager
        self._save_path = save_path
        self._high_scores: List[Dict[str, any]] = []
        self._max_scores = self._settings.get('high_scores.max_entries', 5)
        
        self._ensure_save_directory()
        self.load_scores()
        
        # Subscribe to events
        self._event_manager.subscribe('game_over', self._on_game_over)
        print("HighScoreService initialized")
        
    def _ensure_save_directory(self) -> None:
        """Ensure the save directory exists."""
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        
    def load_scores(self) -> None:
        """Load high scores from file."""
        try:
            if os.path.exists(self._save_path):
                with open(self._save_path, 'r') as f:
                    self._high_scores = json.load(f)
                print("High scores loaded")
            else:
                self._high_scores = []
                print("No high scores file found")
        except Exception as e:
            print(f"Error loading high scores: {e}")
            self._high_scores = []
            
    def save_scores(self) -> None:
        """Save high scores to file."""
        try:
            with open(self._save_path, 'w') as f:
                json.dump(self._high_scores, f)
            print("High scores saved")
        except Exception as e:
            print(f"Error saving high scores: {e}")
            
    def add_score(self, score: int, name: str = "Player") -> bool:
        """Add a new high score.
        
        Args:
            score: Score value
            name: Player name
            
        Returns:
            True if score qualifies as high score
        """
        entry = {
            "name": name,
            "score": score,
        }
        
        # Check if score qualifies
        if len(self._high_scores) < self._max_scores or score > self._high_scores[-1]["score"]:
            self._high_scores.append(entry)
            self._high_scores.sort(key=lambda x: x["score"], reverse=True)
            
            # Trim to max scores
            if len(self._high_scores) > self._max_scores:
                self._high_scores = self._high_scores[:self._max_scores]
                
            self.save_scores()
            self._event_manager.publish('high_score_added', score=score, name=name)
            print(f"Added high score: {score}")
            return True
            
        return False
        
    def get_scores(self) -> List[Dict[str, any]]:
        """Get all high scores.
        
        Returns:
            List of high score entries
        """
        return self._high_scores
        
    def clear_scores(self) -> None:
        """Clear all high scores."""
        self._high_scores = []
        self.save_scores()
        self._event_manager.publish('high_scores_cleared')
        print("High scores cleared")
        
    def is_high_score(self, score: int) -> bool:
        """Check if a score qualifies as a high score.
        
        Args:
            score: Score to check
            
        Returns:
            True if score qualifies
        """
        return (len(self._high_scores) < self._max_scores or 
                score > self._high_scores[-1]["score"])
                
    def get_rank(self, score: int) -> Optional[int]:
        """Get the rank a score would achieve.
        
        Args:
            score: Score to check
            
        Returns:
            Rank position (1-based) or None if doesn't qualify
        """
        for i, entry in enumerate(self._high_scores):
            if score > entry["score"]:
                return i + 1
        if len(self._high_scores) < self._max_scores:
            return len(self._high_scores) + 1
        return None
        
    def _on_game_over(self, **kwargs) -> None:
        """Handle game over event."""
        score = kwargs.get('score', 0)
        if self.is_high_score(score):
            self._event_manager.publish('new_high_score', score=score)
            
    def cleanup(self) -> None:
        """Clean up the service."""
        self.save_scores()
        print("HighScoreService cleaned up") 