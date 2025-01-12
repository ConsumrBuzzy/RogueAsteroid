"""Main entry point for RogueAsteroid game."""
import os
import sys
import traceback
import pygame

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.game import Game
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.components import ComponentRegistry

def init_pygame() -> bool:
    """Initialize pygame and its subsystems.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
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
                
            # Set up display
            pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
            return True
            
        return False
    except Exception as e:
        print(f"Error initializing pygame: {e}", file=sys.stderr)
        return False

def init_component_system() -> bool:
    """Initialize the component system.
    
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        # Initialize component registry
        registry = ComponentRegistry()
        
        # Register all core components
        from src.core.components.transform import TransformComponent
        from src.core.components.physics import PhysicsComponent
        from src.core.components.render import RenderComponent
        from src.core.components.collision import CollisionComponent
        from src.core.components.input import InputComponent
        from src.core.components.effect import EffectComponent
        from src.core.components.screen_wrap import ScreenWrapComponent
        from src.core.components.health import HealthComponent
        from src.core.components.timer import TimerComponent
        from src.core.components.score import ScoreComponent
        from src.core.components.wave import WaveComponent
        from src.core.components.ui import UIComponent
        from src.core.components.debug import DebugComponent
        
        registry.register_component('TransformComponent', TransformComponent)
        registry.register_component('PhysicsComponent', PhysicsComponent)
        registry.register_component('RenderComponent', RenderComponent)
        registry.register_component('CollisionComponent', CollisionComponent)
        registry.register_component('InputComponent', InputComponent)
        registry.register_component('EffectComponent', EffectComponent)
        registry.register_component('ScreenWrapComponent', ScreenWrapComponent)
        registry.register_component('HealthComponent', HealthComponent)
        registry.register_component('TimerComponent', TimerComponent)
        registry.register_component('ScoreComponent', ScoreComponent)
        registry.register_component('WaveComponent', WaveComponent)
        registry.register_component('UIComponent', UIComponent)
        registry.register_component('DebugComponent', DebugComponent)
        
        print("Component system initialized successfully")
        return True
        
    except Exception as e:
        print(f"Error initializing component system: {e}", file=sys.stderr)
        traceback.print_exc()
        return False

def main():
    """Entry point for the game."""
    try:
        # Initialize core systems
        if not init_pygame():
            print("Failed to initialize pygame. Exiting.", file=sys.stderr)
            return
            
        if not init_component_system():
            print("Failed to initialize component system. Exiting.", file=sys.stderr)
            return
        
        # Create and run game
        game = Game()
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