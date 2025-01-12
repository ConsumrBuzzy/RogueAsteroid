"""Component for handling position and movement."""
from typing import TYPE_CHECKING
import pygame
from pygame import Vector2
import math

from ..entity.entity import Entity
from .component import Component

if TYPE_CHECKING:
    from ..game import Game

class TransformComponent(Component):
    """Component for handling position and movement.
    
    Manages an entity's position, velocity, and rotation in 2D space.
    """
    
    def __init__(self, entity: Entity, x: float = 0, y: float = 0) -> None:
        """Initialize the transform component.
        
        Args:
            entity: The entity this component belongs to.
            x: Initial x position.
            y: Initial y position.
        """
        super().__init__(entity)
        self._position = Vector2(x, y)
        self._rotation = 0.0  # In degrees
        self._velocity = Vector2(0, 0)  # Added velocity vector
        
    @property
    def velocity(self) -> Vector2:
        """Get the current velocity."""
        return self._velocity
        
    @velocity.setter
    def velocity(self, value: Vector2) -> None:
        """Set the velocity.
        
        Args:
            value: New velocity vector
        """
        self._velocity = Vector2(value)
        
    @property
    def entity(self) -> Entity:
        """Get the entity this component belongs to."""
        return self._entity
        
    @property
    def position(self) -> Vector2:
        """Get the current position."""
        return self._position
        
    @position.setter
    def position(self, value: Vector2) -> None:
        """Set the position.
        
        Args:
            value: New position vector
        """
        self._position = Vector2(value)
        
    @property
    def x(self) -> float:
        """Get the x position."""
        return self._position.x
        
    @x.setter
    def x(self, value: float) -> None:
        """Set the x position.
        
        Args:
            value: New x position
        """
        self._position.x = value
        
    @property
    def y(self) -> float:
        """Get the y position."""
        return self._position.y
        
    @y.setter
    def y(self, value: float) -> None:
        """Set the y position.
        
        Args:
            value: New y position
        """
        self._position.y = value
        
    @property
    def rotation(self) -> float:
        """Get the rotation in degrees."""
        return self._rotation
        
    @rotation.setter
    def rotation(self, value: float) -> None:
        """Set the rotation.
        
        Args:
            value: New rotation in degrees
        """
        self._rotation = value % 360
        
    def move(self, dx: float, dy: float) -> None:
        """Move relative to current position.
        
        Args:
            dx: Change in x position
            dy: Change in y position
        """
        self._position.x += dx
        self._position.y += dy
        
    def rotate(self, angle: float) -> None:
        """Rotate by an angle.
        
        Args:
            angle: Angle to rotate by in degrees
        """
        self._rotation = (self._rotation + angle) % 360
        
    def get_direction(self) -> Vector2:
        """Get the current facing direction as a normalized vector.
        
        Returns:
            Direction vector
        """
        angle_rad = math.radians(self._rotation - 90)  # -90 to align with pygame's coordinate system
        return Vector2(math.cos(angle_rad), math.sin(angle_rad))
        
    def on_update(self, dt: float) -> None:
        """Update the transform.
        
        Args:
            dt: Delta time in seconds
        """
        if self._velocity.length() > 0:
            self.move(self._velocity.x * dt, self._velocity.y * dt) 