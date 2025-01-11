"""Main game class."""
import pygame
from src.core.game_state import StateManager, GameState
from src.core.scoring import ScoringSystem
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

class Game:
    def __init__(self):
        """Initialize the game."""
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Rogue Asteroid")
        
        self.clock = pygame.time.Clock()
        self.dt = 0
        self.running = True
        
        # Game properties
        self.level = 1
        self.lives = 3
        self.score = 0
        
        # Settings
        self.settings = {
            'controls': 'arrows'  # or 'wasd'
        }
        
        # Systems
        self.state_manager = StateManager(self)
        self.scoring = ScoringSystem()
        
        # Entities
        self.ship = None
        self.entities = []
        self.asteroids = []
        
        print("Game initialized")  # Debug info
    
    def reset_game(self):
        """Reset the game state."""
        print("Resetting game...")  # Debug info
        
        # Clear entities
        self.entities.clear()
        self.asteroids.clear()
        
        # Reset game properties
        self.level = 1
        self.lives = 3
        self.score = 0
        self.scoring.reset()
        
        # Create player ship
        self.ship = Ship(self)
        self.entities.append(self.ship)
        print(f"Ship created: {self.ship}")  # Debug info
        
        # Spawn initial asteroids
        self.spawn_asteroid_wave()
        
        print("Game reset complete")  # Debug info
    
    def spawn_asteroid_wave(self):
        """Spawn a wave of asteroids based on current level."""
        if not self.ship:
            return
            
        ship_transform = self.ship.get_component('transform')
        if not ship_transform:
            return
            
        num_asteroids = min(3 + self.level, 8)  # Cap at 8 asteroids
        for _ in range(num_asteroids):
            asteroid = Asteroid.spawn_random(self, ship_transform.position)
            self.asteroids.append(asteroid)
            self.entities.append(asteroid)
    
    def update_entities(self):
        """Update all game entities."""
        # Update all entities
        for entity in self.entities[:]:  # Copy list to allow removal during iteration
            if entity:
                entity.update(self.dt)
    
    def handle_collisions(self):
        """Handle collisions between entities."""
        if not self.ship:
            return
            
        # Check ship collision with asteroids
        ship_collision = self.ship.get_component('collision')
        if not ship_collision:
            return
            
        for asteroid in self.asteroids[:]:  # Copy list to allow removal
            asteroid_collision = asteroid.get_component('collision')
            if not asteroid_collision:
                continue
                
            if ship_collision.check_collision(asteroid_collision):
                self.lives -= 1
                if self.lives <= 0:
                    self.state_manager.change_state(GameState.GAME_OVER)
                else:
                    # Respawn ship after delay
                    self.ship = None
                    self.entities.remove(self.ship)
    
    def run(self):
        """Main game loop."""
        print("Starting game loop")  # Debug info
        
        while self.running:
            # Time
            self.dt = self.clock.tick(60) / 1000.0
            
            # Event handling
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                else:
                    self.state_manager.handle_input(event)
            
            # Update game state
            if self.state_manager.current_state == GameState.PLAYING:
                self.update_entities()
                self.handle_collisions()
            
            # Draw
            self.state_manager.draw(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        print("Game loop ended")  # Debug info