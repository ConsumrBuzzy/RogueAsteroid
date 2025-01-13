"""Handles game input processing."""
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
        if event.type == pygame.QUIT:
            self.game.running = False
            return
            
        # Let state manager handle input first
        self.game.state_manager.handle_input(event)
        
        # Handle game-specific input based on state
        if self.game.state == GameState.PLAYING:
            self._handle_playing_input(event)
        elif self.game.state == GameState.PAUSED:
            self._handle_paused_input(event)
        elif self.game.state == GameState.MAIN_MENU:
            self._handle_menu_input(event)

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

    def _handle_menu_input(self, event: pygame.event.Event) -> None:
        """Handle input in the menu state."""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN:
                self.game.state_manager.change_state(GameState.PLAYING)
            elif event.key == pygame.K_h:
                self.game.state_manager.change_state(GameState.HIGH_SCORE)
            elif event.key == pygame.K_o:
                self.game.state_manager.change_state(GameState.OPTIONS)
            elif event.key == pygame.K_q:
                self.game.running = False 