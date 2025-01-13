"""Main game class."""
import random
import math
import pygame
from src.core.game_state import StateManager, GameState
from src.core.services import AudioManager, HighScoreManager, ScoringSystem
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
    PhysicsComponent
)
from src.core.constants import (
    WINDOW_WIDTH, 
    WINDOW_HEIGHT,
    STARTING_LIVES
)

class Game:
    def __init__(self):
        """Initialize the game."""
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
        
        # Initialize services
        self.audio = AudioManager()
        self.high_scores = HighScoreManager()
        
        # Initialize systems
        self.particle_system = ParticleSystem(self)
        self.spawner = Spawner(self)
        
        # Initialize managers
        self.entity_manager = EntityManager(self)
        self.collision_manager = CollisionManager(self)
        self.spawn_manager = SpawnManager(self)
        self.input_manager = InputManager(self)
        self.game_loop = GameLoopManager(self)
        
        # Initialize scoring system
        self.scoring = ScoringSystem()
        
        # Initialize game properties
        self.level = 1
        self.lives = STARTING_LIVES
        self.respawn_timer = 0.0
        
        # Initialize state management
        self.state_manager = StateManager(self)
        
        # Set initial state
        self.state_manager.change_state(GameState.MAIN_MENU)
    
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
        self.reset_game()
        self.spawn_manager.spawn_ship()
        self.spawner.start_wave()
    
    def reset_game(self):
        """Reset the game state."""
        # Clear entities
        self.entity_manager.clear_all()
        
        # Reset game properties
        self.level = 1
        self.lives = STARTING_LIVES
        self.scoring.reset()
    
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
        
        if self.lives <= 0:
            # Change to game over state - high score check happens there
            self.state_manager.change_state(GameState.GAME_OVER)
        else:
            self.spawn_manager.respawn_ship()
    
    def toggle_control_scheme(self):
        """Toggle between arrow keys and WASD controls."""
        current = self.settings['controls']
        self.settings['controls'] = 'wasd' if current == 'arrows' else 'arrows'
    
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
        
        # Award extra life every level, up to maximum of 99
        if self.lives < 99:
            self.lives += 1
            
        # Spawn new wave of asteroids for next level
        self.spawner.start_wave()