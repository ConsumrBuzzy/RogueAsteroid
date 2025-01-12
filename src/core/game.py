"""Main game class for RogueAsteroid."""
import pygame
from typing import Dict, Type, Optional

from .services import (
    ServiceManager,
    StateService,
    EventManagerService,
    ResourceManagerService,
    InputService,
    RenderService,
    PhysicsService,
    EntityService,
    ParticleService
)
from .constants import TARGET_FPS

class Game:
    """Main game class that manages the game loop and services."""
    
    def __init__(self):
        """Initialize the game and its services."""
        self.running = False
        self.services = ServiceManager()
        self._setup_services()
        self._clock = pygame.time.Clock()
        
    def _setup_services(self):
        """Initialize and register all game services in dependency order."""
        # Core services (no dependencies)
        self.services.register_service("events", EventManagerService)
        self.services.register_service("state", StateService)
        self.services.register_service("resources", ResourceManagerService)
        
        # Input and rendering services
        self.services.register_service("input", InputService)
        self.services.register_service("render", RenderService)
        
        # Game systems
        self.services.register_service("physics", PhysicsService)
        self.services.register_service("entities", EntityService)
        self.services.register_service("particles", ParticleService)
        
    def run(self):
        """Run the main game loop."""
        self.running = True
        last_time = pygame.time.get_ticks() / 1000.0
        
        try:
            while self.running:
                # Calculate delta time
                current_time = pygame.time.get_ticks() / 1000.0
                dt = current_time - last_time
                last_time = current_time
                
                # Update game state
                try:
                    self.update(dt)
                except Exception as e:
                    # Log error but continue running
                    print(f"Error in game update: {e}")
                    continue
                
                # Maintain target frame rate
                self._clock.tick(TARGET_FPS)
                
        except Exception as e:
            print(f"Fatal error in game loop: {e}")
            self.running = False
            
        finally:
            self.cleanup()
            
    def update(self, dt: float):
        """Update game state for the current frame.
        
        Args:
            dt: Time elapsed since last update in seconds.
        """
        # Get required services
        event_manager = self.services.get_service(EventManagerService)
        state_service = self.services.get_service(StateService)
        input_service = self.services.get_service(InputService)
        physics = self.services.get_service(PhysicsService)
        entities = self.services.get_service(EntityService)
        particles = self.services.get_service(ParticleService)
        render = self.services.get_service(RenderService)
        
        # Process events and input
        event_manager.process_events()
        input_service.update()
        
        # Update game systems
        physics.update(dt)
        entities.update(dt)
        particles.update(dt)
        
        # Render frame
        render.clear()
        entities.draw()
        particles.draw()
        render.present()
        
    def cleanup(self):
        """Clean up game resources and shut down services."""
        if self.services:
            self.services.cleanup()
            self.services = None 