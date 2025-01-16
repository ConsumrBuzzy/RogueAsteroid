"""
Menu system for the ECS game.
"""

import pygame
from enum import Enum, auto
from typing import List, Tuple, Callable, Optional, TYPE_CHECKING
from dataclasses import dataclass
from .system import System
from .resources import Resources, GameState, GameSettings
from .audio_manager import play_sound, play_music

if TYPE_CHECKING:
    from .world import World

class MenuState(Enum):
    """Different menu states."""
    MAIN = auto()
    PAUSE = auto()
    OPTIONS = auto()
    HIGH_SCORES = auto()
    GAME_OVER = auto()

@dataclass
class MenuItem:
    """Menu item with text and callback."""
    text: str
    callback: Callable[[], None]
    enabled: bool = True

@dataclass
class MenuResource:
    """Resource for menu state."""
    state: MenuState = MenuState.MAIN
    selected_index: int = 0
    items: List[MenuItem] = None
    title: str = "Rogue Asteroid"
    subtitle: str = ""

    def __post_init__(self):
        if self.items is None:
            self.items = []

class MenuSystem(System):
    """Handles menu rendering and input."""
    
    def __init__(self):
        self.font_large = pygame.font.Font(None, 64)
        self.font_medium = pygame.font.Font(None, 48)
        self.font_small = pygame.font.Font(None, 32)
        
    def update(self, world: 'World', dt: float) -> None:
        menu = world.resources.get(MenuResource)
        if not menu:
            return
            
        # Handle input
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self._select_previous(menu)
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self._select_next(menu)
        elif keys[pygame.K_RETURN] or keys[pygame.K_SPACE]:
            self._activate_item(menu)
    
    def render(self, screen: pygame.Surface, menu: MenuResource) -> None:
        """Render the current menu."""
        # Clear screen
        screen.fill((0, 0, 0))
        
        # Draw title
        title_surf = self.font_large.render(menu.title, True, (255, 255, 255))
        title_rect = title_surf.get_rect(centerx=screen.get_width() // 2, y=50)
        screen.blit(title_surf, title_rect)
        
        # Draw subtitle if present
        if menu.subtitle:
            sub_surf = self.font_small.render(menu.subtitle, True, (200, 200, 200))
            sub_rect = sub_surf.get_rect(centerx=screen.get_width() // 2, y=title_rect.bottom + 20)
            screen.blit(sub_surf, sub_rect)
        
        # Draw menu items
        start_y = 250
        for i, item in enumerate(menu.items):
            color = (255, 255, 0) if i == menu.selected_index else (255, 255, 255)
            if not item.enabled:
                color = (128, 128, 128)
            
            text_surf = self.font_medium.render(item.text, True, color)
            text_rect = text_surf.get_rect(centerx=screen.get_width() // 2, y=start_y + i * 50)
            screen.blit(text_surf, text_rect)
    
    def _select_previous(self, menu: MenuResource) -> None:
        """Select the previous menu item."""
        menu.selected_index = (menu.selected_index - 1) % len(menu.items)
        play_sound(world.resources, "menu_move")
    
    def _select_next(self, menu: MenuResource) -> None:
        """Select the next menu item."""
        menu.selected_index = (menu.selected_index + 1) % len(menu.items)
        play_sound(world.resources, "menu_move")
    
    def _activate_item(self, menu: MenuResource) -> None:
        """Activate the selected menu item."""
        if 0 <= menu.selected_index < len(menu.items):
            item = menu.items[menu.selected_index]
            if item.enabled:
                play_sound(world.resources, "menu_select")
                item.callback()

def create_main_menu(world: 'World') -> None:
    """Create the main menu."""
    menu = MenuResource(
        state=MenuState.MAIN,
        title="Rogue Asteroid",
        items=[
            MenuItem("New Game", lambda: start_game(world)),
            MenuItem("High Scores", lambda: show_high_scores(world)),
            MenuItem("Options", lambda: show_options(world)),
            MenuItem("Quit", lambda: quit_game(world))
        ]
    )
    world.resources.add(menu)
    play_music(world.resources, "menu")

def create_pause_menu(world: 'World') -> None:
    """Create the pause menu."""
    menu = MenuResource(
        state=MenuState.PAUSE,
        title="Paused",
        items=[
            MenuItem("Resume", lambda: resume_game(world)),
            MenuItem("Options", lambda: show_options(world)),
            MenuItem("Main Menu", lambda: return_to_main(world))
        ]
    )
    world.resources.add(menu)

def create_options_menu(world: 'World') -> None:
    """Create the options menu."""
    settings = world.resources.get(GameSettings)
    if not settings:
        return
        
    menu = MenuResource(
        state=MenuState.OPTIONS,
        title="Options",
        items=[
            MenuItem(
                f"Sound: {'ON' if settings.sound_enabled else 'OFF'}",
                lambda: toggle_sound(world)
            ),
            MenuItem(
                f"Music Volume: {int(settings.music_volume * 100)}%",
                lambda: adjust_music_volume(world)
            ),
            MenuItem(
                f"SFX Volume: {int(settings.sfx_volume * 100)}%",
                lambda: adjust_sfx_volume(world)
            ),
            MenuItem("Back", lambda: menu_back(world))
        ]
    )
    world.resources.add(menu)

def create_game_over_menu(world: 'World', score: int) -> None:
    """Create the game over menu."""
    menu = MenuResource(
        state=MenuState.GAME_OVER,
        title="Game Over",
        subtitle=f"Final Score: {score}",
        items=[
            MenuItem("Try Again", lambda: start_game(world)),
            MenuItem("Main Menu", lambda: return_to_main(world))
        ]
    )
    world.resources.add(menu)
    play_music(world.resources, "game_over")
