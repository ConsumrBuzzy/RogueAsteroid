"""Main game class for RogueAsteroid."""
import pygame
import logging
from typing import Dict, Type, Optional

from .services import (
    ServiceManager,
    StateService,
    EventManagerService,
    ResourceManagerService,
    InputService,
    RenderService,
    PhysicsService,
    EntityManagerService,
    ParticleService
)
from .constants import TARGET_FPS, SCREEN_WIDTH, SCREEN_HEIGHT
from .components import ComponentRegistry

logger = logging.getLogger(__name__)

class Game:
    """Main game class that manages the game loop and services."""
    
    def __init__(self):
        """Initialize the game and its services."""
        logger.info("Initializing Game instance...")
        self.running = False
        self.services = ServiceManager()
        
        # Initialize component system first
        logger.info("Initializing component system...")
        self._init_components()
        
        # Initialize pygame and create screen
        logger.info("Setting up display...")
        if not pygame.get_init():
            pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Rogue Asteroid")
        
        logger.info("Setting up services...")
        self._setup_services()
        self._clock = pygame.time.Clock()
        logger.info("Game initialization complete")
        
    def _init_components(self):
        """Initialize the component system."""
        try:
            registry = ComponentRegistry()
            
            # Register all component types
            from .components.transform import TransformComponent
            from .components.physics import PhysicsComponent
            from .components.render import RenderComponent
            from .components.collision import CollisionComponent
            from .components.input import InputComponent
            from .components.effect import EffectComponent
            from .components.screen_wrap import ScreenWrapComponent
            from .components.health import HealthComponent
            from .components.timer import TimerComponent
            from .components.score import ScoreComponent
            from .components.wave import WaveComponent
            from .components.ui import UIComponent
            from .components.debug import DebugComponent
            
            logger.debug("Registering components...")
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
            logger.info("Component system initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize component system: {e}", exc_info=True)
            raise
        
    def _setup_services(self):
        """Initialize and register all game services in dependency order."""
        try:
            # Core services (no dependencies)
            logger.debug("Registering core services...")
            self.services.register_service(EventManagerService.__name__, EventManagerService)
            self.services.register_service(StateService.__name__, StateService)
            self.services.register_service(ResourceManagerService.__name__, ResourceManagerService)
            
            # Input and rendering services
            logger.debug("Registering input and rendering services...")
            self.services.register_service(InputService.__name__, InputService)
            self.services.register_service(RenderService.__name__, lambda: RenderService(self.screen))
            
            # Game systems
            logger.debug("Registering game systems...")
            self.services.register_service(PhysicsService.__name__, lambda: PhysicsService(SCREEN_WIDTH, SCREEN_HEIGHT))
            self.services.register_service(EntityManagerService.__name__, lambda: EntityManagerService(self.services))
            self.services.register_service(ParticleService.__name__, lambda: ParticleService(self.screen))
            logger.info("All services registered successfully")
            
        except Exception as e:
            logger.error(f"Failed to setup services: {e}", exc_info=True)
            raise
        
    def run(self):
        """Run the main game loop."""
        logger.info("Starting game loop...")
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
                    logger.error(f"Error in game update: {e}", exc_info=True)
                    continue
                
                # Maintain target frame rate
                self._clock.tick(TARGET_FPS)
                
        except Exception as e:
            logger.error(f"Fatal error in game loop: {e}", exc_info=True)
            self.running = False
            
        finally:
            self.cleanup()
            
    def update(self, dt: float):
        """Update game state for the current frame."""
        try:
            # Get required services
            event_manager = self.services.get_service(EventManagerService)
            state_service = self.services.get_service(StateService)
            input_service = self.services.get_service(InputService)
            physics = self.services.get_service(PhysicsService)
            entities = self.services.get_service(EntityManagerService)
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
            
        except Exception as e:
            logger.error(f"Error updating game state: {e}", exc_info=True)
            raise
        
    def cleanup(self):
        """Clean up game resources and shut down services."""
        logger.info("Cleaning up game resources...")
        if self.services:
            try:
                self.services.cleanup()
                self.services = None
            except Exception as e:
                logger.error(f"Error cleaning up services: {e}", exc_info=True)
                
        pygame.quit()
        logger.info("Cleanup complete") 