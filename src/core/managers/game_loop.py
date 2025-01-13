"""Handles the main game loop and timing."""
import pygame
from src.core.game_state import GameState
from src.core.entities.components import InputComponent
from src.core.logging import get_logger

class GameLoopManager:
    def __init__(self, game):
        """Initialize the game loop manager.
        
        Args:
            game: Reference to the main game instance
        """
        self.game = game
        self.logger = get_logger()
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True

    def run(self) -> None:
        """Run the main game loop."""
        self.logger.info("Starting game loop")
        
        while self.running:
            # Update delta time
            self.dt = self.clock.tick(60) / 1000.0
            
            # Process input
            for event in pygame.event.get():
                self.game.input_manager.process_input(event)
            
            # Update game state
            self._update()
            
            # Draw
            self._draw()
        
        pygame.quit()
        self.logger.info("Game loop ended")

    def _update(self) -> None:
        """Update game state."""
        # Update input manager for continuous input
        self.game.input_manager.update(self.dt)
        
        # Update game systems
        if self.game.state == GameState.PLAYING:
            # Update entities
            for entity in self.game.entity_manager.entities:
                entity.update(self.dt)
            
            # Update collision detection
            self.game.collision_manager.handle_collisions()

    def _draw(self) -> None:
        """Draw the current frame."""
        self.game.state_manager.draw(self.game.screen)
        pygame.display.flip() 