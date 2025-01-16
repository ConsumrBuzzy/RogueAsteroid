"""
Entity Component System (ECS) implementation for RogueAsteroid.
This module provides a data-oriented design pattern for game entities.
"""

from .world import World
from .components import Component
from .system import System
from .events import Event, EventEmitter
from .resources import Resources

__all__ = ['World', 'Component', 'System', 'Event', 'EventEmitter', 'Resources']
