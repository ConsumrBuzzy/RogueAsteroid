"""Menu system for the game."""
import pygame
from typing import List, Tuple, Callable
from .constants import WINDOW_WIDTH, WINDOW_HEIGHT, WHITE, BLACK

class MenuItem:
    """Represents a menu item that can be selected."""
    
    def __init__(self, text: str, action: Callable, position: Tuple[int, int]):
        self.text = text
        self.action = action
        self.position = position
        self.selected = False
        self.font = pygame.font.Font(None, 36)
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the menu item."""
        color = (255, 255, 0) if self.selected else WHITE
        text_surface = self.font.render(self.text, True, color)
        rect = text_surface.get_rect(center=self.position)
        surface.blit(text_surface, rect)

class Menu:
    """Base class for all menus."""
    
    def __init__(self, game):
        self.game = game
        self.items: List[MenuItem] = []
        self.selected_index = 0
        self.font = pygame.font.Font(None, 48)
        self.title = ""
    
    def handle_input(self, event: pygame.event.Event) -> None:
        """Handle menu input."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_UP:
                self.selected_index = (self.selected_index - 1) % len(self.items)
            elif event.key == pygame.K_DOWN:
                self.selected_index = (self.selected_index + 1) % len(self.items)
            elif event.key == pygame.K_RETURN:
                self.items[self.selected_index].action()
    
    def update(self) -> None:
        """Update menu state."""
        for i, item in enumerate(self.items):
            item.selected = i == self.selected_index
    
    def draw(self, surface: pygame.Surface) -> None:
        """Draw the menu."""
        surface.fill(BLACK)
        
        # Draw title
        if self.title:
            title_surface = self.font.render(self.title, True, WHITE)
            title_rect = title_surface.get_rect(center=(WINDOW_WIDTH/2, 100))
            surface.blit(title_surface, title_rect)
        
        # Draw items
        for item in self.items:
            item.draw(surface)

class OptionsMenu(Menu):
    """Options menu for game settings."""
    
    def __init__(self, game):
        super().__init__(game)
        self.title = "Options"
        
        # Create menu items
        center_x = WINDOW_WIDTH // 2
        start_y = 200
        spacing = 50
        
        self.items = [
            MenuItem(
                f"Control Scheme: {self.game.settings.get('controls', 'scheme').upper()}",
                self.toggle_control_scheme,
                (center_x, start_y)
            ),
            MenuItem(
                "Back",
                self.back_to_main,
                (center_x, start_y + spacing * 3)
            )
        ]
    
    def toggle_control_scheme(self) -> None:
        """Toggle between control schemes."""
        current = self.game.settings.get('controls', 'scheme')
        new_scheme = 'wasd' if current == 'arrows' else 'arrows'
        self.game.settings.set('controls', 'scheme', new_scheme)
        
        # Update menu item text
        self.items[0].text = f"Control Scheme: {new_scheme.upper()}"
    
    def back_to_main(self) -> None:
        """Return to main menu."""
        self.game.show_main_menu()

class MainMenu(Menu):
    """Main menu of the game."""
    
    def __init__(self, game):
        super().__init__(game)
        self.title = "RogueAsteroid"
        
        # Create menu items
        center_x = WINDOW_WIDTH // 2
        start_y = 200
        spacing = 50
        
        self.items = [
            MenuItem("Play", self.start_game, (center_x, start_y)),
            MenuItem("Options", self.show_options, (center_x, start_y + spacing)),
            MenuItem("Quit", self.quit_game, (center_x, start_y + spacing * 2))
        ]
    
    def start_game(self) -> None:
        """Start the game."""
        self.game.start_game()
    
    def show_options(self) -> None:
        """Show options menu."""
        self.game.show_options()
    
    def quit_game(self) -> None:
        """Quit the game."""
        self.game.running = False 