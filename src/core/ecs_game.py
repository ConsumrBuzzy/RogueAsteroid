"""
ECS-based implementation of the main game class.
"""

import pygame
from typing import Optional
from src.core.ecs.world import World
from src.core.ecs.components import (
    Position, Velocity, Input, Renderable, Collider,
    Physics, Player, Bullet, Asteroid, Particle, Sound, Menu
)
from src.core.ecs.systems import (
    PhysicsSystem,
    CollisionSystem,
    InputSystem,
    RenderSystem,
    PlayerControlSystem,
    BulletSystem,
    AsteroidSystem,
    CollisionHandlingSystem,
    ParticleSystem,
    MenuSystem,
    SoundSystem
)
from src.core.ecs.resources import (
    Resources, WindowInfo, GameSettings, GameState,
    SpriteResource, AudioResource, MenuResource
)
from src.core.ecs.events import EventManager, CollisionEvent, ScoreEvent
from src.core.ecs.sprite_manager import init_sprites
from src.core.ecs.audio_manager import init_audio
from src.core.constants import (
    WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_TITLE, FPS,
    PLAYER_INITIAL_LIVES, MIN_ASTEROID_COUNT
)
from src.core.logging import get_logger

class ECSGame:
    """Main game class using Entity Component System architecture."""
    
    def __init__(self):
        """Initialize the game."""
        self.logger = get_logger()
        self.logger.info("Initializing ECS game")
        
        # Initialize pygame
        pygame.init()
        
        # Create world
        self.world = World()
        
        # Initialize window
        window = WindowInfo(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            title=WINDOW_TITLE
        )
        self.world.resources.add(window)
        
        # Set up display
        self.screen = pygame.display.set_mode((window.width, window.height))
        pygame.display.set_caption(window.title)
        
        # Initialize clock
        self.clock = pygame.time.Clock()
        
        # Initialize resources
        self._init_resources()
        
        # Initialize systems
        self._init_systems()
        
        # Initialize game state
        self._init_game_state()
    
    def _init_resources(self) -> None:
        """Initialize game resources."""
        # Initialize sprites
        init_sprites(self.world.resources)
        
        # Initialize audio
        init_audio(self.world.resources)
        
        # Initialize game settings
        settings = GameSettings()
        self.world.resources.add(settings)
        
        # Initialize menu
        menu = MenuResource()
        self.world.resources.add(menu)
    
    def _init_systems(self) -> None:
        """Initialize game systems."""
        self.systems = [
            InputSystem(),
            MenuSystem(),
            PlayerControlSystem(),
            PhysicsSystem(),
            CollisionSystem(),
            BulletSystem(),
            AsteroidSystem(),
            CollisionHandlingSystem(),
            ParticleSystem(),
            SoundSystem(),
            RenderSystem()
        ]
    
    def _init_game_state(self) -> None:
        """Initialize game state."""
        # Add game state resource
        state = GameState()
        self.world.resources.add(state)
        
        # Create player entity
        self._create_player()
        
        # Create initial asteroids
        for _ in range(MIN_ASTEROID_COUNT):
            self._create_asteroid("large")
    
    def _create_player(self) -> None:
        """Create the player entity."""
        player = self.world.create_entity()
        
        # Add components
        self.world.add_component(player, Position(
            x=WINDOW_WIDTH / 2,
            y=WINDOW_HEIGHT / 2
        ))
        self.world.add_component(player, Velocity())
        self.world.add_component(player, Physics())
        self.world.add_component(player, Input())
        self.world.add_component(player, Collider(radius=12))
        self.world.add_component(player, Player(lives=PLAYER_INITIAL_LIVES))
        self.world.add_component(player, Sound())
        self.world.add_component(player, Renderable(
            sprite_name="ship",
            layer=4  # Player layer
        ))
    
    def _create_asteroid(self, size: str) -> None:
        """Create an asteroid entity."""
        asteroid = self.world.create_entity()
        
        # Add components
        self.world.add_component(asteroid, Position())  # Random position set by system
        self.world.add_component(asteroid, Velocity())  # Random velocity set by system
        self.world.add_component(asteroid, Asteroid(size=size))
        self.world.add_component(asteroid, Collider())  # Radius set by system
        self.world.add_component(asteroid, Sound())
        self.world.add_component(asteroid, Renderable(
            sprite_name=f"asteroid_{size}_1",  # Random variant set by system
            layer=2  # Asteroid layer
        ))
    
    def run(self) -> None:
        """Run the game loop."""
        self.logger.info("Starting game loop")
        running = True
        
        while running:
            # Calculate delta time
            dt = self.clock.tick(FPS) / 1000.0
            
            # Process events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    break
            
            # Update game state
            game_state = self.world.resources.get(GameState)
            if game_state and game_state.quit:
                running = False
                break
            
            # Update all systems
            for system in self.systems:
                system.update(self.world, dt)
            
            # Update display
            pygame.display.flip()
        
        self.logger.info("Game loop ended")
    
    def quit(self) -> None:
        """Clean up and quit the game."""
        pygame.quit()
