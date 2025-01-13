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
        # Update game systems
        self.game.particle_system.update(self.dt)
        self.game.spawner.update(self.dt)
        
        # Update all entities
        self.game.entity_manager.update(self.dt)
        
        # Update collision detection
        self.game.collision_manager.handle_collisions()
        
        # Update scoring
        self.game.scoring.update(self.dt)
        
        # Update state manager
        self.game.state_manager.update()

    def _draw(self) -> None:
        """Draw the current frame."""
        self.game.state_manager.draw(self.game.screen)
        pygame.display.flip() 