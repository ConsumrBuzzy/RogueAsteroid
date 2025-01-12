"""State service for game state management."""
from enum import Enum, auto
from typing import Optional, Dict, Callable
import pygame

class GameState(Enum):
    """Game states."""
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    HIGH_SCORE = auto()
    OPTIONS = auto()

class StateService:
    """Service for managing game states.
    
    Provides:
    - State transitions
    - State-specific updates
    - Menu state handling
    """
    
    _instance = None
    
    def __new__(cls):
        """Create or return singleton instance."""
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance
        
    def __init__(self):
        """Initialize the state service."""
        if self._initialized:
            return
            
        self._current_state: Optional[GameState] = None
        self._previous_state: Optional[GameState] = None
        self._state_handlers: Dict[GameState, Callable] = {}
        
        # Set initial state
        self.change_state(GameState.MAIN_MENU)
        print("StateService initialized")
        self._initialized = True
        
    def register_handler(self, state: GameState, handler: Callable) -> None:
        """Register a handler for a state.
        
        Args:
            state: Game state to handle
            handler: Function to call when state is active
        """
        self._state_handlers[state] = handler
        print(f"Registered handler for state {state.name}")
        
    def change_state(self, new_state: GameState) -> None:
        """Change to a new game state.
        
        Args:
            new_state: State to change to
        """
        if new_state == self._current_state:
            return
            
        self._previous_state = self._current_state
        self._current_state = new_state
        
        # Get menu service and update current menu
        from .menu_service import MenuService
        menu_service = MenuService()
        menu_service.set_current_menu(new_state)
        
        print(f"Changed state from {self._previous_state} to {new_state}")
        
    def get_current_state(self) -> Optional[GameState]:
        """Get the current game state.
        
        Returns:
            Current GameState or None
        """
        return self._current_state
        
    def get_previous_state(self) -> Optional[GameState]:
        """Get the previous game state.
        
        Returns:
            Previous GameState or None
        """
        return self._previous_state
        
    def update(self, dt: float) -> None:
        """Update current state.
        
        Args:
            dt: Delta time in seconds
        """
        if self._current_state and self._current_state in self._state_handlers:
            self._state_handlers[self._current_state](dt)
            
    def cleanup(self) -> None:
        """Clean up the service."""
        self._current_state = None
        self._previous_state = None
        self._state_handlers.clear()
        print("StateService cleaned up") 