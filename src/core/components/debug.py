"""Debug component for development and testing support."""
from typing import Dict, List, Any, Optional, Callable
import pygame
from .base import Component

class DebugComponent(Component):
    """Component for managing debug features and testing support.
    
    Provides:
    - Visual debugging
    - Performance monitoring
    - State inspection
    - Event logging
    - Testing hooks
    """
    
    def __init__(self, entity):
        """Initialize debug component.
        
        Args:
            entity: Entity this component belongs to
        """
        super().__init__(entity)
        self._watches: Dict[str, Callable[[], Any]] = {}
        self._logs: List[str] = []
        self._draw_colliders = False
        self._draw_vectors = False
        self._draw_info = False
        self._max_logs = 100
        self._font = None
        self._font_size = 16
        
        print("DebugComponent initialized")
    
    def update(self, dt: float) -> None:
        """Update debug information.
        
        Args:
            dt: Delta time in seconds
        """
        if not self.enabled:
            return
            
        # Update watched values
        for name, getter in self._watches.items():
            try:
                value = getter()
                self.log(f"{name}: {value}")
            except Exception as e:
                self.log(f"Error watching {name}: {e}")
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw debug visualizations.
        
        Args:
            screen: Pygame surface to render on
        """
        if not self.enabled:
            return
            
        # Initialize font if needed
        if self._font is None:
            self._font = pygame.font.Font(None, self._font_size)
        
        # Draw debug info
        if self._draw_info:
            y = 10
            for i, log in enumerate(self._logs[-10:]):  # Show last 10 logs
                surface = self._font.render(log, True, (255, 255, 0))
                screen.blit(surface, (10, y))
                y += self._font_size + 2
        
        # Draw colliders if enabled
        if self._draw_colliders:
            self._draw_entity_colliders(screen)
        
        # Draw vectors if enabled
        if self._draw_vectors:
            self._draw_entity_vectors(screen)
    
    def _draw_entity_colliders(self, screen: pygame.Surface) -> None:
        """Draw collision boundaries for debugging.
        
        Args:
            screen: Pygame surface to render on
        """
        collision = self.get_sibling_component('CollisionComponent')
        transform = self.get_sibling_component('TransformComponent')
        
        if collision and transform:
            # Draw collision circle
            pygame.draw.circle(
                screen,
                (255, 0, 0),
                (int(transform.x), int(transform.y)),
                int(collision.radius),
                1
            )
    
    def _draw_entity_vectors(self, screen: pygame.Surface) -> None:
        """Draw velocity and direction vectors for debugging.
        
        Args:
            screen: Pygame surface to render on
        """
        physics = self.get_sibling_component('PhysicsComponent')
        transform = self.get_sibling_component('TransformComponent')
        
        if physics and transform:
            # Draw velocity vector
            end_pos = (
                transform.x + physics.velocity[0] * 0.5,
                transform.y + physics.velocity[1] * 0.5
            )
            pygame.draw.line(
                screen,
                (0, 255, 0),
                (transform.x, transform.y),
                end_pos,
                1
            )
            
            # Draw forward vector
            end_pos = (
                transform.x + transform.forward[0] * 30,
                transform.y + transform.forward[1] * 30
            )
            pygame.draw.line(
                screen,
                (0, 0, 255),
                (transform.x, transform.y),
                end_pos,
                1
            )
    
    def watch(self, name: str, getter: Callable[[], Any]) -> None:
        """Add a value to watch during debugging.
        
        Args:
            name: Name of the watched value
            getter: Function that returns the value to watch
        """
        self._watches[name] = getter
        print(f"Added debug watch for '{name}'")
    
    def unwatch(self, name: str) -> None:
        """Remove a watched value.
        
        Args:
            name: Name of value to stop watching
        """
        if name in self._watches:
            del self._watches[name]
            print(f"Removed debug watch for '{name}'")
    
    def log(self, message: str) -> None:
        """Add a message to the debug log.
        
        Args:
            message: Message to log
        """
        self._logs.append(message)
        if len(self._logs) > self._max_logs:
            self._logs.pop(0)
    
    def clear_log(self) -> None:
        """Clear the debug log."""
        self._logs.clear()
        print("Debug log cleared")
    
    def toggle_colliders(self, show: Optional[bool] = None) -> None:
        """Toggle collision boundary visualization.
        
        Args:
            show: If provided, set specific state, otherwise toggle
        """
        if show is None:
            self._draw_colliders = not self._draw_colliders
        else:
            self._draw_colliders = show
    
    def toggle_vectors(self, show: Optional[bool] = None) -> None:
        """Toggle vector visualization.
        
        Args:
            show: If provided, set specific state, otherwise toggle
        """
        if show is None:
            self._draw_vectors = not self._draw_vectors
        else:
            self._draw_vectors = show
    
    def toggle_info(self, show: Optional[bool] = None) -> None:
        """Toggle debug info display.
        
        Args:
            show: If provided, set specific state, otherwise toggle
        """
        if show is None:
            self._draw_info = not self._draw_info
        else:
            self._draw_info = show 