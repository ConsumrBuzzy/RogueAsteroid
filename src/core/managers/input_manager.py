"""Handles game input processing."""
import sys
import pygame
from src.core.game_state import GameState
from src.core.entities.components import InputComponent

class InputManager:
    def __init__(self, game):
        """Initialize the input manager.
        
        Args:
            game: Reference to the main game instance
        """
        self.game = game

    def process_input(self, event: pygame.event.Event) -> None:
        """Process a single input event.
        
        Args:
            event: The pygame event to process
        """
        # Handle quit event (window close button)
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        
        # Let state manager handle input first and check if it was consumed
        if self.game.state_manager.handle_input(event):
            return  # Event was consumed by state manager
            
        # Handle game-specific input based on state
        if self.game.state == GameState.PLAYING:
            self._handle_playing_input(event)
        elif self.game.state == GameState.PAUSED:
            self._handle_paused_input(event)

    def _handle_playing_input(self, event: pygame.event.Event) -> None:
        """Handle input in the playing state."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.game.state_manager.change_state(GameState.PAUSED)
            elif event.key == pygame.K_o:
                self.game.state_manager.change_state(GameState.OPTIONS)
            elif event.key == pygame.K_h:
                self.game.state_manager.change_state(GameState.HIGH_SCORE)
            
            # Handle ship input if it exists
            if self.game.entity_manager.ship:
                input_component = self.game.entity_manager.ship.get_component(InputComponent)
                if input_component:
                    input_component.handle_keydown(event.key)
        
        elif event.type == pygame.KEYUP and self.game.entity_manager.ship:
            # Handle ship input release
            input_component = self.game.entity_manager.ship.get_component(InputComponent)
            if input_component:
                input_component.handle_keyup(event.key)

    def _handle_paused_input(self, event: pygame.event.Event) -> None:
        """Handle input in the paused state."""
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.game.state_manager.change_state(GameState.PLAYING)
            elif event.key == pygame.K_q:
                self.game.state_manager.change_state(GameState.MAIN_MENU) 