"""State management for the game."""
from enum import Enum, auto
import pygame
from src.core.constants import WHITE, WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.entities.components import (
    RenderComponent,
    ParticleComponent
)
from src.core.logging import get_logger

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
        self.logger = get_logger()
        self.logger.info("Initializing state manager")
        self.game = game
        self.current_state = None  # Initialize to None, let Game class set initial state
        self.previous_state = None  # Track previous state for returning from menus
        self.selected_option = 0
        self.menu_options = {
            GameState.MAIN_MENU: ['New Game', 'High Scores', 'Options', 'Quit'],
            GameState.OPTIONS: [
                f'Control Scheme: {self.game.settings["controls"].upper()}',
                f'Sound: {"ON" if self.game.settings["sound"] else "OFF"}',
                'Back'
            ],
            GameState.PAUSED: ['Resume', 'Options', 'Main Menu']
        }
        self.high_score_name = ""  # For new high score entry
    
    def change_state(self, new_state: GameState) -> None:
        """Change the current game state."""
        self.logger.info(f"Changing state from {self.current_state} to {new_state}")
        
        # Handle cleanup for old state
        if new_state == GameState.GAME_OVER:
            self.logger.info(f"Game Over - Final Score: {self.game.scoring.current_score}")
            # Clear any remaining entities except the ship
            self.game.entity_manager.clear_all(keep_ship=False)
            # Check for high score immediately
            if self.game.scoring.is_high_score():
                self.logger.info("New high score achieved!")
                self.high_score_name = ""  # Reset name input
                new_state = GameState.NEW_HIGH_SCORE
        elif new_state == GameState.MAIN_MENU:
            if self.current_state in [GameState.GAME_OVER, GameState.NEW_HIGH_SCORE]:
                # Clear all entities when returning to main menu from game over
                self.game.entity_manager.clear_all(keep_ship=False)
                # Reset game state when coming from game over or new high score
                self.game.reset_game()
                # Skip the next input event to prevent auto-start
                if self.current_state == GameState.NEW_HIGH_SCORE:
                    pygame.event.clear(pygame.KEYDOWN)  # Clear any pending key events
        
        # Update previous state, but don't track transitions to/from NEW_HIGH_SCORE
        if self.current_state != GameState.NEW_HIGH_SCORE and new_state != GameState.NEW_HIGH_SCORE:
            self.previous_state = self.current_state
        
        # Set new state
        self.current_state = new_state
        self.selected_option = 0
    
    def handle_input(self, event):
        """Handle input based on current state."""
        if event.type != pygame.KEYDOWN:
            return False
        
        try:
            if self.current_state == GameState.MAIN_MENU:
                return self._handle_main_menu_input(event)
            elif self.current_state == GameState.PLAYING:
                return self._handle_playing_input(event)
            elif self.current_state == GameState.PAUSED:
                return self._handle_pause_input(event)
            elif self.current_state == GameState.OPTIONS:
                return self._handle_options_input(event)
            elif self.current_state == GameState.HIGH_SCORE:
                return self._handle_high_score_input(event)
            elif self.current_state == GameState.NEW_HIGH_SCORE:
                return self._handle_new_high_score_input(event)
            elif self.current_state == GameState.GAME_OVER:
                return self._handle_game_over_input(event)
        except Exception as e:
            self.logger.error(f"Error handling input in state {self.current_state}: {str(e)}")
            import traceback
            self.logger.error(traceback.format_exc())
        return False
    
    def _handle_main_menu_input(self, event):
        """Handle input in the main menu state."""
        self.logger.debug(f"Main menu input: {event.key}")
        
        # Skip processing if we just came from NEW_HIGH_SCORE state
        if self.previous_state == GameState.NEW_HIGH_SCORE:
            self.previous_state = GameState.MAIN_MENU
            return True
        
        # Handle menu navigation
        if event.key == pygame.K_UP or event.key == pygame.K_w or event.key == pygame.K_KP8:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options[GameState.MAIN_MENU])
            return True
        elif event.key == pygame.K_DOWN or event.key == pygame.K_s or event.key == pygame.K_KP2:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options[GameState.MAIN_MENU])
            return True
        elif event.key == pygame.K_RETURN or event.key == pygame.K_KP_ENTER:
            self.logger.debug(f"Selected menu option: {self.selected_option}")
            if self.selected_option == 0:  # New Game
                self.game.new_game()  # First setup the game
                self.change_state(GameState.PLAYING)  # Then change state
            elif self.selected_option == 1:  # High Scores
                self.change_state(GameState.HIGH_SCORE)
            elif self.selected_option == 2:  # Options
                self.change_state(GameState.OPTIONS)
            elif self.selected_option == 3:  # Quit
                self.game.running = False
            return True
        return False
    
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
        """Handle input in the options menu."""
        if event.key == pygame.K_UP:
            self.selected_option = (self.selected_option - 1) % len(self.menu_options[GameState.OPTIONS])
        elif event.key == pygame.K_DOWN:
            self.selected_option = (self.selected_option + 1) % len(self.menu_options[GameState.OPTIONS])
        elif event.key == pygame.K_RETURN:
            if self.selected_option == 0:  # Controls
                self.game.toggle_control_scheme()
                self.menu_options[GameState.OPTIONS][0] = f'Control Scheme: {self.game.settings["controls"].upper()}'
            elif self.selected_option == 1:  # Sound
                self.game.toggle_sound()
                self.menu_options[GameState.OPTIONS][1] = f'Sound: {"ON" if self.game.settings["sound"] else "OFF"}'
            elif self.selected_option == 2:  # Back
                self.change_state(self.previous_state or GameState.MAIN_MENU)
        elif event.key == pygame.K_ESCAPE:
            self.change_state(self.previous_state or GameState.MAIN_MENU)
    
    def _handle_high_score_input(self, event):
        """Handle input in the high score state."""
        if event.key in (pygame.K_ESCAPE, pygame.K_RETURN, pygame.K_KP_ENTER):
            self.change_state(GameState.MAIN_MENU)
    
    def _handle_new_high_score_input(self, event):
        """Handle input in new high score state."""
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER) and self.high_score_name.strip():
            # Save high score and return to main menu
            self.game.scoring.add_high_score(self.high_score_name.strip())  # No score needed, uses current_score
            self.logger.info(f"Saved high score: {self.high_score_name} - {self.game.scoring.current_score}")
            # Reset game state before changing to main menu to prevent auto-start
            self.game.reset_game()
            self.change_state(GameState.MAIN_MENU)
            # Ensure we don't accidentally transition to another state
            self.previous_state = GameState.MAIN_MENU
            return True
        elif event.key == pygame.K_BACKSPACE:
            self.high_score_name = self.high_score_name[:-1]
            return True
        elif event.unicode.isalnum() and len(self.high_score_name) < 10:
            self.high_score_name += event.unicode.upper()
            return True
        return False
    
    def _handle_game_over_input(self, event):
        """Handle input in game over state."""
        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER, pygame.K_ESCAPE):
            # Check for high score before transitioning
            if self.game.scoring.is_high_score():  # No argument needed, uses current_score
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
            for entity in self.game.entity_manager.entities:
                try:
                    # Draw render component
                    render = entity.get_component(RenderComponent)
                    if render and render.visible and render.vertices:
                        render.draw(screen)
                    
                    # Draw particle effects
                    particle = entity.get_component(ParticleComponent)
                    if particle:
                        particle.draw(screen)
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
            
            # Draw lives
            lives_text = font.render(f"Lives: {self.game.lives}", True, WHITE)
            screen.blit(lives_text, (10, 50))
            
            # Draw level
            level_text = font.render(f"Level: {self.game.level}", True, WHITE)
            screen.blit(level_text, (10, 90))
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
        scores = self.game.scoring.get_scores()  # Changed from high_scores to scoring
        y = 200
        for i, (name, score) in enumerate(scores):
            text = f"{i+1}. {name}: {score}"
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
        score_text = font.render(f"Score: {self.game.score}", True, WHITE)
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