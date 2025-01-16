"""
High score system for the ECS game.
"""

import json
import os
from typing import List, Dict, Optional, TYPE_CHECKING
from dataclasses import dataclass, field
from datetime import datetime
from .system import System

if TYPE_CHECKING:
    from .world import World

@dataclass
class HighScore:
    """Individual high score entry."""
    name: str
    score: int
    date: str = field(default_factory=lambda: datetime.now().isoformat())

@dataclass
class HighScoreResource:
    """Resource for managing high scores."""
    scores: List[HighScore] = field(default_factory=list)
    max_scores: int = 10
    filename: str = "highscores.json"

    def add_score(self, name: str, score: int) -> bool:
        """
        Add a new score and return True if it's a high score.
        """
        # Create new score entry
        new_score = HighScore(name=name, score=score)
        
        # Add to list and sort
        self.scores.append(new_score)
        self.scores.sort(key=lambda x: x.score, reverse=True)
        
        # Trim to max scores
        if len(self.scores) > self.max_scores:
            self.scores = self.scores[:self.max_scores]
        
        # Return True if score made the list
        return any(s.score <= score for s in self.scores)
    
    def is_high_score(self, score: int) -> bool:
        """Check if a score qualifies as a high score."""
        if len(self.scores) < self.max_scores:
            return True
        return score > min(s.score for s in self.scores)

class HighScoreSystem(System):
    """System for managing high scores."""
    
    def __init__(self):
        self.save_pending = False
    
    def update(self, world: 'World', dt: float) -> None:
        """Update high score system."""
        if self.save_pending:
            self.save_scores(world)
            self.save_pending = False
    
    def load_scores(self, world: 'World') -> None:
        """Load high scores from file."""
        scores_resource = world.resources.get(HighScoreResource)
        if not scores_resource:
            scores_resource = HighScoreResource()
            world.resources.add(scores_resource)
        
        try:
            if os.path.exists(scores_resource.filename):
                with open(scores_resource.filename, 'r') as f:
                    data = json.load(f)
                    scores_resource.scores = [
                        HighScore(**score_data)
                        for score_data in data['scores']
                    ]
        except Exception as e:
            print(f"Error loading high scores: {e}")
            scores_resource.scores = []
    
    def save_scores(self, world: 'World') -> None:
        """Save high scores to file."""
        scores_resource = world.resources.get(HighScoreResource)
        if not scores_resource:
            return
        
        try:
            data = {
                'scores': [
                    {
                        'name': score.name,
                        'score': score.score,
                        'date': score.date
                    }
                    for score in scores_resource.scores
                ]
            }
            
            with open(scores_resource.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving high scores: {e}")
    
    def add_score(self, world: 'World', name: str, score: int) -> bool:
        """Add a new high score."""
        scores_resource = world.resources.get(HighScoreResource)
        if not scores_resource:
            return False
        
        is_high = scores_resource.add_score(name, score)
        if is_high:
            self.save_pending = True
        return is_high
    
    def is_high_score(self, world: 'World', score: int) -> bool:
        """Check if a score qualifies as a high score."""
        scores_resource = world.resources.get(HighScoreResource)
        if not scores_resource:
            return False
        
        return scores_resource.is_high_score(score)
