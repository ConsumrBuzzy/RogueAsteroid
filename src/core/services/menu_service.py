"""Menu service for game menu management."""
from typing import Dict, Optional, List, Tuple, Callable
import pygame
from .ui_service import UIService
from .state_service import GameState

class MenuItem:
    """Individual menu item with text and callback."""
    def __init__(self, 
                 text: str,
                 callback: Callable,
                 position: Tuple[int, int],
                 selected: bool = False):
        """Initialize a menu item.
        
        Args:
            text: Display text
            callback: Function to call when selected
            position: (x, y) position on screen
            selected: Whether item is initially selected
        """
        self.text = text
        self.callback = callback
        self.position = position
        self.selected = selected
        self._original_text = text
        
    def select(self) -> None:
        """Select this menu item."""
        self.selected = True
        self.text = f"> {self._original_text} <"
        
    def deselect(self) -> None:
        """Deselect this menu item."""
        self.selected = False
        self.text = self._original_text
        
    def execute(self) -> None:
        """Execute the menu item callback."""
        if self.callback:
            self.callback()

class Menu:
    """Menu containing multiple items."""
    def __init__(self, title: str, items: List[MenuItem]):
        """Initialize a menu.
        
        Args:
            title: Menu title
            items: List of menu items
        """
        self.title = title
        self.items = items
        self._selected_index = 0
        self.items[0].select()
        
    def select_next(self) -> None:
        """Select the next menu item."""
        self.items[self._selected_index].deselect()
        self._selected_index = (self._selected_index + 1) % len(self.items)
        self.items[self._selected_index].select()
        
    def select_previous(self) -> None:
        """Select the previous menu item."""
        self.items[self._selected_index].deselect()
        self._selected_index = (self._selected_index - 1) % len(self.items)
        self.items[self._selected_index].select()
        
    def execute_selected(self) -> None:
        """Execute the currently selected item."""
        self.items[self._selected_index].execute()
        
    def get_selected(self) -> MenuItem:
        """Get the currently selected item.
        
        Returns:
            Currently selected MenuItem
        """
        return self.items[self._selected_index]

class MenuService:
    """Service for game menu management.
    
    Provides:
    - Menu creation and management
    - Menu navigation
    - Menu state handling
    - Menu rendering
    """
    
    def __init__(self, ui_service: UIService):
        """Initialize the menu service.
        
        Args:
            ui_service: UI service for rendering
        """
        self._ui_service = ui_service
        self._menus: Dict[GameState, Menu] = {}
        self._current_menu: Optional[Menu] = None
        print("MenuService initialized")
        
    def create_menu(self, state: GameState, title: str, items: List[MenuItem]) -> None:
        """Create a new menu for a game state.
        
        Args:
            state: Game state this menu is for
            title: Menu title
            items: List of menu items
        """
        menu = Menu(title, items)
        self._menus[state] = menu
        print(f"Created menu for state {state.name}")
        
    def show_menu(self, state: GameState) -> None:
        """Show the menu for a specific state.
        
        Args:
            state: Game state to show menu for
        """
        if menu := self._menus.get(state):
            self._current_menu = menu
            self._update_ui()
            print(f"Showing menu for state {state.name}")
            
    def hide_menu(self) -> None:
        """Hide the current menu."""
        self._current_menu = None
        self._ui_service.clear()
        print("Menu hidden")
        
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle input for the current menu.
        
        Args:
            event: Pygame event to handle
        """
        if not self._current_menu:
            return
            
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_UP, pygame.K_w):
                self._current_menu.select_previous()
                self._update_ui()
            elif event.key in (pygame.K_DOWN, pygame.K_s):
                self._current_menu.select_next()
                self._update_ui()
            elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                self._current_menu.execute_selected()
                
    def _update_ui(self) -> None:
        """Update the UI elements for the current menu."""
        if not self._current_menu:
            return
            
        self._ui_service.clear()
        
        # Add title
        self._ui_service.add_element(
            'menu_title',
            self._current_menu.title,
            (400, 100),  # Centered position
            centered=True,
            font_size=36
        )
        
        # Add items
        for i, item in enumerate(self._current_menu.items):
            self._ui_service.add_element(
                f'menu_item_{i}',
                item.text,
                item.position,
                centered=True,
                selected=item.selected
            )
            
    def clear(self) -> None:
        """Clear all menus."""
        self._menus.clear()
        self._current_menu = None
        self._ui_service.clear()
        print("Menu service cleared") 