"""Achievement service for managing game achievements and progress tracking."""
from typing import Dict, List, Any, Optional, Callable
import json
import os
from enum import Enum, auto

class AchievementStatus(Enum):
    """Achievement status enumeration."""
    LOCKED = auto()
    IN_PROGRESS = auto()
    COMPLETED = auto()

class Achievement:
    """Individual achievement with progress tracking."""
    def __init__(self, 
                 id: str,
                 name: str,
                 description: str,
                 target_value: int = 1,
                 hidden: bool = False):
        """Initialize an achievement.
        
        Args:
            id: Unique achievement identifier
            name: Display name
            description: Achievement description
            target_value: Value needed for completion
            hidden: Whether achievement is hidden until unlocked
        """
        self.id = id
        self.name = name
        self.description = description
        self.target_value = target_value
        self.hidden = hidden
        self.current_value = 0
        self.status = AchievementStatus.LOCKED
        self._callbacks: List[Callable] = []
        
    def update_progress(self, value: int) -> None:
        """Update achievement progress.
        
        Args:
            value: New progress value
        """
        old_status = self.status
        self.current_value = min(value, self.target_value)
        
        if self.current_value > 0 and self.status == AchievementStatus.LOCKED:
            self.status = AchievementStatus.IN_PROGRESS
            
        if self.current_value >= self.target_value:
            self.status = AchievementStatus.COMPLETED
            
        if self.status != old_status:
            self._notify_status_change()
            
    def add_callback(self, callback: Callable) -> None:
        """Add status change callback.
        
        Args:
            callback: Function to call on status change
        """
        self._callbacks.append(callback)
        
    def _notify_status_change(self) -> None:
        """Notify all callbacks of status change."""
        for callback in self._callbacks:
            callback(self)
            
    def to_dict(self) -> Dict[str, Any]:
        """Convert achievement to dictionary for saving.
        
        Returns:
            Dictionary representation
        """
        return {
            "id": self.id,
            "current_value": self.current_value,
            "status": self.status.name
        }
        
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Load achievement from dictionary.
        
        Args:
            data: Dictionary data to load
        """
        self.current_value = data.get("current_value", 0)
        self.status = AchievementStatus[data.get("status", "LOCKED")]

class AchievementService:
    """Service for managing game achievements.
    
    Provides:
    - Achievement tracking
    - Progress persistence
    - Achievement validation
    - Status notifications
    """
    
    def __init__(self, settings_service, event_manager):
        """Initialize the achievement service.
        
        Args:
            settings_service: Settings service for configuration
            event_manager: Event manager for notifications
        """
        self._settings = settings_service
        self._event_manager = event_manager
        self._save_path = self._settings.get('achievements.save_path', "data/achievements.json")
        self._achievements: Dict[str, Achievement] = {}
        
        self._ensure_save_directory()
        self._register_achievements()
        self.load_achievements()
        
        # Subscribe to events
        self._event_manager.subscribe('game_over', self._on_game_over)
        self._event_manager.subscribe('asteroid_destroyed', self._on_asteroid_destroyed)
        self._event_manager.subscribe('wave_completed', self._on_wave_completed)
        self._event_manager.subscribe('player_died', self._on_player_died)
        
        print("AchievementService initialized")
        
    def _ensure_save_directory(self) -> None:
        """Ensure the save directory exists."""
        os.makedirs(os.path.dirname(self._save_path), exist_ok=True)
        
    def _register_achievements(self) -> None:
        """Register all game achievements."""
        self.register_achievement(
            "first_kill",
            "First Blood",
            "Destroy your first asteroid",
            1
        )
        self.register_achievement(
            "sharpshooter",
            "Sharpshooter",
            "Achieve 80% accuracy with 50+ shots",
            1
        )
        self.register_achievement(
            "survivor",
            "Survivor",
            "Survive for 5 minutes",
            300  # seconds
        )
        self.register_achievement(
            "asteroid_master",
            "Asteroid Master",
            "Destroy 1000 asteroids",
            1000
        )
        self.register_achievement(
            "high_scorer",
            "High Scorer",
            "Score 100,000 points",
            100000
        )
        print("Default achievements registered")
        
    def register_achievement(self, id: str, name: str, description: str, target: int, hidden: bool = False) -> None:
        """Register a new achievement.
        
        Args:
            id: Unique achievement identifier
            name: Display name
            description: Achievement description
            target: Target value for completion
            hidden: Whether achievement is hidden until unlocked
        """
        if id not in self._achievements:
            achievement = Achievement(id, name, description, target, hidden)
            achievement.add_callback(self._on_achievement_updated)
            self._achievements[id] = achievement
            print(f"Registered achievement: {name}")
        
    def load_achievements(self) -> None:
        """Load achievements progress from file."""
        try:
            if os.path.exists(self._save_path):
                with open(self._save_path, 'r') as f:
                    data = json.load(f)
                    for achievement_data in data:
                        if achievement := self._achievements.get(achievement_data["id"]):
                            achievement.from_dict(achievement_data)
                print("Achievements progress loaded")
            else:
                print("No achievements file found")
        except Exception as e:
            print(f"Error loading achievements: {e}")
            
    def save_achievements(self) -> None:
        """Save achievements progress to file."""
        try:
            data = [achievement.to_dict() for achievement in self._achievements.values()]
            with open(self._save_path, 'w') as f:
                json.dump(data, f, indent=2)
            print("Achievements progress saved")
        except Exception as e:
            print(f"Error saving achievements: {e}")
            
    def update_achievement(self, id: str, value: int) -> None:
        """Update achievement progress.
        
        Args:
            id: Achievement identifier
            value: New progress value
        """
        if achievement := self._achievements.get(id):
            achievement.update_progress(value)
            self.save_achievements()
            print(f"Updated achievement progress: {id} = {value}")
            
    def get_achievement(self, id: str) -> Optional[Achievement]:
        """Get achievement by ID.
        
        Args:
            id: Achievement identifier
            
        Returns:
            Achievement or None if not found
        """
        return self._achievements.get(id)
        
    def get_all_achievements(self, include_hidden: bool = False) -> List[Achievement]:
        """Get all achievements.
        
        Args:
            include_hidden: Whether to include hidden achievements
            
        Returns:
            List of achievements
        """
        return [a for a in self._achievements.values() 
                if not a.hidden or include_hidden]
                
    def get_completion_percentage(self) -> float:
        """Get overall achievement completion percentage.
        
        Returns:
            Percentage of achievements completed (0-100)
        """
        total = len(self._achievements)
        if total == 0:
            return 0.0
        completed = sum(1 for a in self._achievements.values() 
                       if a.status == AchievementStatus.COMPLETED)
        return (completed / total) * 100
        
    def reset_all_achievements(self) -> None:
        """Reset all achievements progress."""
        for achievement in self._achievements.values():
            achievement.current_value = 0
            achievement.status = AchievementStatus.LOCKED
        self.save_achievements()
        self._event_manager.publish('achievements_reset')
        print("All achievements reset")
        
    def _on_achievement_updated(self, achievement: Achievement) -> None:
        """Handle achievement status change."""
        self._event_manager.publish('achievement_updated', 
                                  id=achievement.id,
                                  status=achievement.status.name,
                                  progress=achievement.current_value)
        
    def _on_game_over(self, **kwargs) -> None:
        """Handle game over event."""
        score = kwargs.get('score', 0)
        self.update_achievement('high_scorer', score)
        
    def _on_asteroid_destroyed(self, **kwargs) -> None:
        """Handle asteroid destroyed event."""
        self.update_achievement('first_kill', 1)
        count = kwargs.get('total_destroyed', 0)
        self.update_achievement('asteroid_master', count)
        
    def _on_wave_completed(self, **kwargs) -> None:
        """Handle wave completed event."""
        wave = kwargs.get('wave', 1)
        if wave >= 10:
            self.update_achievement('wave_master', wave)
            
    def _on_player_died(self, **kwargs) -> None:
        """Handle player death event."""
        survival_time = kwargs.get('survival_time', 0)
        self.update_achievement('survivor', survival_time)
        
    def cleanup(self) -> None:
        """Clean up the service."""
        self.save_achievements()
        print("AchievementService cleaned up") 