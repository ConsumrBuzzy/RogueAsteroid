"""Main entry point for RogueAsteroid game."""
import os
import sys
import traceback
import pygame

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game import Game
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

def init_pygame():
    """Initialize pygame and its subsystems."""
    try:
        pygame.init()
        if pygame.get_init():
            print("Pygame initialized successfully")
            pygame.display.set_caption("RogueAsteroid")
            # Initialize required subsystems
            if not pygame.font.get_init():
                pygame.font.init()
            if not pygame.display.get_init():
                pygame.display.init()
            return True
        return False
    except Exception as e:
        print(f"Error initializing pygame: {e}", file=sys.stderr)
        return False

def main():
    """Entry point for the game."""
    try:
        # Initialize pygame first
        if not init_pygame():
            print("Failed to initialize pygame. Exiting.", file=sys.stderr)
            return
        
        # Create and run game
        game = Game()  # Game class now handles its own settings initialization
        print("Starting game loop")
        game.run()
        
    except KeyboardInterrupt:
        print("\nGame terminated by user")
    except Exception as e:
        print(f"Fatal error running game: {e}", file=sys.stderr)
        traceback.print_exc()
        
    finally:
        print("Cleaning up...")
        try:
            pygame.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}", file=sys.stderr)
        sys.exit()

if __name__ == "__main__":
    main() 