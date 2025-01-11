"""State management for the game."""
from enum import Enum, auto
import pygame
from src.core.constants import WHITE, WINDOW_WIDTH, WINDOW_HEIGHT

class GameState(Enum):
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    OPTIONS = auto()
    HIGH_SCORE = auto()

class StateManager:
    def __init__(self, game):
        self.game = game
        self.current_state = GameState.MAIN_MENU
        self.selected_option = 0
        self.menu_options = {
            GameState.MAIN_MENU: ['New Game', 'High Scores', 'Options', 'Quit'],
            GameState.OPTIONS: ['Controls: Arrows', 'Controls: WASD', 'Back'],
            GameState.PAUSED: ['Resume', 'Options', 'Main Menu']
        }

    def change_state(self, new_state):
        if new_state == self.current_state:
            return

        if new_state == GameState.PLAYING:
            if self.current_state == GameState.MAIN_MENU:
                self.game.reset_game()
            elif self.current_state == GameState.PAUSED:
                pass  # Just unpause
        
        self.current_state = new_state
        self.selected_option = 0

    def handle_input(self, event):
        if event.type != pygame.KEYDOWN:
            return

        if self.current_state == GameState.MAIN_MENU:
            self._handle_main_menu_input(event)
        elif self.current_state == GameState.PLAYING:
            self._handle_playing_input(event)
        elif self.current_state == GameState.PAUSED:
            self._handle_pause_input(event)
        elif self.current_state == GameState.OPTIONS:
            self._handle_options_input(event)
        elif self.current_state == GameState.HIGH_SCORE:
            self._handle_high_score_input(event)

    def _handle_main_menu_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options[GameState.MAIN_MENU])
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options[GameState.MAIN_MENU])
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # New Game
                self.change_state(GameState.PLAYING)
            elif self.selected_option == 1:  # High Scores
                self.change_state(GameState.HIGH_SCORE)
            elif self.selected_option == 2:  # Options
                self.change_state(GameState.OPTIONS)
            elif self.selected_option == 3:  # Quit
                self.game.running = False

    def _handle_playing_input(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_p):
            self.change_state(GameState.PAUSED)

    def _handle_pause_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options[GameState.PAUSED])
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options[GameState.PAUSED])
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Resume
                self.change_state(GameState.PLAYING)
            elif self.selected_option == 1:  # Options
                self.change_state(GameState.OPTIONS)
            elif self.selected_option == 2:  # Main Menu
                self.change_state(GameState.MAIN_MENU)
        elif event.key in (pygame.K_ESCAPE, pygame.K_p):
            self.change_state(GameState.PLAYING)

    def _handle_options_input(self, event):
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options[GameState.OPTIONS])
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options[GameState.OPTIONS])
        elif event.key == pygame.K_RETURN:
            if self.selected_option < 2:  # Control scheme selection
                self.game.settings['controls'] = 'arrows' if self.selected_option == 0 else 'wasd'
            else:  # Back
                self.change_state(GameState.MAIN_MENU)
        elif event.key == pygame.K_ESCAPE:
            self.change_state(GameState.MAIN_MENU)

    def _handle_high_score_input(self, event):
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN):
            self.change_state(GameState.MAIN_MENU)

    def draw(self, screen):
        if self.current_state == GameState.MAIN_MENU:
            self._draw_main_menu(screen)
        elif self.current_state == GameState.PLAYING:
            self._draw_game(screen)
        elif self.current_state == GameState.PAUSED:
            self._draw_game(screen)
            self._draw_pause_overlay(screen)
        elif self.current_state == GameState.OPTIONS:
            self._draw_options(screen)
        elif self.current_state == GameState.HIGH_SCORE:
            self._draw_high_scores(screen)

    def _draw_main_menu(self, screen):
        screen.fill((0, 0, 0))  # Black background
        font = pygame.font.Font(None, 64)
        title = font.render("ROGUE ASTEROID", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, 100))

        font = pygame.font.Font(None, 36)
        for i, option in enumerate(self.menu_options[GameState.MAIN_MENU]):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = font.render(option, True, color)
            screen.blit(text, (WINDOW_WIDTH/2 - text.get_width()/2, 300 + i * 50))

    def _draw_game(self, screen):
        screen.fill((0, 0, 0))  # Black background
        
        # Draw all game entities
        for entity in self.game.entities:
            render = entity.get_component('render')
            if render and render.visible and render.vertices:
                render.draw(screen)
            
            # Draw effects if any
            effects = entity.get_component('effects')
            if effects:
                effects.draw(screen)

        # Draw HUD
        font = pygame.font.Font(None, 36)
        score_text = font.render(f"Score: {self.game.score}", True, WHITE)
        screen.blit(score_text, (10, 10))

    def _draw_pause_overlay(self, screen):
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))

        font = pygame.font.Font(None, 48)
        title = font.render("PAUSED", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, 200))

        font = pygame.font.Font(None, 36)
        for i, option in enumerate(self.menu_options[GameState.PAUSED]):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = font.render(option, True, color)
            screen.blit(text, (WINDOW_WIDTH/2 - text.get_width()/2, 300 + i * 50))

    def _draw_options(self, screen):
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 48)
        title = font.render("OPTIONS", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, 100))

        font = pygame.font.Font(None, 36)
        for i, option in enumerate(self.menu_options[GameState.OPTIONS]):
            color = (255, 255, 0) if i == self.selected_option else WHITE
            text = font.render(option, True, color)
            screen.blit(text, (WINDOW_WIDTH/2 - text.get_width()/2, 300 + i * 50))

    def _draw_high_scores(self, screen):
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 48)
        title = font.render("HIGH SCORES", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, 100))

        font = pygame.font.Font(None, 36)
        text = font.render("Press ENTER or ESC to return", True, WHITE)
        screen.blit(text, (WINDOW_WIDTH/2 - text.get_width()/2, 500)) 