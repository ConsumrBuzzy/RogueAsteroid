"""
ECS-based implementation of the main game class.
"""

import pygame
from typing import Optional
from src.core.ecs import World
from src.core.ecs.components import Position, Velocity, Input, Renderable, Collider
from src.core.ecs.system import (
    PhysicsSystem,
    CollisionSystem,
    InputSystem,
    RenderSystem
)
from src.core.ecs.game_systems import (
    PlayerControlSystem,
    BulletSystem,
    AsteroidSystem,
    CollisionHandlingSystem
)
from src.core.ecs.particle_system import ParticleSystem
from src.core.ecs.menu_system import MenuSystem, MenuResource, create_main_menu
from src.core.ecs.high_score_system import HighScoreSystem, HighScoreResource
from src.core.ecs.resources import Resources, WindowInfo, GameSettings, GameState
from src.core.ecs.events import CollisionEvent, ScoreEvent
from src.core.ecs.game_components import EntityTag, EntityType, Physics, Player, Asteroid
from src.core.ecs.sprite_manager import SpriteResource, init_sprites
from src.core.ecs.audio_manager import init_audio, play_sound, play_music
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT
from src.core.logging import get_logger

class ECSGame:
    """Main game class using Entity Component System architecture."""
    
    def __init__(self):
        """Initialize the game."""
        self.logger = get_logger()
        self.logger.info("Initializing ECS game")
        
        # Initialize pygame
        pygame.init()
        
        # Create world and resources
        self.world = World()
        self.resources = Resources()
        
        # Initialize window
        self.resources.add(WindowInfo(
            width=WINDOW_WIDTH,
            height=WINDOW_HEIGHT,
            title="Rogue Asteroid"
        ))
        window_info = self.resources.get(WindowInfo)
        self.screen = pygame.display.set_mode((window_info.width, window_info.height))
        pygame.display.set_caption(window_info.title)
        
        # Initialize game settings and state
        self.resources.add(GameSettings())
        self.resources.add(GameState())
        
        # Initialize assets
        init_sprites(self.resources)
        init_audio(self.resources)
        
        # Initialize high scores
        high_score_system = HighScoreSystem()
        high_score_system.load_scores(self.world)
        
        # Initialize systems
        self.systems = [
            PhysicsSystem(),
            PlayerControlSystem(),
            BulletSystem(),
            AsteroidSystem(),
            CollisionSystem(),
            CollisionHandlingSystem(),
            ParticleSystem(),
            InputSystem(),
            RenderSystem(),
            MenuSystem(),
            high_score_system
        ]
        
        # Setup event handlers
        self._setup_event_handlers()
        
        self.clock = pygame.time.Clock()
        self.running = True
        
        # Create main menu
        create_main_menu(self.world)
        
        # Start menu music
        play_music(self.resources, "menu")
        
        self.logger.info("ECS game initialization complete")
    
    def _setup_event_handlers(self):
        """Setup event handlers for game events."""
        self.world.events.subscribe(CollisionEvent, self._handle_collision)
        self.world.events.subscribe(ScoreEvent, self._handle_score)
    
    def _handle_collision(self, event: CollisionEvent):
        """Handle collision events between entities."""
        # Get colliding entities' components
        entity1_collider = self.world.get_component(event.entity1, Collider)
        entity2_collider = self.world.get_component(event.entity2, Collider)
        
        if not entity1_collider or not entity2_collider:
            return
        
        # Get entity types
        entity1_tag = self.world.get_component(event.entity1, EntityTag)
        entity2_tag = self.world.get_component(event.entity2, EntityTag)
        
        if not entity1_tag or not entity2_tag:
            return
        
        # Play appropriate sound effects
        if (entity1_tag.type == EntityType.BULLET and entity2_tag.type == EntityType.ASTEROID or
            entity2_tag.type == EntityType.BULLET and entity1_tag.type == EntityType.ASTEROID):
            asteroid = event.entity1 if entity1_tag.type == EntityType.ASTEROID else event.entity2
            asteroid_size = self.world.get_component(asteroid, Asteroid)
            if asteroid_size:
                play_sound(self.resources, f"explosion_{asteroid_size.size}")
        
        elif (entity1_tag.type == EntityType.PLAYER and entity2_tag.type == EntityType.ASTEROID or
              entity2_tag.type == EntityType.PLAYER and entity1_tag.type == EntityType.ASTEROID):
            play_sound(self.resources, "explosion_large")

        # Handle collision based on entity types
        # This will be expanded based on game logic
        self.logger.debug(f"Collision between entities {event.entity1} and {event.entity2}")
    
    def _handle_score(self, event: ScoreEvent):
        """Handle score events."""
        game_state = self.resources.get(GameState)
        if game_state:
            game_state.score += event.points
    
    def update(self, dt: float):
        """Update game state."""
        # Process events
        self.world.events.process_events()
        
        # Get current menu if any
        menu = self.world.resources.get(MenuResource)
        
        # Update all systems
        for system in self.systems:
            if isinstance(system, MenuSystem) and menu:
                # Only update menu system if we're in a menu
                system.update(self.world, dt)
            elif not isinstance(system, MenuSystem) and not menu:
                # Only update game systems if we're not in a menu
                system.update(self.world, dt)
        
        # Cleanup any dead entities
        self.world.cleanup()
    
    def render(self):
        """Render the game."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Get current menu if any
        menu = self.world.resources.get(MenuResource)
        
        if menu:
            # Render menu
            menu_system = next((s for s in self.systems if isinstance(s, MenuSystem)), None)
            if menu_system:
                menu_system.render(self.screen, menu)
        else:
            # Render game
            render_system = next((s for s in self.systems if isinstance(s, RenderSystem)), None)
            if render_system:
                render_system.update(self.world, 0)
        
        # Update display
        pygame.display.flip()
    
    def run(self):
        """Main game loop."""
        self.logger.info("Starting game loop")
        
        while self.running:
            # Calculate delta time
            dt = self.clock.tick(60) / 1000.0
            
            # Handle pygame events
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
            
            # Update and render
            self.update(dt)
            self.render()
        
        pygame.quit()
    
    def spawn_player(self) -> int:
        """Spawn the player ship."""
        window_info = self.resources.get(WindowInfo)
        if not window_info:
            return -1
            
        player = self.world.create_entity()
        
        # Add components
        self.world.add_component(player, Position(
            x=window_info.width / 2,
            y=window_info.height / 2
        ))
        self.world.add_component(player, Velocity())
        self.world.add_component(player, Input())
        self.world.add_component(player, Collider(radius=20.0))
        self.world.add_component(player, Physics(
            mass=1.0,
            drag=0.1,
            max_speed=400.0,
            max_rotation=360.0
        ))
        self.world.add_component(player, EntityTag(type=EntityType.PLAYER))
        
        # Add renderable when sprites are loaded
        sprites = self.resources.get(SpriteResource)
        if sprites and "ship" in sprites.sprites:
            self.world.add_component(player, Renderable(
                texture=sprites.sprites["ship"],
                width=32,
                height=32,
                layer=1
            ))
        
        return player
    
    def spawn_asteroid(self, size: str = "large") -> int:
        """Spawn an asteroid."""
        window_info = self.resources.get(WindowInfo)
        if not window_info:
            return -1
            
        # Size configurations
        size_configs = {
            "large": (40.0, 50.0),
            "medium": (20.0, 35.0),
            "small": (10.0, 20.0)
        }
        
        radius, speed = size_configs.get(size, size_configs["large"])
        
        asteroid = self.world.create_entity()
        
        # Random position at screen edge
        if pygame.random.random() < 0.5:
            x = pygame.random.randint(0, window_info.width)
            y = 0 if pygame.random.random() < 0.5 else window_info.height
        else:
            x = 0 if pygame.random.random() < 0.5 else window_info.width
            y = pygame.random.randint(0, window_info.height)
        
        # Random velocity
        angle = pygame.random.random() * 2 * 3.14159
        vel_x = pygame.math.cos(angle) * speed
        vel_y = pygame.math.sin(angle) * speed
        
        # Add components
        self.world.add_component(asteroid, Position(x=x, y=y))
        self.world.add_component(asteroid, Velocity(dx=vel_x, dy=vel_y))
        self.world.add_component(asteroid, Collider(radius=radius))
        
        return asteroid
