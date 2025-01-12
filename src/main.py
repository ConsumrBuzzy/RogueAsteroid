"""Main entry point for RogueAsteroid game."""
import os
import sys
import traceback
import time
import pygame

# Add src directory to Python path for proper imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT, TARGET_FPS
from src.core.components import ComponentRegistry
from src.core.services import ServiceManager

# Performance monitoring
frame_times = []
MAX_FRAME_TIMES = 60  # Store last 60 frames for averaging

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
                
            # Set up display with flags
            flags = pygame.HWSURFACE | pygame.DOUBLEBUF
            screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT), flags)
            screen.fill((0, 0, 0))  # Clear to black
            pygame.display.flip()  # Show the cleared screen
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
        # Get component registry instance
        registry = ComponentRegistry()
        
        # Register all component types
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
        
def init_services(screen: pygame.Surface) -> bool:
    """Initialize game services.
    
    Args:
        screen: Pygame surface to render to
        
    Returns:
        bool: True if initialization successful, False otherwise
    """
    try:
        # Initialize service manager
        service_manager = ServiceManager()
        
        # Initialize all services
        service_manager.init_services(screen)
        return True
        
    except Exception as e:
        print(f"Error initializing services: {e}", file=sys.stderr)
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
            
        # Get screen surface
        screen = pygame.display.get_surface()
        
        # Initialize services
        if not init_services(screen):
            print("Failed to initialize services. Exiting.", file=sys.stderr)
            return
            
        # Get game service and start game loop
        service_manager = ServiceManager()
        game_service = service_manager.get_service('game')
        if not game_service:
            print("Failed to get game service. Exiting.", file=sys.stderr)
            return
            
        print("Starting game loop")
        game_service.start()
        
        # Main game loop
        clock = pygame.time.Clock()
        last_time = time.perf_counter()
        frame_count = 0
        frame_time_accum = 0
        
        while game_service.is_running():
            # Time management
            current_time = time.perf_counter()
            raw_dt = current_time - last_time
            last_time = current_time
            
            # Limit frame time to prevent spiral of death
            dt = min(raw_dt, 0.1)  # Cap at 100ms
            frame_times.append(dt)
            if len(frame_times) > MAX_FRAME_TIMES:
                frame_times.pop(0)
            
            # FPS tracking
            frame_count += 1
            frame_time_accum += dt
            if frame_time_accum >= 1.0:  # Every second
                fps = frame_count / frame_time_accum
                avg_frame_time = sum(frame_times) / len(frame_times)
                print(f"FPS: {fps:.1f}, Frame Time: {avg_frame_time*1000:.1f}ms")
                frame_count = 0
                frame_time_accum = 0
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_service.stop()
                else:
                    input_service = service_manager.get_service('input')
                    if input_service:
                        input_service.handle_event(event)
            
            # Update and render
            if not game_service.is_paused():
                game_service.update(dt)
            game_service.draw()
            
            # Maintain target frame rate
            clock.tick(TARGET_FPS)
            
        print("Game loop ended")
        
    except KeyboardInterrupt:
        print("\nGame terminated by user")
    except Exception as e:
        print(f"Fatal error running game: {e}", file=sys.stderr)
        traceback.print_exc()
        
    finally:
        print("Cleaning up...")
        try:
            # Clean up services
            service_manager = ServiceManager()
            service_manager.cleanup()
            
            # Quit pygame
            pygame.quit()
        except Exception as e:
            print(f"Error during cleanup: {e}", file=sys.stderr)
        sys.exit()
        
if __name__ == "__main__":
    main() 