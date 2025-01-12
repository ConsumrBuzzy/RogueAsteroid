"""Score component for managing game scoring."""
from typing import Dict, Optional, List, Tuple
from .base import Component

class ScoreComponent(Component):
    """Component for managing scoring and high scores.
    
    Provides:
    - Score tracking
    - High score management
    - Score multipliers
    - Score events
    - Persistence support
    """
    
    def __init__(self, entity, max_high_scores: int = 5):
        """Initialize score component.
        
        Args:
            entity: Entity this component belongs to
            max_high_scores: Maximum number of high scores to track
        """
        super().__init__(entity)
        self.current_score = 0
        self.high_scores: List[Tuple[str, int]] = []
        self.max_high_scores = max_high_scores
        self.score_multiplier = 1.0
        self._score_events: Dict[str, int] = {}
        
        print("ScoreComponent initialized")
    
    def add_points(self, points: int, event_type: Optional[str] = None) -> None:
        """Add points to current score.
        
        Args:
            points: Base points to add
            event_type: Optional event type for tracking score sources
        """
        if not self.enabled:
            return
            
        # Apply multiplier to points
        actual_points = int(points * self.score_multiplier)
        self.current_score += actual_points
        
        # Track score event if specified
        if event_type:
            self._score_events[event_type] = self._score_events.get(event_type, 0) + actual_points
            
        print(f"Added {actual_points} points (x{self.score_multiplier} multiplier)")
    
    def set_multiplier(self, multiplier: float) -> None:
        """Set score multiplier.
        
        Args:
            multiplier: New score multiplier (1.0 = normal scoring)
        """
        self.score_multiplier = max(0, multiplier)
        print(f"Score multiplier set to x{self.score_multiplier}")
    
    def reset_score(self) -> None:
        """Reset current score to 0."""
        self.current_score = 0
        self._score_events.clear()
        self.score_multiplier = 1.0
        print("Score reset to 0")
    
    def add_high_score(self, name: str) -> bool:
        """Add current score to high scores if it qualifies.
        
        Args:
            name: Player name for high score entry
            
        Returns:
            True if score was added to high scores
        """
        # Don't add if score is 0
        if self.current_score == 0:
            return False
            
        # Add score and sort descending
        self.high_scores.append((name, self.current_score))
        self.high_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Trim to max size
        if len(self.high_scores) > self.max_high_scores:
            self.high_scores = self.high_scores[:self.max_high_scores]
            
        # Check if score made the cut
        return (name, self.current_score) in self.high_scores
    
    def clear_high_scores(self) -> None:
        """Clear all high scores."""
        self.high_scores.clear()
        print("High scores cleared")
    
    def get_score_breakdown(self) -> Dict[str, int]:
        """Get breakdown of points by event type.
        
        Returns:
            Dictionary mapping event types to total points
        """
        return self._score_events.copy()
    
    def is_high_score(self) -> bool:
        """Check if current score qualifies as high score.
        
        Returns:
            True if current score would make high scores list
        """
        if len(self.high_scores) < self.max_high_scores:
            return True
        return self.current_score > self.high_scores[-1][1]
    
    @property
    def score(self) -> int:
        """Get current score."""
        return self.current_score 