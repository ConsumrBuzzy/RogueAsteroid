"""State service for game state management."""
from typing import Dict, Optional, Callable, List
from enum import Enum, auto
import pygame

class GameState(Enum):
    """Game states enumeration."""
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    OPTIONS = auto()
    HIGH_SCORE = auto()
    NEW_HIGH_SCORE = auto()
    GAME_OVER = auto()

class StateService:
    """Service for game state management.
    
    Provides:
    - State transitions
    - State-specific updates
    - Input handling per state
    - State history tracking
    - State validation
    """
    
    def __init__(self):
        """Initialize the state service."""
        self._current_state = GameState.MAIN_MENU
        self._previous_state = None
        self._state_handlers: Dict[GameState, Dict[str, Callable]] = {}
        self._state_data: Dict[GameState, Dict] = {}
        
        # Initialize state handlers dictionary
        for state in GameState:
            self._state_handlers[state] = {
                'enter': lambda: None,
                'exit': lambda: None,
                'update': lambda dt: None,
                'draw': lambda: None,
                'input': lambda event: None
            }
            self._state_data[state] = {}
            
        print("StateService initialized")
        
    def register_handler(self, state: GameState, handler_type: str, handler: Callable) -> None:
        """Register a handler for a specific state.
        
        Args:
            state: Game state to register for
            handler_type: Type of handler ('enter', 'exit', 'update', 'draw', 'input')
            handler: Handler function
        """
        if state in self._state_handlers and handler_type in self._state_handlers[state]:
            self._state_handlers[state][handler_type] = handler
            print(f"Registered {handler_type} handler for state {state.name}")
            
    def change_state(self, new_state: GameState) -> None:
        """Change to a new game state.
        
        Args:
            new_state: State to change to
        """
        if new_state == self._current_state:
            return
            
        # Call exit handler for current state
        self._state_handlers[self._current_state]['exit']()
        
        print(f"State changing from {self._current_state.name} to {new_state.name}")
        
        # Update state
        self._previous_state = self._current_state
        self._current_state = new_state
        
        # Call enter handler for new state
        self._state_handlers[self._current_state]['enter']()
        
    def get_current_state(self) -> GameState:
        """Get the current game state.
        
        Returns:
            Current GameState
        """
        return self._current_state
        
    def get_previous_state(self) -> Optional[GameState]:
        """Get the previous game state.
        
        Returns:
            Previous GameState if exists, None otherwise
        """
        return self._previous_state
        
    def update(self, dt: float) -> None:
        """Update the current state.
        
        Args:
            dt: Delta time in seconds
        """
        self._state_handlers[self._current_state]['update'](dt)
        
    def draw(self) -> None:
        """Draw the current state."""
        self._state_handlers[self._current_state]['draw']()
        
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input for the current state.
        
        Args:
            event: Pygame event to handle
        """
        self._state_handlers[self._current_state]['input'](event)
        
    def set_state_data(self, state: GameState, key: str, value: any) -> None:
        """Set data for a specific state.
        
        Args:
            state: State to set data for
            key: Data key
            value: Data value
        """
        if state in self._state_data:
            self._state_data[state][key] = value
            
    def get_state_data(self, state: GameState, key: str) -> Optional[any]:
        """Get data for a specific state.
        
        Args:
            state: State to get data from
            key: Data key
            
        Returns:
            Data value if exists, None otherwise
        """
        return self._state_data.get(state, {}).get(key)
        
    def clear_state_data(self, state: GameState) -> None:
        """Clear all data for a specific state.
        
        Args:
            state: State to clear data for
        """
        if state in self._state_data:
            self._state_data[state].clear()
            print(f"Cleared data for state {state.name}") 