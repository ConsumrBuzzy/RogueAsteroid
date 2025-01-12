"""Timer component for managing time-based events."""
from typing import Dict, Optional, Callable, Any
from .base import Component

class Timer:
    """Individual timer for tracking cooldowns and events."""
    
    def __init__(self, duration: float, callback: Optional[Callable] = None,
                 repeat: bool = False, auto_start: bool = True):
        """Initialize timer.
        
        Args:
            duration: Timer duration in seconds
            callback: Optional function to call when timer completes
            repeat: Whether timer should automatically restart
            auto_start: Whether timer should start immediately
        """
        self.duration = duration
        self.time_left = duration if auto_start else 0
        self.callback = callback
        self.repeat = repeat
        self.running = auto_start
        self.completed = False
    
    def update(self, dt: float) -> bool:
        """Update timer state.
        
        Args:
            dt: Delta time in seconds
            
        Returns:
            True if timer completed this update
        """
        if not self.running or self.completed:
            return False
            
        self.time_left = max(0, self.time_left - dt)
        
        if self.time_left <= 0:
            self.completed = True
            if self.repeat:
                self.reset()
            if self.callback:
                self.callback()
            return True
            
        return False
    
    def start(self) -> None:
        """Start or resume the timer."""
        if not self.running:
            self.running = True
            self.completed = False
    
    def stop(self) -> None:
        """Stop the timer."""
        self.running = False
    
    def reset(self) -> None:
        """Reset timer to initial duration."""
        self.time_left = self.duration
        self.completed = False
        self.running = True
    
    @property
    def progress(self) -> float:
        """Get timer progress as percentage (0-1)."""
        return 1 - (self.time_left / self.duration) if self.duration > 0 else 1

class TimerComponent(Component):
    """Component for managing multiple timers and cooldowns.
    
    Provides:
    - Multiple timer tracking
    - Cooldown management
    - Event scheduling
    - Timer controls
    - Progress tracking
    """
    
    def __init__(self, entity):
        """Initialize timer component.
        
        Args:
            entity: Entity this component belongs to
        """
        super().__init__(entity)
        self._timers: Dict[str, Timer] = {}
        
        print("TimerComponent initialized")
    
    def update(self, dt: float) -> None:
        """Update all active timers.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return
            
        # Update all timers and track completed ones
        completed = []
        for name, timer in self._timers.items():
            if timer.update(dt):
                completed.append(name)
                
        # Remove non-repeating completed timers
        for name in completed:
            if not self._timers[name].repeat:
                del self._timers[name]
    
    def add_timer(self, name: str, duration: float, callback: Optional[Callable] = None,
                 repeat: bool = False, auto_start: bool = True) -> None:
        """Add a new timer.
        
        Args:
            name: Unique name for the timer
            duration: Timer duration in seconds
            callback: Optional function to call when timer completes
            repeat: Whether timer should automatically restart
            auto_start: Whether timer should start immediately
        """
        if name in self._timers:
            print(f"Warning: Overwriting existing timer '{name}'")
            
        self._timers[name] = Timer(duration, callback, repeat, auto_start)
        print(f"Added timer '{name}' with duration {duration}s")
    
    def remove_timer(self, name: str) -> None:
        """Remove a timer.
        
        Args:
            name: Name of timer to remove
        """
        if name in self._timers:
            del self._timers[name]
            print(f"Removed timer '{name}'")
    
    def start_timer(self, name: str) -> None:
        """Start or resume a timer.
        
        Args:
            name: Name of timer to start
        """
        if name in self._timers:
            self._timers[name].start()
    
    def stop_timer(self, name: str) -> None:
        """Stop a timer.
        
        Args:
            name: Name of timer to stop
        """
        if name in self._timers:
            self._timers[name].stop()
    
    def reset_timer(self, name: str) -> None:
        """Reset a timer to its initial duration.
        
        Args:
            name: Name of timer to reset
        """
        if name in self._timers:
            self._timers[name].reset()
    
    def get_progress(self, name: str) -> Optional[float]:
        """Get progress of a timer as percentage.
        
        Args:
            name: Name of timer to check
            
        Returns:
            Progress as percentage (0-1) or None if timer doesn't exist
        """
        return self._timers[name].progress if name in self._timers else None
    
    def is_running(self, name: str) -> bool:
        """Check if a timer is currently running.
        
        Args:
            name: Name of timer to check
            
        Returns:
            True if timer exists and is running
        """
        return name in self._timers and self._timers[name].running
    
    def is_completed(self, name: str) -> bool:
        """Check if a timer has completed.
        
        Args:
            name: Name of timer to check
            
        Returns:
            True if timer exists and has completed
        """
        return name in self._timers and self._timers[name].completed 