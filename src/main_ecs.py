"""
Main entry point for RogueAsteroid game.
"""

import os
import sys
import traceback
import pygame

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.ecs_game import ECSGame
from src.core.logging import get_logger

def init_pygame() -> bool:
    """Initialize pygame and its subsystems."""
    logger = get_logger()
    try:
        pygame.init()
        if pygame.get_init():
            logger.info("Pygame initialized successfully")
            
            # Initialize required subsystems
            if not pygame.font.get_init():
                pygame.font.init()
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            if not pygame.display.get_init():
                pygame.display.init()
                
            return True
            
        return False
        
    except Exception as e:
        logger.error(f"Error initializing pygame: {e}")
        return False

def main():
    """Entry point for the game."""
    logger = get_logger()
    
    try:
        # Initialize pygame
        if not init_pygame():
            logger.error("Failed to initialize pygame. Exiting.")
            return
        
        # Create and run game
        game = ECSGame()
        game.run()
        
    except Exception as e:
        logger.error(f"Unhandled error: {e}")
        traceback.print_exc()
        
    finally:
        pygame.quit()
        logger.info("Game terminated")

if __name__ == "__main__":
    main()
