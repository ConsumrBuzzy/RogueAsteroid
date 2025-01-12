"""Wave component for managing game progression and difficulty."""
from typing import Dict, Optional, Callable
from .component import Component

class WaveComponent(Component):
    """Component for managing game waves and difficulty progression.
    
    Provides:
    - Wave progression
    - Difficulty scaling
    - Wave completion tracking
    - Wave callbacks
    - Score multiplier integration
    """
    
    def __init__(self, entity, starting_wave: int = 1,
                 difficulty_multiplier: float = 1.2):
        """Initialize wave component.
        
        Args:
            entity: Entity this component belongs to
            starting_wave: Initial wave number
            difficulty_multiplier: Factor to increase difficulty each wave
        """
        super().__init__(entity)
        self.current_wave = starting_wave
        self.difficulty_multiplier = difficulty_multiplier
        self.enemies_remaining = 0
        self.wave_complete = False
        self._wave_callbacks: Dict[str, Callable] = {}
        
        print(f"WaveComponent initialized at wave {starting_wave}")
    
    def start_wave(self) -> None:
        """Start the current wave."""
        if not self.enabled:
            return
            
        self.wave_complete = False
        
        # Calculate difficulty-scaled values for this wave
        base_enemies = 4 + (self.current_wave - 1) * 2
        self.enemies_remaining = min(base_enemies, 12)  # Cap at 12 enemies
        
        # Calculate score multiplier based on wave
        score_multiplier = 1.0 + (self.current_wave - 1) * 0.1
        
        # Notify wave start
        if 'on_wave_start' in self._wave_callbacks:
            self._wave_callbacks['on_wave_start'](
                self.current_wave,
                self.enemies_remaining,
                score_multiplier
            )
            
        print(f"Starting wave {self.current_wave} with {self.enemies_remaining} enemies")
    
    def enemy_destroyed(self) -> None:
        """Register an enemy being destroyed."""
        if not self.enabled or self.wave_complete:
            return
            
        self.enemies_remaining = max(0, self.enemies_remaining - 1)
        
        # Check for wave completion
        if self.enemies_remaining == 0:
            self.wave_complete = True
            if 'on_wave_complete' in self._wave_callbacks:
                self._wave_callbacks['on_wave_complete'](self.current_wave)
            print(f"Wave {self.current_wave} completed!")
    
    def next_wave(self) -> None:
        """Advance to next wave."""
        if not self.enabled:
            return
            
        self.current_wave += 1
        print(f"Advancing to wave {self.current_wave}")
        self.start_wave()
    
    def reset_waves(self) -> None:
        """Reset to starting wave."""
        self.current_wave = 1
        self.enemies_remaining = 0
        self.wave_complete = False
        print("Wave progress reset to 1")
    
    def register_callback(self, event: str, callback: Callable) -> None:
        """Register a callback for wave events.
        
        Args:
            event: Event type ('on_wave_start' or 'on_wave_complete')
            callback: Function to call when event occurs
        """
        if event in ['on_wave_start', 'on_wave_complete']:
            self._wave_callbacks[event] = callback
    
    def get_difficulty_scale(self) -> float:
        """Get current difficulty scaling factor.
        
        Returns:
            Difficulty multiplier based on current wave
        """
        return pow(self.difficulty_multiplier, self.current_wave - 1)
    
    @property
    def wave(self) -> int:
        """Get current wave number."""
        return self.current_wave 