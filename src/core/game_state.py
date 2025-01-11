"""Game state management system."""
from enum import Enum, auto
from typing import Optional, Dict, Any, Callable
import pygame

class GameState(Enum):
    """Game states enumeration."""
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    OPTIONS = auto()
    GAME_OVER = auto()
    HIGH_SCORE = auto()
    HIGH_SCORE_ENTRY = auto()

class StateManager:
    """Manages game state transitions and UI."""
    
    def __init__(self, game: 'Game'):
        self.game = game
        self.current_state = GameState.MAIN_MENU
        self.previous_state: Optional[GameState] = None
        self.player_name = ""  # For high score entry
        
        # State transition handlers
        self.state_handlers: Dict[GameState, Callable[[], None]] = {
            GameState.MAIN_MENU: self._handle_main_menu,
            GameState.PLAYING: self._handle_playing,
            GameState.PAUSED: self._handle_paused,
            GameState.OPTIONS: self._handle_options,
            GameState.GAME_OVER: self._handle_game_over,
            GameState.HIGH_SCORE: self._handle_high_score,
            GameState.HIGH_SCORE_ENTRY: self._handle_high_score_entry
        }
        
        # UI elements
        self.fonts = {
            'large': pygame.font.Font(None, 74),
            'medium': pygame.font.Font(None, 48),
            'small': pygame.font.Font(None, 36)
        }
        
        # Options menu settings
        self.selected_option = 0
        self.options = [
            ('Controls', ['Arrows', 'WASD']),
            ('Back', None)
        ]
    
    def change_state(self, new_state: GameState) -> None:
        """Change to a new game state."""
        if new_state == self.current_state:
            return
            
        self.previous_state = self.current_state
        self.current_state = new_state
        
        # Handle state entry actions
        if new_state == GameState.PLAYING:
            if self.previous_state == GameState.MAIN_MENU:
                self.game.reset_game()
            elif self.previous_state == GameState.PAUSED:
                # Just unpause
                pass
        elif new_state == GameState.HIGH_SCORE_ENTRY:
            self.player_name = ""
    
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
                elif self.current_state == GameState.OPTIONS:
                    if self.previous_state == GameState.PAUSED:
                        self.change_state(GameState.PAUSED)
                    else:
                        self.change_state(GameState.MAIN_MENU)
                elif self.current_state == GameState.MAIN_MENU:
                    return True
                elif self.current_state == GameState.HIGH_SCORE:
                    self.change_state(GameState.MAIN_MENU)
            
            elif event.key == pygame.K_p and self.current_state == GameState.PLAYING:
                self.change_state(GameState.PAUSED)
            
            elif event.key == pygame.K_r and self.current_state == GameState.PAUSED:
                self.change_state(GameState.PLAYING)
            
            elif event.key == pygame.K_o:
                if self.current_state in [GameState.MAIN_MENU, GameState.PAUSED]:
                    self.change_state(GameState.OPTIONS)
            
            elif event.key == pygame.K_h and self.current_state == GameState.MAIN_MENU:
                self.change_state(GameState.HIGH_SCORE)
            
            elif event.key == pygame.K_m and self.current_state == GameState.PAUSED:
                self.change_state(GameState.MAIN_MENU)
                self.game.reset_game()
            
            elif event.key == pygame.K_RETURN:
                if self.current_state == GameState.MAIN_MENU:
                    self.change_state(GameState.PLAYING)
                elif self.current_state == GameState.OPTIONS:
                    if self.selected_option == len(self.options) - 1:  # Back option
                        self.change_state(self.previous_state or GameState.MAIN_MENU)
                elif self.current_state == GameState.GAME_OVER:
                    self.change_state(GameState.MAIN_MENU)
                elif self.current_state == GameState.HIGH_SCORE:
                    self.change_state(GameState.MAIN_MENU)
            
            elif self.current_state == GameState.OPTIONS:
                self._handle_options_input(event)
        
        return False
    
    def _handle_options_input(self, event: pygame.event.Event) -> None:
        """Handle input in options menu."""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.options)
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.options)
        elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
            option, values = self.options[self.selected_option]
            if values:  # If this option has multiple values
                current_value = self.game.settings['controls']['scheme'].lower()
                new_value = values[1].lower() if current_value == values[0].lower() else values[0].lower()
                self.game.settings['controls']['scheme'] = new_value
    
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
        if not self.game.ship:
            return  # Don't update if ship is destroyed
            
        self.game.update_entities()
        self.game.handle_collisions()
        
        # Check for level completion
        if len(self.game.asteroids) == 0:  # Only progress if all asteroids are destroyed
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
    
    def _handle_high_score_entry(self) -> None:
        """Handle high score entry state."""
        pass  # Handle in input method
    
    def _handle_options(self) -> None:
        """Handle options menu state."""
        pass  # Options are handled in input method
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw current state UI."""
        if self.current_state == GameState.MAIN_MENU:
            self._draw_main_menu(screen)
        elif self.current_state == GameState.PLAYING:
            self._draw_game(screen)
        elif self.current_state == GameState.PAUSED:
            self._draw_game(screen)
            self._draw_pause_overlay(screen)
        elif self.current_state == GameState.OPTIONS:
            self._draw_options(screen)
        elif self.current_state == GameState.GAME_OVER:
            self._draw_game_over(screen)
        elif self.current_state == GameState.HIGH_SCORE:
            self._draw_high_scores(screen)
        elif self.current_state == GameState.HIGH_SCORE_ENTRY:
            self._draw_high_score_entry(screen)
    
    def _draw_main_menu(self, screen: pygame.Surface) -> None:
        """Draw main menu screen."""
        # Title
        title = self.fonts['large'].render('ROGUE ASTEROID', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.game.width/2, self.game.height/3))
        screen.blit(title, title_rect)
        
        # Menu items
        menu_items = [
            ('Press ENTER to Start', 'medium'),
            ('H - High Scores', 'small'),
            ('O - Options', 'small'),
            ('ESC - Quit', 'small')
        ]
        
        for i, (text, size) in enumerate(menu_items):
            item = self.fonts[size].render(text, True, (255, 255, 255))
            item_rect = item.get_rect(center=(self.game.width/2, self.game.height*2/3 + i * 40))
            screen.blit(item, item_rect)
    
    def _draw_options(self, screen: pygame.Surface) -> None:
        """Draw options menu screen."""
        # Title
        title = self.fonts['large'].render('OPTIONS', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.game.width/2, self.game.height/4))
        screen.blit(title, title_rect)
        
        # Options
        for i, (option, values) in enumerate(self.options):
            color = (255, 255, 0) if i == self.selected_option else (255, 255, 255)
            
            if values:  # Option with multiple values
                current_value = self.game.settings['controls']['scheme']
                text = f"{option}: < {current_value} >"
            else:  # Simple option (like Back)
                text = option
                
            option_text = self.fonts['medium'].render(text, True, color)
            option_rect = option_text.get_rect(
                center=(self.game.width/2, self.game.height/2 + i * 60)
            )
            screen.blit(option_text, option_rect)
    
    def _draw_pause_overlay(self, screen: pygame.Surface) -> None:
        """Draw pause screen overlay."""
        # Semi-transparent overlay
        overlay = pygame.Surface((self.game.width, self.game.height))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(128)
        screen.blit(overlay, (0, 0))
        
        # Pause text
        text = self.fonts['large'].render('PAUSED', True, (255, 255, 255))
        text_rect = text.get_rect(center=(self.game.width/2, self.game.height/3))
        screen.blit(text, text_rect)
        
        # Menu items
        menu_items = [
            ('R - Resume', 'medium'),
            ('O - Options', 'small'),
            ('M - Main Menu', 'small')
        ]
        
        for i, (text, size) in enumerate(menu_items):
            item = self.fonts[size].render(text, True, (255, 255, 255))
            item_rect = item.get_rect(center=(self.game.width/2, self.game.height/2 + i * 40))
            screen.blit(item, item_rect)
    
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
        # Title
        title = self.fonts['large'].render('HIGH SCORES', True, (255, 255, 255))
        title_rect = title.get_rect(center=(self.game.width/2, self.game.height/4))
        screen.blit(title, title_rect)
        
        # High scores
        scores = self.game.scoring.get_high_scores()
        start_y = self.game.height/2 - len(scores) * 20
        
        for i, score in enumerate(scores):
            text = self.fonts['medium'].render(f"{score['name']}: {score['score']}", True, (255, 255, 255))
            rect = text.get_rect(center=(self.game.width/2, start_y + i * 40))
            screen.blit(text, rect)
        
        # Back instruction
        back_text = self.fonts['small'].render('Press ESC to return', True, (255, 255, 255))
        back_rect = back_text.get_rect(center=(self.game.width/2, self.game.height - 50))
        screen.blit(back_text, back_rect)

    def _draw_high_score_entry(self, screen: pygame.Surface) -> None:
        """Draw high score entry screen."""
        # Title
        title = self.fonts['large'].render('NEW HIGH SCORE!', True, (255, 255, 0))
        title_rect = title.get_rect(center=(self.game.width/2, self.game.height/3))
        screen.blit(title, title_rect)
        
        # Score
        score_text = self.fonts['medium'].render(f'Score: {self.game.score}', True, (255, 255, 255))
        score_rect = score_text.get_rect(center=(self.game.width/2, self.game.height/2))
        screen.blit(score_text, score_rect)
        
        # Name entry
        name_text = self.fonts['medium'].render(f'Name: {self.player_name}_', True, (255, 255, 255))
        name_rect = name_text.get_rect(center=(self.game.width/2, self.game.height/2 + 50))
        screen.blit(name_text, name_rect)
        
        # Instructions
        instr_text = self.fonts['small'].render('Press ENTER when done', True, (255, 255, 255))
        instr_rect = instr_text.get_rect(center=(self.game.width/2, self.game.height/2 + 100))
        screen.blit(instr_text, instr_rect)

    def _draw_game(self, screen: pygame.Surface) -> None:
        """Draw game screen."""
        # Draw all entities
        for entity in self.game.entities:
            if not entity:
                continue
            
            render = entity.get_component('render')
            effects = entity.get_component('effects')
            
            if render and render.visible:
                render.draw(screen)
            
            if effects:
                effects.draw(screen)
        
        # Draw HUD
        self._draw_hud(screen)

    def _draw_hud(self, screen: pygame.Surface) -> None:
        """Draw heads-up display."""
        # Score and multiplier
        score_text = self.fonts['small'].render(f'Score: {self.game.score}', True, (255, 255, 255))
        screen.blit(score_text, (10, 10))
        
        if self.game.scoring.score_multiplier > 1.0:
            mult_text = self.fonts['small'].render(f'x{self.game.scoring.score_multiplier:.1f}', True, (255, 255, 0))
            screen.blit(mult_text, (10, 30))
        
        # Lives
        lives_text = self.fonts['small'].render(f'Lives: {self.game.lives}', True, (255, 255, 255))
        screen.blit(lives_text, (10, 70))
        
        # Level
        level_text = self.fonts['small'].render(f'Level: {self.game.level}', True, (255, 255, 255))
        screen.blit(level_text, (self.game.width - 120, 10)) 