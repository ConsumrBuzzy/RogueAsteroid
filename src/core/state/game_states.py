"""Game states enumeration."""
from enum import Enum, auto

class GameState(Enum):
    """Game states for the state machine."""
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    OPTIONS = auto()
    HIGH_SCORES = auto()
    QUIT = auto() 