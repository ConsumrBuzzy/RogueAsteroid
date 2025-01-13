"""Main game class."""
import random
import math
import pygame
from src.core.game_state import StateManager, GameState
from src.core.services import AudioManager, HighScoreManager
from src.core.systems import ParticleSystem, Spawner
from src.core.managers import (
    CollisionManager,
    EntityManager,
    SpawnManager,
    InputManager,
    GameLoopManager
)
from src.entities.particle import Particle
from src.core.entities.components import (
    TransformComponent,
    PhysicsComponent,
    InputComponent
)
from src.core.constants import (
    WINDOW_WIDTH, 
    WINDOW_HEIGHT,
    STARTING_LIVES
)
from src.core.logging import get_logger

class Game:
    def __init__(self):
        """Initialize the game."""
        self.logger = get_logger()
        self.logger.info("Initializing game")
        
        # Initialize pygame and display
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        
        # Game settings
        self.settings = {
            'window': {
                'width': self.width,
                'height': self.height
            },
            'controls': 'arrows',  # Default to arrow keys
            'sound': False  # Default to sound off
        }
        self.logger.debug(f"Game settings initialized: {self.settings}")
        
        # Initialize services
        self.audio = AudioManager()
        self.scoring = HighScoreManager()  # Use consolidated scoring system
        self.logger.debug("Game services initialized")
        
        # Initialize systems
        self.particle_system = ParticleSystem(self)
        self.spawner = Spawner(self)
        self.logger.debug("Systems initialized")
        
        # Initialize managers
        self.entity_manager = EntityManager(self)
        self.collision_manager = CollisionManager(self)
        self.spawn_manager = SpawnManager(self)
        self.input_manager = InputManager(self)
        self.game_loop = GameLoopManager(self)
        self.logger.debug("Managers initialized")
        
        # Initialize game properties
        self.level = 1
        self.lives = STARTING_LIVES
        self.respawn_timer = 0.0
        self.logger.debug(f"Game properties initialized with {self.lives} lives")
        
        # Initialize state management
        self.state_manager = StateManager(self)
        self.logger.debug("State manager initialized")
        
        # Set initial state
        self.state_manager.change_state(GameState.MAIN_MENU)
        self.logger.info("Game initialization complete")
    
    @property
    def state(self):
        """Get current game state."""
        return self.state_manager.current_state
    
    @state.setter
    def state(self, new_state):
        """Set game state through state manager."""
        self.state_manager.change_state(new_state)
    
    @property
    def score(self):
        """Get current score."""
        return self.scoring.current_score
    
    @score.setter
    def score(self, value):
        """Set current score."""
        self.scoring.current_score = value
    
    def new_game(self):
        """Start a new game."""
        self.logger.info("Starting new game")
        self.reset_game()
        self.spawn_manager.spawn_ship()
        self.spawner.start_wave()
    
    def reset_game(self):
        """Reset the game state."""
        self.logger.info("Resetting game state")
        self.entity_manager.clear_all()
        self.level = 1
        self.lives = STARTING_LIVES
        self.scoring.reset_score()
    
    def pause(self):
        """Pause the game."""
        if self.state == GameState.PLAYING:
            self.state_manager.change_state(GameState.PAUSED)
    
    def resume(self):
        """Resume the game."""
        if self.state == GameState.PAUSED:
            self.state_manager.change_state(GameState.PLAYING)
    
    def return_to_menu(self):
        """Return to the main menu."""
        self.reset_game()
        self.state_manager.change_state(GameState.MAIN_MENU)
    
    def lose_life(self):
        """Handle losing a life."""
        self.lives -= 1
        self.logger.info(f"Life lost. Remaining lives: {self.lives}")
        
        if self.lives <= 0:
            self.logger.info("Game over - No lives remaining")
            self.state_manager.change_state(GameState.GAME_OVER)
        else:
            self.spawn_manager.respawn_ship()
    
    def toggle_control_scheme(self):
        """Toggle between arrow keys and WASD controls."""
        new_scheme = 'wasd' if self.settings['controls'] == 'arrows' else 'arrows'
        self.settings['controls'] = new_scheme
        self.logger.info(f"Control scheme changed to {new_scheme}")
        
        # Update ship's input component if it exists
        if self.entity_manager.ship:
            input_component = self.entity_manager.ship.get_component(InputComponent)
            if input_component:
                input_component.update_control_scheme(new_scheme)
                self.logger.debug("Ship input component updated with new control scheme")
            else:
                self.logger.warning("Ship exists but has no input component")
    
    def create_explosion(self, pos: pygame.Vector2, size: str = 'large') -> None:
        """Create an explosion effect.
        
        Args:
            pos: Position of the explosion
            size: Size of explosion ('small', 'medium', or 'large')
        """
        # Configure explosion based on size
        if size == 'large':
            count = 20  # More particles for large explosions
            speed = 250
            lifetime = (0.6, 0.8)
            particle_size = (3.0, 4.0)
        elif size == 'medium':
            count = 15  # More particles for medium explosions
            speed = 200
            lifetime = (0.4, 0.6)
            particle_size = (2.0, 3.0)
        else:  # small
            count = 10  # More particles for small explosions
            speed = 150
            lifetime = (0.2, 0.4)
            particle_size = (1.0, 2.0)
            
        # Create explosion particles
        for _ in range(count):
            # Create particle with random color from explosion palette
            color = random.choice([
                (255, 69, 0),   # Red-orange
                (255, 140, 0),  # Dark orange
                (255, 165, 0),  # Orange
                (255, 215, 0)   # Yellow
            ])
            
            # Create particle
            lifetime_value = random.uniform(lifetime[0], lifetime[1])
            size_value = random.uniform(particle_size[0], particle_size[1])
            particle = Particle(self, lifetime_value, color, size_value)
            
            # Set position and random velocity
            transform = particle.get_component(TransformComponent)
            if transform:
                transform.position = pygame.Vector2(pos)
                
                # Calculate random velocity direction
                angle = random.uniform(0, 2 * math.pi)
                velocity = pygame.Vector2(
                    math.cos(angle) * speed,
                    math.sin(angle) * speed
                )
                physics = particle.get_component(PhysicsComponent)
                if physics:
                    physics.velocity = velocity
                
                # Add particle to game
                self.entity_manager.add_entity(particle)
    
    def run(self):
        """Run the game."""
        self.game_loop.run()
    
    def toggle_sound(self):
        """Toggle sound on/off."""
        self.settings['sound'] = not self.settings['sound']
        self.audio.enabled = self.settings['sound']
    
    def _complete_level(self):
        """Handle level completion."""
        self.level += 1
        self.logger.info(f"Level {self.level} completed")
        
        if self.lives < 99:
            self.lives += 1
            self.logger.debug(f"Extra life awarded. Lives: {self.lives}")
        
        self.spawner.start_wave()