"""Utility functions for vector operations."""
import math
import pygame
import numpy as np
from typing import Union, Tuple, List

VectorLike = Union[pygame.Vector2, Tuple[float, float], List[float], np.ndarray]

def to_vector2(value: VectorLike) -> pygame.Vector2:
    """Convert various types to pygame.Vector2.
    
    Args:
        value: The value to convert. Can be:
            - pygame.Vector2
            - tuple of (x, y)
            - list of [x, y]
            - numpy array [x, y]
            - any object with x, y attributes
            
    Returns:
        pygame.Vector2: The converted vector
    """
    if isinstance(value, pygame.Vector2):
        return value
    if isinstance(value, (list, tuple, np.ndarray)):
        return pygame.Vector2(float(value[0]), float(value[1]))
    if hasattr(value, 'x') and hasattr(value, 'y'):
        return pygame.Vector2(float(value.x), float(value.y))
    return pygame.Vector2(value)

def ensure_minimum_velocity(velocity: VectorLike, min_speed: float) -> pygame.Vector2:
    """Ensure a velocity vector maintains a minimum speed if moving.
    
    Args:
        velocity: The velocity vector to check
        min_speed: The minimum speed to maintain if moving
        
    Returns:
        pygame.Vector2: The velocity vector with at least min_speed if moving
    """
    vel = to_vector2(velocity)
    speed = vel.length()
    if 0 < speed < min_speed:
        return vel.normalize() * min_speed
    return vel

def angle_to_vector(angle_degrees: float) -> pygame.Vector2:
    """Convert an angle in degrees to a unit vector.
    
    Args:
        angle_degrees: The angle in degrees (0 is right, 90 is down)
        
    Returns:
        pygame.Vector2: A unit vector pointing in the specified direction
    """
    angle_rad = math.radians(angle_degrees)
    return pygame.Vector2(math.cos(angle_rad), math.sin(angle_rad))

def vector_to_angle(vector: VectorLike) -> float:
    """Convert a vector to an angle in degrees.
    
    Args:
        vector: The vector to convert
        
    Returns:
        float: The angle in degrees (0 is right, 90 is down)
    """
    vec = to_vector2(vector)
    return math.degrees(math.atan2(vec.y, vec.x))
