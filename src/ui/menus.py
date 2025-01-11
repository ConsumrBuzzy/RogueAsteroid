"""Menu system for game UI."""
import pygame
from typing import List, Tuple, Callable, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from src.core.game import Game

class MenuItem:
    """Menu item with text and action."""
    
    def __init__(self, text: str, action: Callable[[], None],
                 font_size: int = 36, color: Tuple[int, int, int] = (255, 255, 255)):
        self.text = text
        self.action = action
        self.font = pygame.font.Font(None, font_size)
        self.color = color
        self.hover_color = (255, 165, 0)  # Orange
        self.is_selected = False
        
        # Create text surfaces
        self.text_surface = self.font.render(text, True, self.color)
        self.hover_surface = self.font.render(text, True, self.hover_color)
        self.rect = self.text_surface.get_rect()
    
    def draw(self, screen: pygame.Surface, pos: Tuple[int, int]) -> None:
        """Draw menu item at position."""
        self.rect.center = pos
        screen.blit(
            self.hover_surface if self.is_selected else self.text_surface,
            self.rect
        )
    
    def handle_mouse(self, mouse_pos: Tuple[int, int]) -> bool:
        """Handle mouse interaction. Returns True if clicked."""
        self.is_selected = self.rect.collidepoint(mouse_pos)
        return self.is_selected and pygame.mouse.get_pressed()[0]

class Menu:
    """Base menu class."""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.spacing = 50  # Pixels between items
    
    def update(self) -> None:
        """Update menu state."""
        mouse_pos = pygame.mouse.get_pos()
        
        # Handle mouse hover
        for item in self.items:
            if item.handle_mouse(mouse_pos):
                item.action()
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle keyboard input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
                self._update_selection()
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
                self._update_selection()
            elif event.key == pygame.K_RETURN:
                self.items[self.selected_index].action()
    
    def _update_selection(self) -> None:
        """Update selected state of menu items."""
        for i, item in enumerate(self.items):
            item.is_selected = i == self.selected_index
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw menu items."""
        screen_center_x = screen.get_width() // 2
        start_y = screen.get_height() // 2 - (len(self.items) * self.spacing) // 2
        
        for i, item in enumerate(self.items):
            pos = (screen_center_x, start_y + i * self.spacing)
            item.draw(screen, pos)

class MainMenu(Menu):
    """Main game menu."""
    
    def __init__(self, game: 'Game'):
        super().__init__(game)
        
        # Create menu items
        self.items = [
            MenuItem('Start Game', self._start_game),
            MenuItem('Options', self._show_options),
            MenuItem('Quit', self._quit_game)
        ]
        self._update_selection()
    
    def _start_game(self) -> None:
        """Start new game."""
        self.game.state = self.game.GameState.PLAYING
        self.game.reset_game()
    
    def _show_options(self) -> None:
        """Show options menu."""
        self.game.state = self.game.GameState.OPTIONS
    
    def _quit_game(self) -> None:
        """Quit the game."""
        self.game.running = False

class OptionsMenu(Menu):
    """Options menu for game settings."""
    
    def __init__(self, game: 'Game'):
        super().__init__(game)
        
        # Create menu items
        self.items = [
            MenuItem('Controls: ' + self.game.settings['controls']['scheme'],
                    self._toggle_controls),
            MenuItem('Back', self._back_to_main)
        ]
        self._update_selection()
    
    def _toggle_controls(self) -> None:
        """Toggle between control schemes."""
        current = self.game.settings['controls']['scheme']
        new_scheme = 'wasd' if current == 'arrows' else 'arrows'
        self.game.settings['controls']['scheme'] = new_scheme
        
        # Update menu text
        self.items[0].text = f'Controls: {new_scheme}'
        self.items[0].text_surface = self.items[0].font.render(
            self.items[0].text, True, self.items[0].color
        )
        self.items[0].hover_surface = self.items[0].font.render(
            self.items[0].text, True, self.items[0].hover_color
        )
    
    def _back_to_main(self) -> None:
        """Return to main menu."""
        self.game.state = self.game.GameState.MENU 