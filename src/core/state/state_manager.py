"""Game state management system."""
from enum import Enum, auto
from typing import Optional, Dict, Callable
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
    """Manages game state transitions and state-specific behaviors."""
    
    def __init__(self, game):
        """Initialize the state manager.
        
        Args:
            game: Reference to the main game instance
        """
        self._game = game
        self._current_state: Optional[GameState] = None
        self._previous_state: Optional[GameState] = None
        self._state_handlers: Dict[GameState, Dict[str, Callable]] = {}
        self._initialize_state_handlers()
        
        # Debug info
        print("StateManager initialized")
    
    def _initialize_state_handlers(self):
        """Initialize state-specific handlers."""
        # Main Menu handlers
        self._state_handlers[GameState.MAIN_MENU] = {
            'enter': self._enter_main_menu,
            'exit': self._exit_main_menu,
            'update': self._update_main_menu,
            'draw': self._draw_main_menu,
            'handle_input': self._handle_main_menu_input
        }
        
        # Playing state handlers
        self._state_handlers[GameState.PLAYING] = {
            'enter': self._enter_playing,
            'exit': self._exit_playing,
            'update': self._update_playing,
            'draw': self._draw_playing,
            'handle_input': self._handle_playing_input
        }
        
        # Initialize other state handlers similarly...
    
    @property
    def current_state(self) -> Optional[GameState]:
        """Get the current game state."""
        return self._current_state
    
    @property
    def previous_state(self) -> Optional[GameState]:
        """Get the previous game state."""
        return self._previous_state
    
    def change_state(self, new_state: GameState):
        """Change to a new game state.
        
        Args:
            new_state: The GameState to transition to
        """
        # Don't transition to the same state
        if new_state == self._current_state:
            return
            
        print(f"State changing from {self._current_state} to {new_state}")
        
        # Exit current state
        if self._current_state and self._current_state in self._state_handlers:
            self._state_handlers[self._current_state]['exit']()
        
        # Update state tracking
        self._previous_state = self._current_state
        self._current_state = new_state
        
        # Enter new state
        if new_state in self._state_handlers:
            self._state_handlers[new_state]['enter']()
        
        print(f"State changed to: {new_state}")
    
    def update(self, dt: float):
        """Update the current state.
        
        Args:
            dt: Delta time in seconds
        """
        if self._current_state in self._state_handlers:
            self._state_handlers[self._current_state]['update'](dt)
    
    def draw(self, screen: pygame.Surface):
        """Draw the current state.
        
        Args:
            screen: Pygame surface to draw on
        """
        if self._current_state in self._state_handlers:
            self._state_handlers[self._current_state]['draw'](screen)
    
    def handle_input(self, event: pygame.event.Event):
        """Handle input for the current state.
        
        Args:
            event: Pygame event to handle
        """
        if self._current_state in self._state_handlers:
            self._state_handlers[self._current_state]['handle_input'](event)
    
    # State handler methods
    def _enter_main_menu(self):
        """Enter main menu state."""
        pass
    
    def _exit_main_menu(self):
        """Exit main menu state."""
        pass
    
    def _update_main_menu(self, dt: float):
        """Update main menu state."""
        pass
    
    def _draw_main_menu(self, screen: pygame.Surface):
        """Draw main menu state."""
        pass
    
    def _handle_main_menu_input(self, event: pygame.event.Event):
        """Handle main menu input."""
        pass
    
    def _enter_playing(self):
        """Enter playing state."""
        self._game.reset_game()
    
    def _exit_playing(self):
        """Exit playing state."""
        pass
    
    def _update_playing(self, dt: float):
        """Update playing state."""
        self._game.update(dt)
    
    def _draw_playing(self, screen: pygame.Surface):
        """Draw playing state."""
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw all entities
        for entity in self._game.entities:
            entity.draw(screen)
    
    def _handle_playing_input(self, event: pygame.event.Event):
        """Handle playing state input."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.change_state(GameState.PAUSED)
            elif event.key == pygame.K_o:
                self.change_state(GameState.OPTIONS)
            elif event.key == pygame.K_h:
                self.change_state(GameState.HIGH_SCORE) 