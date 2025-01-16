"""
Resource management for global game state.
"""

from typing import Dict, Type, TypeVar, Any, Optional
from dataclasses import dataclass, field
import pygame

T = TypeVar('T')

@dataclass
class WindowInfo:
    """Window configuration resource."""
    width: int
    height: int
    title: str = "Rogue Asteroid"

@dataclass
class GameSettings:
    """Game settings resource."""
    difficulty: float = 1.0
    sound_enabled: bool = True
    music_volume: float = 0.7
    sfx_volume: float = 1.0

@dataclass
class GameState:
    """Current game state resource."""
    score: int = 0
    level: int = 1
    lives: int = 3
    paused: bool = False
    quit: bool = False
    game_over: bool = False

@dataclass
class SpriteResource:
    """Resource for managing game sprites."""
    sprites: Dict[str, pygame.Surface] = field(default_factory=dict)
    shapes: Dict[str, list] = field(default_factory=dict)

@dataclass
class AudioResource:
    """Resource for managing game audio."""
    sounds: Dict[str, pygame.mixer.Sound] = field(default_factory=dict)
    music: Dict[str, str] = field(default_factory=dict)  # Music paths

@dataclass
class MenuResource:
    """Resource for managing menu state."""
    active: bool = True
    current_menu: str = "main"  # main, pause, game_over
    selected_item: int = 0
    menu_items: Dict[str, list] = field(default_factory=lambda: {
        "main": [
            ("Start Game", "start"),
            ("High Scores", "scores"),
            ("Settings", "settings"),
            ("Quit", "quit")
        ],
        "pause": [
            ("Resume", "resume"),
            ("Settings", "settings"),
            ("Quit to Menu", "menu")
        ],
        "game_over": [
            ("Play Again", "start"),
            ("High Scores", "scores"),
            ("Quit to Menu", "menu")
        ]
    })

class Resources:
    """
    Manages global game resources and state.
    Resources are singleton-like objects that can be accessed by systems.
    """
    def __init__(self):
        self._resources: Dict[Type, Any] = {}

    def add(self, resource: Any) -> None:
        """Add or update a resource."""
        self._resources[type(resource)] = resource

    def get(self, resource_type: Type[T]) -> Optional[T]:
        """Get a resource by type."""
        return self._resources.get(resource_type)

    def remove(self, resource_type: Type) -> None:
        """Remove a resource."""
        if resource_type in self._resources:
            del self._resources[resource_type]

    def clear(self) -> None:
        """Remove all resources."""
        self._resources.clear()
