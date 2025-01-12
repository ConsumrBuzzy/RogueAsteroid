"""Game state management system."""
from enum import Enum, auto
from typing import Optional, Dict, Callable, Set
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

class StateManager:
    """Manages game states and transitions."""
    
    def __init__(self):
        """Initialize the state manager."""
        self._current_state: Optional[GameState] = None
        self._previous_state: Optional[GameState] = None
        self._state_handlers: Dict[GameState, Dict[str, Callable]] = {}
        self._valid_transitions: Dict[GameState, Set[GameState]] = {}
        self._paused = False
        
        # Set up valid state transitions
        self._setup_valid_transitions()
        
        # Register default handlers
        self.register_state(GameState.MAIN_MENU, 
                          on_enter=self._enter_main_menu,
                          on_exit=self._exit_main_menu,
                          on_update=self._update_main_menu,
                          on_draw=self._draw_main_menu,
                          on_input=self._handle_main_menu_input)
                          
        self.register_state(GameState.PLAYING,
                          on_enter=self._enter_playing,
                          on_exit=self._exit_playing,
                          on_update=self._update_playing,
                          on_draw=self._draw_playing,
                          on_input=self._handle_playing_input)
                          
        print("StateManager initialized")
        
    def _setup_valid_transitions(self) -> None:
        """Set up valid state transitions."""
        # From main menu
        self._valid_transitions[GameState.MAIN_MENU] = {
            GameState.PLAYING,
            GameState.OPTIONS,
            GameState.HIGH_SCORE
        }
        
        # From playing
        self._valid_transitions[GameState.PLAYING] = {
            GameState.PAUSED,
            GameState.GAME_OVER,
            GameState.NEW_HIGH_SCORE
        }
        
        # From paused
        self._valid_transitions[GameState.PAUSED] = {
            GameState.PLAYING,
            GameState.MAIN_MENU
        }
        
        # From options
        self._valid_transitions[GameState.OPTIONS] = {
            GameState.MAIN_MENU
        }
        
        # From high score
        self._valid_transitions[GameState.HIGH_SCORE] = {
            GameState.MAIN_MENU
        }
        
        # From new high score
        self._valid_transitions[GameState.NEW_HIGH_SCORE] = {
            GameState.HIGH_SCORE,
            GameState.MAIN_MENU
        }
        
        # From game over
        self._valid_transitions[GameState.GAME_OVER] = {
            GameState.NEW_HIGH_SCORE,
            GameState.MAIN_MENU
        }
        
    def is_valid_transition(self, from_state: GameState, to_state: GameState) -> bool:
        """Check if a state transition is valid.
        
        Args:
            from_state: Current state
            to_state: Target state
            
        Returns:
            bool: True if transition is valid
        """
        if from_state not in self._valid_transitions:
            return False
        return to_state in self._valid_transitions[from_state]
        
    def change_state(self, new_state: GameState) -> bool:
        """Change to a new state.
        
        Args:
            new_state: State to change to
            
        Returns:
            bool: True if state changed successfully
            
        Raises:
            ValueError: If new_state is invalid
        """
        if new_state not in GameState:
            raise ValueError(f"Invalid state: {new_state}")
            
        # Check if transition is valid
        if self._current_state and not self.is_valid_transition(self._current_state, new_state):
            print(f"Invalid state transition: {self._current_state} -> {new_state}")
            return False
            
        try:
            # Exit current state
            if self._current_state and self._current_state in self._state_handlers:
                self._state_handlers[self._current_state]['on_exit']()
                
            # Update state
            self._previous_state = self._current_state
            self._current_state = new_state
            
            # Enter new state
            if new_state in self._state_handlers:
                self._state_handlers[new_state]['on_enter']()
                
            print(f"State changed: {new_state}")
            return True
            
        except Exception as e:
            print(f"Error changing state: {e}")
            return False
            
    def update(self, dt: float) -> None:
        """Update the current state.
        
        Args:
            dt: Time delta in seconds
        """
        if not self._current_state:
            return
            
        try:
            if self._current_state in self._state_handlers:
                self._state_handlers[self._current_state]['on_update'](dt)
        except Exception as e:
            print(f"Error updating state: {e}")
            
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the current state.
        
        Args:
            screen: Surface to draw on
        """
        if not self._current_state:
            return
            
        try:
            if self._current_state in self._state_handlers:
                self._state_handlers[self._current_state]['on_draw'](screen)
        except Exception as e:
            print(f"Error drawing state: {e}")
            
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input for current state.
        
        Args:
            event: Event to handle
        """
        if not self._current_state:
            return
            
        try:
            if self._current_state in self._state_handlers:
                self._state_handlers[self._current_state]['on_input'](event)
        except Exception as e:
            print(f"Error handling input: {e}")
            
    # State handler implementations
    def _enter_main_menu(self) -> None:
        """Enter main menu state."""
        self._paused = False
        # Reset game state
        self.publish_event('menu_entered')
        
    def _exit_main_menu(self) -> None:
        """Exit main menu state."""
        self.publish_event('menu_exited')
        
    def _update_main_menu(self, dt: float) -> None:
        """Update main menu state."""
        # Update menu animations
        pass
        
    def _draw_main_menu(self, screen: pygame.Surface) -> None:
        """Draw main menu state."""
        try:
            # Draw menu background
            screen.fill((0, 0, 0))  # Black background
            
            # Draw menu items (delegated to menu service)
            self.publish_event('draw_menu', screen)
            
        except pygame.error as e:
            print(f"Error drawing menu: {e}")
            
    def _handle_main_menu_input(self, event: pygame.event.Event) -> None:
        """Handle main menu input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.publish_event('quit_game')
                
    def _enter_playing(self) -> None:
        """Enter playing state."""
        self._paused = False
        self.publish_event('game_started')
        
    def _exit_playing(self) -> None:
        """Exit playing state."""
        self.publish_event('game_exited')
        
    def _update_playing(self, dt: float) -> None:
        """Update playing state."""
        if not self._paused:
            self.publish_event('update_game', dt)
            
    def _draw_playing(self, screen: pygame.Surface) -> None:
        """Draw playing state."""
        try:
            self.publish_event('draw_game', screen)
        except pygame.error as e:
            print(f"Error drawing game: {e}")
            
    def _handle_playing_input(self, event: pygame.event.Event) -> None:
        """Handle playing state input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.change_state(GameState.PAUSED)
            else:
                self.publish_event('game_input', event)
                
    def publish_event(self, event_type: str, *args) -> None:
        """Publish a state event.
        
        Args:
            event_type: Type of event
            *args: Event arguments
        """
        # Delegate to event manager if available
        if hasattr(self, '_event_manager'):
            self._event_manager.publish(event_type, *args) 