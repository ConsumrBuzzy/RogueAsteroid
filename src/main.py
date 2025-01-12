"""Main entry point for RogueAsteroid game."""
import os
import sys
import logging
import traceback

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('docs/logs/debug/game_init.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

from src.core.game import Game

def main():
    """Main entry point for the game."""
    try:
        logger.info("Starting RogueAsteroid...")
        game = Game()
        game.run()
        
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        logger.error(traceback.format_exc())
        
if __name__ == "__main__":
    main() 