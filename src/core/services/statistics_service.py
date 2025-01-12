"""Statistics service for tracking game metrics and player performance."""
from typing import Dict, List, Any, Optional
import json
import os
from datetime import datetime

class GameSession:
    """Individual game session statistics."""
    def __init__(self, session_id: str):
        """Initialize a game session.
        
        Args:
            session_id: Unique session identifier
        """
        self.session_id = session_id
        self.start_time = datetime.now()
        self.end_time: Optional[datetime] = None
        self.duration: float = 0.0
        self.score: int = 0
        self.asteroids_destroyed: int = 0
        self.shots_fired: int = 0
        self.shots_hit: int = 0
        self.deaths: int = 0
        self.waves_completed: int = 0
        self.accuracy: float = 0.0
        self.highest_wave: int = 0
        
    def end_session(self) -> None:
        """End the game session and calculate final statistics."""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.accuracy = (self.shots_hit / self.shots_fired * 100) if self.shots_fired > 0 else 0.0
        
    def to_dict(self) -> Dict[str, Any]:
        """Convert session to dictionary for saving.
        
        Returns:
            Dictionary representation
        """
        return {
            "session_id": self.session_id,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat() if self.end_time else None,
            "duration": self.duration,
            "score": self.score,
            "asteroids_destroyed": self.asteroids_destroyed,
            "shots_fired": self.shots_fired,
            "shots_hit": self.shots_hit,
            "deaths": self.deaths,
            "waves_completed": self.waves_completed,
            "accuracy": self.accuracy,
            "highest_wave": self.highest_wave
        }
        
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load session from dictionary.
        
        Args:
            data: Dictionary data to load
        """
        self.start_time = datetime.fromisoformat(data["start_time"])
        self.end_time = datetime.fromisoformat(data["end_time"]) if data["end_time"] else None
        self.duration = data["duration"]
        self.score = data["score"]
        self.asteroids_destroyed = data["asteroids_destroyed"]
        self.shots_fired = data["shots_fired"]
        self.shots_hit = data["shots_hit"]
        self.deaths = data["deaths"]
        self.waves_completed = data["waves_completed"]
        self.accuracy = data["accuracy"]
        self.highest_wave = data["highest_wave"]

class StatisticsService:
    """Service for tracking game statistics and metrics.
    
    Provides:
    - Session tracking
    - Performance metrics
    - Historical data
    - Aggregate statistics
    """
    
    def __init__(self, save_path: str = "data/statistics.json"):
        """Initialize the statistics service.
        
        Args:
            save_path: Path to save statistics file
        """
        self._save_path = save_path
        self._sessions: List[GameSession] = []
        self._current_session: Optional[GameSession] = None
        self._ensure_save_directory()
        self.load_statistics()
        print("StatisticsService initialized")
        
    def _ensure_save_directory(self) -> None:
        """Ensure the save directory exists."""
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        
    def start_session(self) -> None:
        """Start a new game session."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_session = GameSession(session_id)
        print(f"Started new session: {session_id}")
        
    def end_session(self) -> None:
        """End the current game session."""
        if self._current_session:
            self._current_session.end_session()
            self._sessions.append(self._current_session)
            self.save_statistics()
            print(f"Ended session: {self._current_session.session_id}")
            self._current_session = None
            
    def update_session(self, **kwargs) -> None:
        """Update current session statistics.
        
        Args:
            **kwargs: Statistics to update
        """
        if self._current_session:
            for key, value in kwargs.items():
                if hasattr(self._current_session, key):
                    setattr(self._current_session, key, value)
                    
    def load_statistics(self) -> None:
        """Load statistics from file."""
        try:
            if os.path.exists(self._save_path):
                with open(self._save_path, 'r') as f:
                    data = json.load(f)
                    for session_data in data:
                        session = GameSession(session_data["session_id"])
                        session.from_dict(session_data)
                        self._sessions.append(session)
                print("Statistics loaded")
            else:
                print("No statistics file found")
        except Exception as e:
            print(f"Error loading statistics: {e}")
            
    def save_statistics(self) -> None:
        """Save statistics to file."""
        try:
            data = [session.to_dict() for session in self._sessions]
            with open(self._save_path, 'w') as f:
                json.dump(data, f, indent=2)
            print("Statistics saved")
        except Exception as e:
            print(f"Error saving statistics: {e}")
            
    def get_total_playtime(self) -> float:
        """Get total playtime across all sessions.
        
        Returns:
            Total playtime in seconds
        """
        return sum(session.duration for session in self._sessions)
        
    def get_average_accuracy(self) -> float:
        """Get average accuracy across all sessions.
        
        Returns:
            Average accuracy percentage
        """
        if not self._sessions:
            return 0.0
        return sum(session.accuracy for session in self._sessions) / len(self._sessions)
        
    def get_total_score(self) -> int:
        """Get total score across all sessions.
        
        Returns:
            Total score
        """
        return sum(session.score for session in self._sessions)
        
    def get_best_session(self) -> Optional[GameSession]:
        """Get session with highest score.
        
        Returns:
            Best session or None if no sessions
        """
        if not self._sessions:
            return None
        return max(self._sessions, key=lambda s: s.score)
        
    def get_session_count(self) -> int:
        """Get total number of sessions.
        
        Returns:
            Number of sessions
        """
        return len(self._sessions)
        
    def clear_statistics(self) -> None:
        """Clear all statistics."""
        self._sessions.clear()
        self.save_statistics()
        print("Statistics cleared") 