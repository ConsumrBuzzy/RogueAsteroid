"""Menu service for managing game menus."""
from typing import Dict, List, Optional, Callable
import pygame
from core.game_states import GameState
from .ui_service import UIService
from .state_service import StateService

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
    
    def __init__(self, ui_service: UIService, state_service: StateService):
        """Initialize the menu service.
        
        Args:
            ui_service: UI service for rendering
            state_service: State service for managing game state
        """
        self._ui_service = ui_service
        self._state_service = state_service
        self._menus: Dict[GameState, Menu] = {}
        self._current_menu: Optional[Menu] = None
        
        # Create menus
        self._create_main_menu()
        self._create_pause_menu()
        self._create_game_over_menu()
        self._create_options_menu()
        self._create_high_scores_menu()
        
        # Set initial menu based on current state
        current_state = self._state_service.get_current_state()
        if current_state in self._menus:
            self._current_menu = self._menus[current_state]
            if self._current_menu.items:
                self._current_menu.items[0].selected = True
                
        print("MenuService initialized")
        
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
        
    def update(self, dt: float) -> None:
        """Update menu state.
        
        Args:
            dt: Delta time in seconds
        """
        # Menu state updates will go here
        pass
        
    def draw(self) -> None:
        """Draw the current menu."""
        if not self._current_menu:
            return
            
        # Draw menu title centered at y=100
        self._ui_service.draw_text(
            self._current_menu.title,
            (400, 100),  # Centered horizontally
            font_size=48,
            color=(255, 255, 255),
            center=True
        )
        
        # Draw menu items
        for item in self._current_menu.items:
            color = (255, 255, 0) if item.selected else (255, 255, 255)
            self._ui_service.draw_text(
                item.text,
                item.position,
                font_size=36,
                color=color,
                center=True
            )
            
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
            
    def cleanup(self) -> None:
        """Clean up the service."""
        self._menus.clear()
        self._current_menu = None
        print("MenuService cleaned up") 