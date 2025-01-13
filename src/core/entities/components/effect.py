"""Effect component module."""
from typing import Dict, Optional, Callable
from .base import Component

class EffectComponent(Component):
    """Component for managing visual effects on entities."""
    def __init__(self, entity):
        super().__init__(entity)
        self.effects: Dict[str, dict] = {}  # Active effects
        self.default_alpha = 255
        self.current_alpha = 255
        self.is_visible = True
    
    def add_effect(self, name: str, duration: float, 
                  on_start: Optional[Callable] = None,
                  on_update: Optional[Callable] = None,
                  on_end: Optional[Callable] = None) -> None:
        """Add a timed effect.
        
        Args:
            name: Unique identifier for the effect
            duration: Duration in seconds (use float('inf') for permanent effects)
            on_start: Optional callback when effect starts
            on_update: Optional callback during effect update
            on_end: Optional callback when effect ends
        """
        # Validate callbacks are actually callable if provided
        if on_start is not None and not callable(on_start):
            raise TypeError(f"on_start must be callable or None, got {type(on_start)}")
        if on_update is not None and not callable(on_update):
            raise TypeError(f"on_update must be callable or None, got {type(on_update)}")
        if on_end is not None and not callable(on_end):
            raise TypeError(f"on_end must be callable or None, got {type(on_end)}")
            
        self.effects[name] = {
            'duration': duration,
            'time_remaining': duration,
            'on_start': on_start,
            'on_update': on_update,
            'on_end': on_end,
            'active': True
        }
        
        # Only call on_start if it's a valid callback
        if on_start and callable(on_start):
            on_start()
            
    def remove_effect(self, name: str) -> None:
        """Remove an effect by name."""
        if name in self.effects:
            effect = self.effects[name]
            if effect['on_end']:
                effect['on_end']()
            del self.effects[name]
    
    def has_effect(self, name: str) -> bool:
        """Check if an effect is active."""
        return name in self.effects
    
    def clear_effects(self) -> None:
        """Remove all active effects."""
        effect_names = list(self.effects.keys())
        for name in effect_names:
            self.remove_effect(name)
    
    def update(self, dt: float) -> None:
        """Update all active effects."""
        # Update each effect
        effects_to_remove = []
        for name, effect in self.effects.items():
            effect['time_remaining'] -= dt
            
            # Call update callback if it exists
            if effect['on_update']:
                effect['on_update'](effect['time_remaining'] / effect['duration'])
            
            # Check if effect has expired
            if effect['time_remaining'] <= 0:
                effects_to_remove.append(name)
        
        # Remove expired effects
        for name in effects_to_remove:
            self.remove_effect(name)
    
    def set_visibility(self, visible: bool) -> None:
        """Set entity visibility."""
        self.is_visible = visible
        self.current_alpha = self.default_alpha if visible else 0
    
    def set_alpha(self, alpha: int) -> None:
        """Set entity alpha/transparency."""
        self.current_alpha = max(0, min(255, alpha)) 
    
    def set_effect_active(self, name: str, active: bool) -> None:
        """Set whether an effect is active."""
        if name in self.effects:
            self.effects[name]['active'] = active 