"""Menu service for game menu management."""
from typing import Dict, Optional, List, Tuple, Callable
import pygame
from .ui_service import UIService
from .state_service import GameState, StateService

class MenuItem:
    """A menu item with text and callback."""
    def __init__(self, text: str, callback: Callable[[], None], position: Tuple[int, int]):
        self.text = text
        self.callback = callback
        self.selected = False
        self.position = position

class Menu:
    """A menu with title and items."""
    def __init__(self, title: str):
        self.title = title
        self.items: List[MenuItem] = []
        self._selected_index = 0
        self._base_y = 200  # Starting Y position for first item
        self._y_spacing = 50  # Spacing between items
        
    def add_item(self, text: str, callback: Callable[[], None]) -> None:
        """Add an item to the menu.
        
        Args:
            text: Text to display
            callback: Function to call when selected
        """
        position = (400, self._base_y + len(self.items) * self._y_spacing)
        item = MenuItem(text, callback, position)
        if not self.items:  # First item is selected by default
            item.selected = True
        self.items.append(item)
        
    def select_next(self) -> None:
        """Select the next item in the menu."""
        if not self.items:
            return
        self.items[self._selected_index].selected = False
        self._selected_index = (self._selected_index + 1) % len(self.items)
        self.items[self._selected_index].selected = True
        
    def select_previous(self) -> None:
        """Select the previous item in the menu."""
        if not self.items:
            return
        self.items[self._selected_index].selected = False
        self._selected_index = (self._selected_index - 1) % len(self.items)
        self.items[self._selected_index].selected = True
        
    def execute_selected(self) -> None:
        """Execute the callback of the selected item."""
        if not self.items:
            return
        self.items[self._selected_index].callback()
        
    def clear(self) -> None:
        """Clear all items from the menu."""
        self.items.clear()
        self._selected_index = 0

class MenuService:
    """Service for managing game menus.
    
    Provides:
    - Menu creation and management
    - Menu navigation
    - Menu rendering
    - Input handling
    """
    
    def __init__(self, ui_service: UIService, state_service: StateService):
        """Initialize the menu service.
        
        Args:
            ui_service: UI service for rendering
            state_service: State service for state management
        """
        self._ui_service = ui_service
        self._state_service = state_service
        self._menus: Dict[GameState, Menu] = {}
        self._current_menu: Optional[Menu] = None
        
        # Create default menus
        self._create_menus()
        
        # Set initial menu based on current state
        self.set_current_menu(self._state_service.get_current_state())
        
        # Get input service and register handlers
        from .input_service import InputService, InputAction
        input_service = InputService()  # Get singleton instance
        input_service.add_handler(InputAction.MENU_UP, self.navigate_up)
        input_service.add_handler(InputAction.MENU_DOWN, self.navigate_down)
        input_service.add_handler(InputAction.MENU_SELECT, self.select)
        input_service.add_handler(InputAction.MENU_BACK, lambda: self._change_state(GameState.MAIN_MENU))
        
        # Get render service and add menu to UI layer
        from .render_service import RenderService
        render_service = RenderService()  # Get singleton instance
        render_service.add_to_layer("ui", self)
        
        print("MenuService initialized")
        
    def _create_menus(self) -> None:
        """Create default game menus."""
        # Main menu
        main_menu = Menu("Main Menu")
        main_menu.add_item("Start Game", lambda: self._change_state(GameState.PLAYING))
        main_menu.add_item("High Scores", lambda: self._change_state(GameState.HIGH_SCORE))
        main_menu.add_item("Options", lambda: self._change_state(GameState.OPTIONS))
        main_menu.add_item("Quit", self._quit_game)
        self._menus[GameState.MAIN_MENU] = main_menu
        
        # Options menu
        options_menu = Menu("Options")
        options_menu.add_item("Back", lambda: self._change_state(GameState.MAIN_MENU))
        self._menus[GameState.OPTIONS] = options_menu
        
        # High score menu
        high_score_menu = Menu("High Scores")
        high_score_menu.add_item("Back", lambda: self._change_state(GameState.MAIN_MENU))
        self._menus[GameState.HIGH_SCORE] = high_score_menu
        
        # Game over menu
        game_over_menu = Menu("Game Over")
        game_over_menu.add_item("Retry", lambda: self._change_state(GameState.PLAYING))
        game_over_menu.add_item("Main Menu", lambda: self._change_state(GameState.MAIN_MENU))
        self._menus[GameState.GAME_OVER] = game_over_menu
        
    def set_current_menu(self, state: GameState) -> None:
        """Set the current menu based on game state.
        
        Args:
            state: Game state to show menu for
        """
        self._current_menu = self._menus.get(state)
        
    def navigate_up(self) -> None:
        """Navigate to previous menu item."""
        if self._current_menu:
            self._current_menu.select_previous()
            
    def navigate_down(self) -> None:
        """Navigate to next menu item."""
        if self._current_menu:
            self._current_menu.select_next()
            
    def select(self) -> None:
        """Select current menu item."""
        if self._current_menu:
            self._current_menu.execute_selected()
            
    def update(self, dt: float) -> None:
        """Update menu state.
        
        Args:
            dt: Delta time in seconds
        """
        if self._current_menu:
            # Draw menu title
            self._ui_service.draw_text(
                self._current_menu.title,
                (400, 100),
                font_size=48,
                color=(255, 255, 255),
                centered=True
            )
            
            # Draw menu items
            for item in self._current_menu.items:
                color = (255, 165, 0) if item.selected else (255, 255, 255)
                self._ui_service.draw_text(
                    item.text,
                    item.position,
                    font_size=36,
                    color=color,
                    centered=True
                )
                
    def clear(self) -> None:
        """Clear all menus."""
        for menu in self._menus.values():
            menu.clear()
        self._current_menu = None
        
    def _change_state(self, state: GameState) -> None:
        """Change game state.
        
        Args:
            state: State to change to
        """
        self._state_service.change_state(state)
        
    def _quit_game(self) -> None:
        """Quit the game."""
        pygame.event.post(pygame.event.Event(pygame.QUIT))
        
    def cleanup(self) -> None:
        """Clean up the service."""
        self.clear()
        self._menus.clear()
        print("MenuService cleaned up") 
        
    def draw(self, screen: pygame.Surface) -> None:
        """Draw the menu on screen.
        
        Args:
            screen: Pygame surface to render to
        """
        if self._current_menu:
            # Draw menu title
            self._ui_service.draw_text(
                self._current_menu.title,
                (400, 100),
                font_size=48,
                color=(255, 255, 255),
                centered=True
            )
            
            # Draw menu items
            for item in self._current_menu.items:
                color = (255, 165, 0) if item.selected else (255, 255, 255)
                self._ui_service.draw_text(
                    item.text,
                    item.position,
                    font_size=36,
                    color=color,
                    centered=True
                ) 