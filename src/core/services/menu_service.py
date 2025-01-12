"""Menu service for managing game menus."""
from typing import Dict, List, Optional, Callable
import pygame
from ..state.game_states import GameState
from .ui_service import UIService
from .state_service import StateService
from .input_service import InputAction

class MenuItem:
    """A menu item with text and callback."""
    def __init__(self, text: str, callback: Callable, position: tuple[int, int]):
        self.text = text
        self.callback = callback
        self.position = position
        self.selected = False

class Menu:
    """A menu with items and selection."""
    def __init__(self, title: str):
        self.title = title
        self.items: List[MenuItem] = []
        self._selected_index = 0
        self._base_y = 200  # Base Y position for first item
        self._spacing = 50   # Spacing between items
        
    def add_item(self, text: str, callback: Callable) -> None:
        """Add an item to the menu."""
        # Calculate position - centered horizontally, stacked vertically
        x = 400  # Center of screen
        y = self._base_y + len(self.items) * self._spacing
        self.items.append(MenuItem(text, callback, (x, y)))
        
        # If this is the first item, select it
        if len(self.items) == 1:
            self.items[0].selected = True
        
    def select_next(self) -> None:
        """Select the next item."""
        if not self.items:
            return
        self.items[self._selected_index].selected = False
        self._selected_index = (self._selected_index + 1) % len(self.items)
        self.items[self._selected_index].selected = True
        
    def select_previous(self) -> None:
        """Select the previous item."""
        if not self.items:
            return
        self.items[self._selected_index].selected = False
        self._selected_index = (self._selected_index - 1) % len(self.items)
        self.items[self._selected_index].selected = True
        
    def execute_selected(self) -> None:
        """Execute the selected item's callback."""
        if not self.items:
            return
        self.items[self._selected_index].callback()
        
    def clear(self) -> None:
        """Clear all items."""
        self.items.clear()
        self._selected_index = 0

