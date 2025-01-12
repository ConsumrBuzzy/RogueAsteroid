"""State service for game state management."""
from typing import Dict, Optional, Callable, List
from enum import Enum, auto

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
    """Service for managing game states.
    
    Provides:
    - State transitions
    - State-specific handlers
    - State validation
    - State history
    """
    
    def __init__(self):
        """Initialize the state service."""
        self._current_state: Optional[GameState] = None
        self._state_handlers: Dict[GameState, List[Callable]] = {}
        self._state_history: List[GameState] = []
        
        # Initialize handlers for each state
        for state in GameState:
            self._state_handlers[state] = []
            
        # Set initial state
        self.change_state(GameState.MAIN_MENU)
        print("StateService initialized")
        
    def add_handler(self, state: GameState, handler: Callable) -> None:
        """Add a handler for a specific state.
        
        Args:
            state: Game state to handle
            handler: Function to call when state is active
        """
        if state in self._state_handlers:
            self._state_handlers[state].append(handler)
            
    def remove_handler(self, state: GameState, handler: Callable) -> None:
        """Remove a handler for a specific state.
        
        Args:
            state: Game state to remove handler from
            handler: Handler to remove
        """
        if state in self._state_handlers and handler in self._state_handlers[state]:
            self._state_handlers[state].remove(handler)
            
    def get_current_state(self) -> Optional[GameState]:
        """Get the current game state.
        
        Returns:
            Current state or None if no state set
        """
        return self._current_state
        
    def change_state(self, new_state: str | GameState) -> None:
        """Change to a new game state.
        
        Args:
            new_state: State to change to (can be string or GameState enum)
        """
        # Convert string to enum if needed
        if isinstance(new_state, str):
            try:
                new_state = GameState[new_state]
            except KeyError:
                print(f"Invalid state name: {new_state}")
                return
                
        # Don't change if same state
        if new_state == self._current_state:
            return
            
        # Log state change
        if self._current_state:
            print(f"State changing from {self._current_state.name} to {new_state.name}")
        else:
            print(f"Initial state set to: {new_state.name}")
            
        # Update state
        self._current_state = new_state
        self._state_history.append(new_state)
        
        # Call handlers for new state
        for handler in self._state_handlers.get(new_state, []):
            handler()
            
        print(f"State changed to: {new_state.name}")
        
    def get_previous_state(self) -> Optional[GameState]:
        """Get the previous game state.
        
        Returns:
            Previous state or None if no history
        """
        if len(self._state_history) > 1:
            return self._state_history[-2]
        return None
        
    def revert_to_previous_state(self) -> None:
        """Revert to the previous game state."""
        if previous_state := self.get_previous_state():
            self.change_state(previous_state)
            
    def update(self, dt: float) -> None:
        """Update current state handlers.
        
        Args:
            dt: Delta time in seconds
        """
        if self._current_state:
            for handler in self._state_handlers[self._current_state]:
                handler()
                
    def cleanup(self) -> None:
        """Clean up the service."""
        self._state_handlers.clear()
        self._state_history.clear()
        self._current_state = None
        print("StateService cleaned up") 