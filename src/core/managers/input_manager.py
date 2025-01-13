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
        # Handle global game controls first
        if event.type == pygame.KEYDOWN:
            if event.key in (pygame.K_ESCAPE, pygame.K_p):
                self.game.state_manager.change_state(GameState.PAUSED)
                return
            elif event.key == pygame.K_o:
                self.game.state_manager.change_state(GameState.OPTIONS)
                return
            elif event.key == pygame.K_h:
                self.game.state_manager.change_state(GameState.HIGH_SCORE)
                return
        
        # Pass all events to ship's input component if it exists
        if self.game.entity_manager.ship:
            input_component = self.game.entity_manager.ship.get_component(InputComponent)
            if input_component:
                input_component.handle_event(event)

    def _handle_paused_input(self, event: pygame.event.Event) -> None:
        """Handle input in the paused state."""
        if event.type == pygame.KEYDOWN:
            # Let state manager handle all pause menu input
            self.game.state_manager.handle_input(event) 

    def update(self, dt: float) -> None:
        """Update input state for continuous actions."""
        if self.game.state == GameState.PLAYING and self.game.entity_manager.ship:
            input_component = self.game.entity_manager.ship.get_component(InputComponent)
            if input_component:
                input_component.update(dt) 