class MenuService:
    """Service for managing game menus.
    
    Provides:
    - Menu creation and management
    - Menu navigation
    - Menu rendering
    """
    
    def __init__(self, ui_service: UIService, state_service: StateService, input_service = None):
        """Initialize the menu service.
        
        Args:
            ui_service: UI service for rendering
            state_service: State service for managing game state
            input_service: Optional input service for handling menu input
            
        Raises:
            ValueError: If required services are not provided
            RuntimeError: If state service is not ready
        """
        if not ui_service:
            raise ValueError("UI service is required")
        if not state_service:
            raise ValueError("State service is required")
            
        if not state_service.is_ready():
            raise RuntimeError("State service must be ready")
            
        self._ui_service = ui_service
        self._state_service = state_service
        self._input_service = input_service
        self._menus: Dict[GameState, Menu] = {}
        self._current_menu: Optional[Menu] = None
        
        try:
            # Create menus
            self._create_main_menu()
            self._create_pause_menu()
            self._create_game_over_menu()
            self._create_options_menu()
            self._create_high_scores_menu()
            
            # Subscribe to state changes with a unique ID
            self._state_service.subscribe('menu_service', self._on_state_changed)
            
            # Register input handlers if input service is provided
            if self._input_service:
                self._input_service.add_handler(InputAction.MENU_UP, lambda: self.handle_input("MENU_UP"))
                self._input_service.add_handler(InputAction.MENU_DOWN, lambda: self.handle_input("MENU_DOWN"))
                self._input_service.add_handler(InputAction.MENU_SELECT, lambda: self.handle_input("MENU_SELECT"))
                self._input_service.add_handler(InputAction.MENU_BACK, lambda: self.handle_input("MENU_BACK"))
            
            print("MenuService initialized")
            
        except Exception as e:
            print(f"Error initializing MenuService: {e}")
            raise
            
    def _create_main_menu(self) -> None:
        """Create the main menu."""
        menu = Menu("ROGUE ASTEROID")
        menu.add_item("Start Game", lambda: self._state_service.change_state(GameState.PLAYING))
        menu.add_item("Options", lambda: self._state_service.change_state(GameState.OPTIONS))
        menu.add_item("High Scores", lambda: self._state_service.change_state(GameState.HIGH_SCORES))
        menu.add_item("Exit", lambda: self._state_service.change_state(GameState.QUIT))
        self._menus[GameState.MAIN_MENU] = menu
        
    def _create_pause_menu(self) -> None:
        """Create the pause menu."""
        menu = Menu("PAUSED")
        menu.add_item("Resume", lambda: self._state_service.change_state(GameState.PLAYING))
        menu.add_item("Options", lambda: self._state_service.change_state(GameState.OPTIONS))
        menu.add_item("Main Menu", lambda: self._state_service.change_state(GameState.MAIN_MENU))
        self._menus[GameState.PAUSED] = menu
        
    def _create_game_over_menu(self) -> None:
        """Create the game over menu."""
        menu = Menu("GAME OVER")
        menu.add_item("Play Again", lambda: self._state_service.change_state(GameState.PLAYING))
        menu.add_item("Main Menu", lambda: self._state_service.change_state(GameState.MAIN_MENU))
        self._menus[GameState.GAME_OVER] = menu
        
    def _create_options_menu(self) -> None:
        """Create the options menu."""
        menu = Menu("OPTIONS")
        menu.add_item("Back", lambda: self._state_service.change_state(GameState.MAIN_MENU))
        self._menus[GameState.OPTIONS] = menu
        
    def _create_high_scores_menu(self) -> None:
        """Create the high scores menu."""
        menu = Menu("HIGH SCORES")
        menu.add_item("Back", lambda: self._state_service.change_state(GameState.MAIN_MENU))
        self._menus[GameState.HIGH_SCORES] = menu
        
    def _on_state_changed(self, old_state: Optional[GameState], new_state: Optional[GameState]) -> None:
        """Handle state changes.
        
        Args:
            old_state: Previous game state
            new_state: New game state
        """
        try:
            # Update current menu based on new state
            if new_state in self._menus:
                self._current_menu = self._menus[new_state]
                print(f"Menu changed to: {new_state}")
            else:
                self._current_menu = None
                
        except Exception as e:
            print(f"Error handling state change: {e}")
            
    def update(self, dt: float) -> None:
        """Update current menu.
        
        Args:
            dt: Delta time in seconds
        """
        if self._current_menu:
            self._current_menu.update(dt)
            
    def draw(self) -> None:
        """Draw current menu."""
        if self._current_menu:
            self._current_menu.draw(self._ui_service)
            
    def handle_input(self, action: str) -> None:
        """Handle menu input.
        
        Args:
            action: Input action to handle
        """
        if not self._current_menu:
            return
            
        if action == "MENU_UP":
            self._current_menu.select_previous()
        elif action == "MENU_DOWN":
            self._current_menu.select_next()
        elif action == "MENU_SELECT":
            self._current_menu.execute_selected()
        elif action == "MENU_BACK":
            # If we're not in the main menu, go back to it
            if self._state_service.get_current_state() != GameState.MAIN_MENU:
                self._state_service.change_state(GameState.MAIN_MENU)
            
    def cleanup(self) -> None:
        """Clean up the menu service."""
        try:
            # Unsubscribe from state changes
            if hasattr(self._state_service, 'unsubscribe'):
                self._state_service.unsubscribe('menu_service')
            
            # Remove input handlers
            if self._input_service:
                self._input_service.remove_handler(InputAction.MENU_UP)
                self._input_service.remove_handler(InputAction.MENU_DOWN)
                self._input_service.remove_handler(InputAction.MENU_SELECT)
                self._input_service.remove_handler(InputAction.MENU_BACK)
            
            # Clear menus
            self._menus.clear()
            self._current_menu = None
            
            print("MenuService cleaned up")
            
        except Exception as e:
            print(f"Error cleaning up MenuService: {e}")
            # Continue cleanup despite errors 