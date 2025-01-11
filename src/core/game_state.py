"""Game state management system."""
from enum import Enum, auto
from typing import Optional, Dict, Any, Callable
import pygame

class GameState(Enum):
    """Game states enumeration."""
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    GAME_OVER = auto()
    HIGH_SCORE = auto()

class StateManager:
    """Manages game state transitions and UI."""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.current_state = GameState.MAIN_MENU
        self.previous_state: Optional[GameState] = None
        
        # State transition handlers
        self.state_handlers: Dict[GameState, Callable[[], None]] = {
            GameState.MAIN_MENU: self._handle_main_menu,
            GameState.PLAYING: self._handle_playing,
            GameState.PAUSED: self._handle_paused,
            GameState.GAME_OVER: self._handle_game_over,
            GameState.HIGH_SCORE: self._handle_high_score
        }
        
        # UI elements
        self.fonts = {
            'large': pygame.font.Font(None, 74),
            'medium': pygame.font.Font(None, 48),
            'small': pygame.font.Font(None, 36)
        }
    
    def change_state(self, new_state: GameState) -> None:
        """Change to a new game state."""
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Handle state entry actions
        if new_state == GameState.PLAYING and self.previous_state == GameState.MAIN_MENU:
            self.game.reset_game()
    
    def handle_input(self, event: pygame.event.Event) -> bool:
        """Handle input for current state. Returns True if game should quit."""
        if event.type == pygame.QUIT:
            return True
            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                if self.current_state == GameState.PLAYING:
                    self.change_state(GameState.PAUSED)
                elif self.current_state == GameState.PAUSED:
                    self.change_state(GameState.PLAYING)
                elif self.current_state in [GameState.MAIN_MENU, GameState.HIGH_SCORE]:
                    return True
            
            elif event.key == pygame.K_RETURN:
                if self.current_state == GameState.MAIN_MENU:
                    self.change_state(GameState.PLAYING)
                elif self.current_state == GameState.GAME_OVER:
                    self.change_state(GameState.MAIN_MENU)
                elif self.current_state == GameState.HIGH_SCORE:
                    self.change_state(GameState.MAIN_MENU)
        
        return False
    
    def update(self) -> None:
        """Update current state."""
        handler = self.state_handlers.get(self.current_state)
        if handler:
            handler()
    
    def _handle_main_menu(self) -> None:
        """Handle main menu state."""
        pass  # Menu items are drawn in draw method
    
    def _handle_playing(self) -> None:
        """Handle playing state."""
        self.game.update_entities()
        self.game.handle_collisions()
        
        # Check for level completion
        if not self.game.asteroids and self.game.ship:
            self.game.level += 1
            self.game.spawn_asteroid_wave()
    
    def _handle_paused(self) -> None:
        """Handle paused state."""
        pass  # Game is frozen
    
    def _handle_game_over(self) -> None:
        """Handle game over state."""
        pass  # Wait for input to return to menu
    
    def _handle_high_score(self) -> None:
        """Handle high score state."""
        pass  # Display high scores
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw current state UI."""
        if self.current_state == GameState.MAIN_MENU:
            self._draw_main_menu(screen)
        elif self.current_state == GameState.PLAYING:
            self._draw_game(screen)
        elif self.current_state == GameState.PAUSED:
            self._draw_game(screen)
            self._draw_pause_overlay(screen)
        elif self.current_state == GameState.GAME_OVER:
            self._draw_game_over(screen)
        elif self.current_state == GameState.HIGH_SCORE:
            self._draw_high_scores(screen)
    
    def _draw_main_menu(self, screen: pygame.Surface) -> None:
        """Draw main menu screen."""
        # Title
        title = self.fonts['large'].render('ROGUE ASTEROID', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.game.width/2, self.game.height/3))
        screen.blit(title, title_rect)
        
        # Menu items
        start_text = self.fonts['medium'].render('Press ENTER to Start', True, (255, 255, 255))
        start_rect = start_text.get_rect(center=(self.game.width/2, self.game.height*2/3))
        screen.blit(start_text, start_rect)
        
        quit_text = self.fonts['small'].render('Press ESC to Quit', True, (255, 255, 255))
        quit_rect = quit_text.get_rect(center=(self.game.width/2, self.game.height*2/3 + 50))
        screen.blit(quit_text, quit_rect)
    
    def _draw_game(self, screen: pygame.Surface) -> None:
        """Draw game screen."""
        # Draw all entities
        for entity in self.game.entities:
            render = entity.get_component('render')
            if render:
                render.draw(screen)
        
        # Draw HUD
        self._draw_hud(screen)
    
    def _draw_pause_overlay(self, screen: pygame.Surface) -> None:
        """Draw pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.game.width, self.game.height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Pause text
        text = self.fonts['large'].render('PAUSED', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.game.width/2, self.game.height/2))
        screen.blit(text, text_rect)
        
        resume_text = self.fonts['small'].render('Press ESC to Resume', True, (255, 255, 255))
        resume_rect = resume_text.get_rect(center=(self.game.width/2, self.game.height/2 + 50))
        screen.blit(resume_text, resume_rect)
    
    def _draw_game_over(self, screen: pygame.Surface) -> None:
        """Draw game over screen."""
        text = self.fonts['large'].render('GAME OVER', True, (255, 0, 0))
        text_rect = text.get_rect(center=(self.game.width/2, self.game.height/2))
        screen.blit(text, text_rect)
        
        score_text = self.fonts['medium'].render(f'Final Score: {self.game.score}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.game.width/2, self.game.height/2 + 50))
        screen.blit(score_text, score_rect)
        
        continue_text = self.fonts['small'].render('Press ENTER to Continue', True, (255, 255, 255))
        continue_rect = continue_text.get_rect(center=(self.game.width/2, self.game.height/2 + 100))
        screen.blit(continue_text, continue_rect)
    
    def _draw_high_scores(self, screen: pygame.Surface) -> None:
        """Draw high scores screen."""
        title = self.fonts['large'].render('HIGH SCORES', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.game.width/2, self.game.height/4))
        screen.blit(title, title_rect)
    
    def _draw_hud(self, screen: pygame.Surface) -> None:
        """Draw heads-up display."""
        # Score
        score_text = self.fonts['small'].render(f'Score: {self.game.score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        # Lives
        lives_text = self.fonts['small'].render(f'Lives: {self.game.lives}', True, (255, 255, 255))
        screen.blit(lives_text, (10, 50))
        
        # Level
        level_text = self.fonts['small'].render(f'Level: {self.game.level}', True, (255, 255, 255))
        screen.blit(level_text, (self.game.width - 120, 10)) 