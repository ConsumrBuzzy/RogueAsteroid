"""Main entry point for RogueAsteroid game."""
import os
import sys

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game import Game

def main():
    """Entry point for the game."""
    game = Game()
    game.run()

if __name__ == "__main__":
    main() 