"""Main entry point for RogueAsteroid game."""
import os
import sys
import pygame

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game import Game
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

def main():
    """Entry point for the game."""
    try:
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("RogueAsteroid")
        
        # Create and run game
        game = Game()
        game.settings = {
            'window': {
                'width': WINDOW_WIDTH,
                'height': WINDOW_HEIGHT
            },
            'controls': 'arrows'  # Default to arrow keys
        }
        print("Game initialized with settings:", game.settings)  # Debug info
        game.run()
        
    except Exception as e:
        print(f"Error running game: {e}", file=sys.stderr)
        raise
        
    finally:
        pygame.quit()
        sys.exit()

if __name__ == "__main__":
    main() 