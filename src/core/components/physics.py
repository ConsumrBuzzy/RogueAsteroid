"""Physics component for handling velocity and forces."""
from typing import Tuple
from .component import Component

class PhysicsComponent(Component):
    """Component for managing entity physics.
    
    Provides:
    - Velocity management
    - Acceleration handling
    - Force application
    - Friction/drag
    - Speed limiting
    """
    
    def __init__(self, entity, max_speed: float = float('inf'), friction: float = 0):
        """Initialize physics component.
        
        Args:
            entity: Entity this component belongs to
            max_speed: Maximum speed limit (infinity for no limit)
            friction: Friction coefficient (0 for no friction)
        """
        super().__init__(entity)
        self.velocity_x = 0.0
        self.velocity_y = 0.0
        self.acceleration_x = 0.0
        self.acceleration_y = 0.0
        self.max_speed = max_speed
        self.friction = friction
        
        print(f"PhysicsComponent initialized with max_speed={max_speed}, friction={friction}")
    
    @property
    def velocity(self) -> Tuple[float, float]:
        """Get current velocity vector."""
        return (self.velocity_x, self.velocity_y)
    
    @velocity.setter
    def velocity(self, value: Tuple[float, float]) -> None:
        """Set velocity from tuple.
        
        Args:
            value: (x, y) velocity tuple
        """
        self.velocity_x, self.velocity_y = value
        self._clamp_speed()
    
    @property
    def speed(self) -> float:
        """Get current speed (magnitude of velocity)."""
        return (self.velocity_x * self.velocity_x + 
                self.velocity_y * self.velocity_y) ** 0.5
    
    def update(self, dt: float) -> None:
        """Update physics simulation.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return
            
        # Apply acceleration
        self.velocity_x += self.acceleration_x * dt
        self.velocity_y += self.acceleration_y * dt
        
        # Apply friction
        if self.friction > 0:
            self.velocity_x *= (1 - self.friction)
            self.velocity_y *= (1 - self.friction)
        
        # Clamp speed
        self._clamp_speed()
        
        # Update position via transform component
        transform = self.get_sibling_component('TransformComponent')
        if transform:
            transform.move(
                self.velocity_x * dt,
                self.velocity_y * dt
            )
    
    def _clamp_speed(self) -> None:
        """Limit speed to max_speed if set."""
        current_speed = self.speed
        if current_speed > self.max_speed:
            scale = self.max_speed / current_speed
            self.velocity_x *= scale
            self.velocity_y *= scale
    
    def add_force(self, force_x: float, force_y: float) -> None:
        """Add a force vector to current acceleration.
        
        Args:
            force_x: X component of force
            force_y: Y component of force
        """
        self.acceleration_x += force_x
        self.acceleration_y += force_y
    
    def add_impulse(self, impulse_x: float, impulse_y: float) -> None:
        """Add an instantaneous impulse to velocity.
        
        Args:
            impulse_x: X component of impulse
            impulse_y: Y component of impulse
        """
        self.velocity_x += impulse_x
        self.velocity_y += impulse_y
        self._clamp_speed()
    
    def stop(self) -> None:
        """Stop all movement."""
        self.velocity_x = 0
        self.velocity_y = 0
        self.acceleration_x = 0
        self.acceleration_y = 0 