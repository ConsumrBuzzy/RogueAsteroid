"""Health component for managing entity health and damage."""
from typing import Optional, Callable
from .base import Component

class HealthComponent(Component):
    """Component for managing entity health.
    
    Provides:
    - Health tracking
    - Damage handling
    - Invulnerability periods
    - Death callbacks
    - Visual feedback
    """
    
    def __init__(self, entity, max_health: float, invulnerable_time: float = 0,
                 on_damage: Optional[Callable] = None, on_death: Optional[Callable] = None):
        """Initialize health component.
        
        Args:
            entity: Entity this component belongs to
            max_health: Maximum health value
            invulnerable_time: Time in seconds to be invulnerable after damage
            on_damage: Optional callback when damage is taken
            on_death: Optional callback when health reaches 0
        """
        super().__init__(entity)
        self.max_health = max_health
        self.current_health = max_health
        self.invulnerable_time = invulnerable_time
        self.invulnerable_timer = 0
        self.on_damage = on_damage
        self.on_death = on_death
        self._is_dead = False
        
        print(f"HealthComponent initialized with {max_health} health")
    
    def update(self, dt: float) -> None:
        """Update invulnerability timer.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return
            
        # Update invulnerability
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0, self.invulnerable_timer - dt)
            
            # Update visual feedback through render component
            render = self.get_sibling_component('RenderComponent')
            if render:
                # Flash visibility every 0.1 seconds during invulnerability
                render.visible = (self.invulnerable_timer * 10) % 1 > 0.5
    
    def take_damage(self, amount: float) -> bool:
        """Apply damage to the entity.
        
        Args:
            amount: Amount of damage to apply
            
        Returns:
            True if damage was applied, False if invulnerable
        """
        if not self.enabled or self._is_dead or self.invulnerable_timer > 0:
            return False
            
        self.current_health = max(0, self.current_health - amount)
        
        # Start invulnerability period
        if self.invulnerable_time > 0:
            self.invulnerable_timer = self.invulnerable_time
        
        # Notify damage callback
        if self.on_damage:
            self.on_damage(amount)
            
        # Check for death
        if self.current_health <= 0 and not self._is_dead:
            self._is_dead = True
            if self.on_death:
                self.on_death()
        
        print(f"Entity took {amount} damage, health: {self.current_health}/{self.max_health}")
        return True
    
    def heal(self, amount: float) -> None:
        """Heal the entity.
        
        Args:
            amount: Amount of health to restore
        """
        if not self.enabled or self._is_dead:
            return
            
        self.current_health = min(self.max_health, self.current_health + amount)
        print(f"Entity healed {amount}, health: {self.current_health}/{self.max_health}")
    
    def revive(self, health_percentage: float = 1.0) -> None:
        """Revive the entity with specified health percentage.
        
        Args:
            health_percentage: Percentage of max health to restore (0-1)
        """
        if not self.enabled:
            return
            
        self._is_dead = False
        self.current_health = self.max_health * max(0, min(1, health_percentage))
        self.invulnerable_timer = self.invulnerable_time
        
        # Reset render visibility
        render = self.get_sibling_component('RenderComponent')
        if render:
            render.visible = True
            
        print(f"Entity revived with {self.current_health}/{self.max_health} health")
    
    @property
    def is_dead(self) -> bool:
        """Check if entity is dead."""
        return self._is_dead
    
    @property
    def is_invulnerable(self) -> bool:
        """Check if entity is currently invulnerable."""
        return self.invulnerable_timer > 0
    
    @property
    def health_percentage(self) -> float:
        """Get current health as percentage of max health."""
        return self.current_health / self.max_health if self.max_health > 0 else 0 