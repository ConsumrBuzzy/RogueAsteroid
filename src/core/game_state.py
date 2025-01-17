"""State management for the game."""
from enum import Enum, auto
import pygame
from src.core.constants import WHITE, WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.events.event_types import GameStateChangedEvent

class GameState(Enum):
    MAIN_MENU = auto()
    PLAYING = auto()
    PAUSED = auto()
    OPTIONS = auto()
    HIGH_SCORE = auto()
    NEW_HIGH_SCORE = auto()  # For entering name when achieving high score
    GAME_OVER = auto()

class StateManager:
    def __init__(self, game):
        """Initialize the state manager."""
        print("Initializing StateManager")  # Debug info
        self.game = game
        self.current_state = None  # Initialize to None, let Game class set initial state
        self.previous_state = None  # Track previous state for returning from menus
        self.selected_option = 0
        self.menu_options = {
            GameState.MAIN_MENU: ['New Game', 'High Scores', 'Options', 'Quit'],
            GameState.OPTIONS: [f'Control Scheme: {self.game.settings["controls"].upper()}', 'Back'],
            GameState.PAUSED: ['Resume', 'Options', 'Main Menu']
        }
        self.high_score_name = ""  # For new high score entry
    
    def change_state(self, new_state):
        """Change the current game state."""
        if new_state == self.current_state:
            return
            
        old_state = self.current_state
        print(f"Changing state from {old_state} to {new_state}")  # Debug info
        
        # Emit state change event
        self.game.event_manager.emit(GameStateChangedEvent(old_state, new_state))
        
        # Update previous state, but don't track transitions to/from NEW_HIGH_SCORE
        if old_state != GameState.NEW_HIGH_SCORE and new_state != GameState.NEW_HIGH_SCORE:
            self.previous_state = old_state
        
        # Handle state-specific transitions
        if new_state == GameState.PLAYING:
            if old_state == GameState.MAIN_MENU:
                print("Starting new game")  # Debug info
                self.game.reset_game()
            elif old_state == GameState.PAUSED:
                print("Resuming game")  # Debug info
        elif new_state == GameState.GAME_OVER:
            print("Game Over!")  # Debug info
        
        self.current_state = new_state
        self.selected_option = 0
        print(f"State changed to: {self.current_state}")  # Debug info
    
    def handle_input(self, event):
        """Handle input based on current state."""
        if event.type != pygame.KEYDOWN:
            return
        
        try:
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
            elif self.current_state == GameState.NEW_HIGH_SCORE:
                self._handle_new_high_score_input(event)
            elif self.current_state == GameState.GAME_OVER:
                self._handle_game_over_input(event)
        except Exception as e:
            print(f"Error handling input in state {self.current_state}: {e}")  # Debug info
    
    def _handle_main_menu_input(self, event):
        """Handle input in the main menu state."""
        print(f"Main menu input: {event.key}")  # Debug info
        if event.key in (pygame.K_UP, pygame.K_w, pygame.K_KP8):
            self.selected_option = (self.selected_option - 1) % len(self.menu_options[GameState.MAIN_MENU])
        elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_KP2):
            self.selected_option = (self.selected_option + 1) % len(self.menu_options[GameState.MAIN_MENU])
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.selected_option == 0:  # New Game
                self.change_state(GameState.PLAYING)
            elif self.selected_option == 1:  # High Scores
                self.change_state(GameState.HIGH_SCORE)
            elif self.selected_option == 2:  # Options
                self.change_state(GameState.OPTIONS)
            elif self.selected_option == 3:  # Quit
                self.game.running = False
    
    def _handle_playing_input(self, event):
        """Handle input in the playing state."""
        if event.key in (pygame.K_ESCAPE, pygame.K_p):
            self.change_state(GameState.PAUSED)
        elif event.key == pygame.K_o:
            self.change_state(GameState.OPTIONS)
        elif event.key == pygame.K_h:
            self.change_state(GameState.HIGH_SCORE)
    
    def _handle_pause_input(self, event):
        """Handle input in the pause state."""
        if event.key in (pygame.K_UP, pygame.K_w, pygame.K_KP8):
            self.selected_option = (self.selected_option - 1) % len(self.menu_options[GameState.PAUSED])
        elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_KP2):
            self.selected_option = (self.selected_option + 1) % len(self.menu_options[GameState.PAUSED])
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.selected_option == 0:  # Resume
                self.change_state(GameState.PLAYING)
            elif self.selected_option == 1:  # Options
                self.change_state(GameState.OPTIONS)
            elif self.selected_option == 2:  # Main Menu
                self.change_state(GameState.MAIN_MENU)
        elif event.key in (pygame.K_ESCAPE, pygame.K_p, pygame.K_r):  # Added R for resume
            self.change_state(GameState.PLAYING)
        elif event.key == pygame.K_o:  # O for options
            self.change_state(GameState.OPTIONS)
        elif event.key == pygame.K_m:  # M for main menu
            self.change_state(GameState.MAIN_MENU)
        elif event.key == pygame.K_h:  # H for high scores
            self.change_state(GameState.HIGH_SCORE)
    
    def _handle_options_input(self, event):
        """Handle input in the options state."""
        if event.key in (pygame.K_UP, pygame.K_w, pygame.K_KP8):
            self.selected_option = (self.selected_option - 1) % len(self.menu_options[GameState.OPTIONS])
        elif event.key in (pygame.K_DOWN, pygame.K_s, pygame.K_KP2):
            self.selected_option = (self.selected_option + 1) % len(self.menu_options[GameState.OPTIONS])
        elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
            if self.selected_option == 0:  # Control scheme toggle
                # Toggle between arrows and wasd
                new_scheme = 'wasd' if self.game.settings['controls'] == 'arrows' else 'arrows'
                self.game.settings['controls'] = new_scheme
                # Update menu text
                self.menu_options[GameState.OPTIONS][0] = f'Control Scheme: {new_scheme.upper()}'
                # Update ship controls if it exists
                if self.game.ship and hasattr(self.game.ship, 'update_controls'):
                    self.game.ship.update_controls()
                    print(f"Updated ship controls to {new_scheme}")  # Debug info
            else:  # Back
                # Return to previous state (MAIN_MENU or PLAYING)
                if self.previous_state == GameState.PLAYING:
                    self.change_state(GameState.PLAYING)
                else:
                    self.change_state(GameState.MAIN_MENU)
        elif event.key == pygame.K_ESCAPE:
            # Return to previous state (MAIN_MENU or PLAYING)
            if self.previous_state == GameState.PLAYING:
                self.change_state(GameState.PLAYING)
            else:
                self.change_state(GameState.MAIN_MENU)
    
    def _handle_high_score_input(self, event):
        """Handle input in the high score state."""
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.change_state(GameState.MAIN_MENU)
    
    def _handle_new_high_score_input(self, event):
        """Handle input in new high score state."""
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.high_score_name.strip():
            # Save high score and return to main menu
            self.game.scoring.add_high_score(self.high_score_name.strip(), self.game.level)
            self.change_state(GameState.MAIN_MENU)
        elif event.key == pygame.K_BACKSPACE:
            self.high_score_name = self.high_score_name[:-1]
        elif event.unicode.isalnum() and len(self.high_score_name) < 10:
            self.high_score_name += event.unicode.upper()
    
    def _handle_game_over_input(self, event):
        """Handle input in game over state."""
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
            if self.game.scoring.check_high_score():
                print("New high score achieved!")  # Debug info
                self.high_score_name = ""  # Reset name input
                self.change_state(GameState.NEW_HIGH_SCORE)
            else:
                print("Returning to main menu")  # Debug info
                self.change_state(GameState.MAIN_MENU)
    
    def draw(self, screen):
        """Draw the current state."""
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
        elif self.current_state == GameState.NEW_HIGH_SCORE:
            self._draw_new_high_score(screen)
        elif self.current_state == GameState.GAME_OVER:
            self._draw_game_over(screen)
    
    def _draw_main_menu(self, screen):
        """Draw the main menu."""
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
        """Draw the game state."""
        screen.fill((0, 0, 0))  # Black background
        
        try:
            # Draw all game entities
            for entity in self.game.entities:
                try:
                    # Draw render component
                    render = entity.get_component('render')
                    if render and render.visible and render.vertices:
                        render.draw(screen)
                    
                    # Draw particle effects
                    particle = entity.get_component('particle')
                    if particle:
                        particle.draw(screen)
                    
                    # Draw other effects
                    effects = entity.get_component('effects')
                    if effects:
                        effects.draw(screen)
                except Exception as e:
                    print(f"Error drawing entity {entity}: {e}")  # Debug info
                    continue
        except Exception as e:
            print(f"Error drawing game entities: {e}")  # Debug info
        
        try:
            # Draw HUD
            font = pygame.font.Font(None, 36)
            
            # Draw score
            score_text = font.render(f"Score: {self.game.scoring.current_score}", True, WHITE)
            screen.blit(score_text, (10, 10))
            
            # Draw multiplier if active
            if self.game.scoring.score_multiplier > 1.0:
                mult_text = font.render(f"x{self.game.scoring.score_multiplier:.1f}", True, (255, 255, 0))
                screen.blit(mult_text, (10, 30))
            
            # Draw lives
            lives_text = font.render(f"Lives: {self.game.lives}", True, WHITE)
            screen.blit(lives_text, (10, 50))  # Position below score
            
            # Draw level
            level_text = font.render(f"Level: {self.game.level}", True, WHITE)
            screen.blit(level_text, (10, 90))  # Position below lives
        except Exception as e:
            print(f"Error drawing HUD: {e}")  # Debug info
    
    def _draw_pause_overlay(self, screen):
        """Draw the pause menu overlay."""
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
        """Draw the options menu."""
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
        """Draw the high scores screen."""
        screen.fill((0, 0, 0))
        
        # Draw title
        font = pygame.font.Font(None, 48)
        title = font.render("HIGH SCORES", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, 100))
        
        # Draw scores
        font = pygame.font.Font(None, 36)
        scores = self.game.scoring.get_high_scores()
        y = 200
        for i, score in enumerate(scores):
            text = f"{i+1}. {score.name}: {score.score} (Level {score.level})"
            score_surf = font.render(text, True, WHITE)
            screen.blit(score_surf, (WINDOW_WIDTH/2 - score_surf.get_width()/2, y))
            y += 40
        
        # Draw return instruction
        text = font.render("Press ENTER or ESC to return", True, WHITE)
        screen.blit(text, (WINDOW_WIDTH/2 - text.get_width()/2, 500))
    
    def _draw_new_high_score(self, screen):
        """Draw the new high score entry screen."""
        screen.fill((0, 0, 0))
        font = pygame.font.Font(None, 48)
        
        # Draw title
        title = font.render("NEW HIGH SCORE!", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, 100))
        
        # Draw score
        score_text = font.render(f"Score: {self.game.scoring.current_score}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH/2 - score_text.get_width()/2, 200))
        
        # Draw name entry
        font = pygame.font.Font(None, 36)
        name_prompt = font.render("Enter your name:", True, WHITE)
        screen.blit(name_prompt, (WINDOW_WIDTH/2 - name_prompt.get_width()/2, 300))
        
        name_text = font.render(self.high_score_name + "_", True, (255, 255, 0))
        screen.blit(name_text, (WINDOW_WIDTH/2 - name_text.get_width()/2, 350))
        
        # Draw instructions
        instructions = font.render("Press ENTER when done", True, WHITE)
        screen.blit(instructions, (WINDOW_WIDTH/2 - instructions.get_width()/2, 450))
    
    def _draw_game_over(self, screen):
        """Draw the game over screen."""
        # Draw the final game state in background
        self._draw_game(screen)
        
        # Draw semi-transparent overlay
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.fill((0, 0, 0))
        overlay.set_alpha(192)  # More opaque for better readability
        screen.blit(overlay, (0, 0))
        
        # Draw game over text
        font = pygame.font.Font(None, 72)  # Larger font for main text
        title = font.render("GAME OVER", True, WHITE)
        screen.blit(title, (WINDOW_WIDTH/2 - title.get_width()/2, 180))
        
        # Draw final stats
        font = pygame.font.Font(None, 48)
        score_text = font.render(f"Final Score: {self.game.scoring.current_score}", True, WHITE)
        screen.blit(score_text, (WINDOW_WIDTH/2 - score_text.get_width()/2, 280))
        
        level_text = font.render(f"Level Reached: {self.game.level}", True, WHITE)
        screen.blit(level_text, (WINDOW_WIDTH/2 - level_text.get_width()/2, 340))
        
        # Draw high score message if applicable
        font = pygame.font.Font(None, 36)
        if self.game.scoring.check_high_score():
            high_score_text = font.render("NEW HIGH SCORE!", True, (255, 255, 0))  # Yellow for emphasis
            screen.blit(high_score_text, (WINDOW_WIDTH/2 - high_score_text.get_width()/2, 400))
            prompt = font.render("Press ENTER to save your score", True, WHITE)
        else:
            prompt = font.render("Press ENTER to continue", True, WHITE)
        screen.blit(prompt, (WINDOW_WIDTH/2 - prompt.get_width()/2, 460)) 