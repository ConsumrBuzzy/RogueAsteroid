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
    
    def __init__(self, settings_service, event_manager):
        """Initialize the statistics service.
        
        Args:
            settings_service: Settings service for configuration
            event_manager: Event manager for notifications
        """
        self._settings = settings_service
        self._event_manager = event_manager
        self._save_path = self._settings.get('statistics.save_path', "data/statistics.json")
        self._sessions: List[GameSession] = []
        self._current_session: Optional[GameSession] = None
        
        self._ensure_save_directory()
        self.load_statistics()
        
        # Subscribe to events
        self._event_manager.subscribe('game_start', self._on_game_start)
        self._event_manager.subscribe('game_over', self._on_game_over)
        self._event_manager.subscribe('asteroid_destroyed', self._on_asteroid_destroyed)
        self._event_manager.subscribe('player_shot', self._on_player_shot)
        self._event_manager.subscribe('player_died', self._on_player_died)
        self._event_manager.subscribe('wave_completed', self._on_wave_completed)
        
        print("StatisticsService initialized")
        
    def _ensure_save_directory(self) -> None:
        """Ensure the save directory exists."""
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        
    def start_session(self) -> None:
        """Start a new game session."""
        session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self._current_session = GameSession(session_id)
        self._event_manager.publish('session_started', session_id=session_id)
        print(f"Started new session: {session_id}")
        
    def end_session(self) -> None:
        """End the current game session."""
        if self._current_session:
            self._current_session.end_session()
            self._sessions.append(self._current_session)
            self._event_manager.publish('session_ended', 
                                      session_id=self._current_session.session_id,
                                      stats=self._current_session.to_dict())
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
        self._event_manager.publish('statistics_cleared')
        print("Statistics cleared")
        
    def _on_game_start(self, **kwargs) -> None:
        """Handle game start event."""
        self.start_session()
        
    def _on_game_over(self, **kwargs) -> None:
        """Handle game over event."""
        if self._current_session:
            self._current_session.score = kwargs.get('score', 0)
            self.end_session()
            
    def _on_asteroid_destroyed(self, **kwargs) -> None:
        """Handle asteroid destroyed event."""
        if self._current_session:
            self._current_session.asteroids_destroyed += 1
            self._current_session.shots_hit += 1
            
    def _on_player_shot(self, **kwargs) -> None:
        """Handle player shot event."""
        if self._current_session:
            self._current_session.shots_fired += 1
            
    def _on_player_died(self, **kwargs) -> None:
        """Handle player death event."""
        if self._current_session:
            self._current_session.deaths += 1
            
    def _on_wave_completed(self, **kwargs) -> None:
        """Handle wave completed event."""
        if self._current_session:
            wave = kwargs.get('wave', 1)
            self._current_session.waves_completed += 1
            self._current_session.highest_wave = max(wave, self._current_session.highest_wave)
            
    def cleanup(self) -> None:
        """Clean up the service."""
        if self._current_session:
            self.end_session()
        self.save_statistics()
        print("StatisticsService cleaned up") 