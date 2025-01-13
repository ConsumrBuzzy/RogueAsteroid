"""Handles the main game loop and timing."""
import pygame
from src.core.game_state import GameState

class GameLoopManager:
    def __init__(self, game):
        """Initialize the game loop manager.
        
        Args:
            game: Reference to the main game instance
        """
        self.game = game
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True

    def run(self) -> None:
        """Run the main game loop."""
        print("Starting game loop")
        
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
        print("Game loop ended")

    def _update(self) -> None:
        """Update game state."""
        # Only update gameplay elements when in PLAYING state
        if self.game.state == GameState.PLAYING:
            # Update systems
            self.game.particle_system.update(self.dt)
            self.game.spawner.update(self.dt)
            
            # Update entities
            self.game.entity_manager.update(self.dt)
            
            # Handle collisions
            self.game.collision_manager.handle_collisions()
            
            # Check for wave completion
            if self.game.spawner.check_wave_complete():
                self.game.level += 1
                self.game.spawner.advance_wave()
        
        # Always update particles for visual effects
        elif self.game.state != GameState.PAUSED:
            self.game.particle_system.update(self.dt)

    def _draw(self) -> None:
        """Draw the current frame."""
        self.game.state_manager.draw(self.game.screen)
        pygame.display.flip() 