"""Core game loop and state management."""
import pygame
import numpy as np
from typing import List, Optional, Dict, Any
from src.core.constants import (
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    FPS,
    BLACK,
    INITIAL_LIVES
)
from src.core.game_state import StateManager
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet

class Game:
    """Main game class managing entities and game loop."""
    
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Rogue Asteroid")
        self.clock = pygame.time.Clock()
        
        # Game properties
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.dt = 0.0
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        
        # Settings with defaults
        self.settings: Dict[str, Any] = {
            'controls': {
                'scheme': 'arrows'  # or 'wasd'
            }
        }
        
        # Entity management
        self.entities: List[Any] = []
        self.ship: Optional[Ship] = None
        self.asteroids: List[Asteroid] = []
        
        # State management
        self.state_manager = StateManager(self)
    
    def reset_game(self) -> None:
        """Reset game state for new game."""
        self.score = 0
        self.lives = INITIAL_LIVES
        self.level = 1
        self.entities.clear()
        self.asteroids.clear()
        
        # Create player ship
        self.ship = Ship(self)
        self.entities.append(self.ship)
        
        # Spawn initial asteroids
        self.spawn_asteroid_wave()
    
    def spawn_asteroid_wave(self) -> None:
        """Spawn a wave of asteroids based on current level."""
        num_asteroids = 2 + self.level
        
        for _ in range(num_asteroids):
            # Spawn asteroids away from player
            while True:
                x = np.random.uniform(0, WINDOW_WIDTH)
                y = np.random.uniform(0, WINDOW_HEIGHT)
                
                if self.ship:
                    dist = np.hypot(x - self.ship.get_component('transform').position[0],
                                  y - self.ship.get_component('transform').position[1])
                    if dist > 200:  # Minimum safe distance
                        break
                else:
                    break
            
            asteroid = Asteroid(self, x, y, 'large')
            self.asteroids.append(asteroid)
            self.entities.append(asteroid)
    
    def update_entities(self) -> None:
        """Update all game entities."""
        # Handle ship respawn
        if self.ship and hasattr(self, 'respawn_timer'):
            self.respawn_timer -= self.dt
            if self.respawn_timer <= 0:
                # Reset ship state
                transform = self.ship.get_component('transform')
                if transform:
                    transform.position = np.array([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
                    transform.velocity = np.array([0.0, 0.0])
                
                self.ship.get_component('render').visible = True
                self.ship.get_component('collision').active = True
                delattr(self, 'respawn_timer')
        
        # Update all entities
        for entity in self.entities[:]:  # Copy list for safe removal
            entity.update(self.dt)
    
    def handle_collisions(self) -> None:
        """Handle collisions between entities."""
        if not self.ship:
            return
            
        ship_collision = self.ship.get_component('collision')
        if not ship_collision:
            return
            
        # Check ship collision with asteroids
        for asteroid in self.asteroids[:]:  # Copy list for safe removal
            asteroid_collision = asteroid.get_component('collision')
            if not asteroid_collision:
                continue
                
            if ship_collision.check_collision(asteroid_collision):
                # Get collision details
                collision_normal = ship_collision.get_collision_normal(asteroid_collision)
                if collision_normal is not None:
                    # Apply knockback to ship
                    ship_physics = self.ship.get_component('physics')
                    if ship_physics:
                        knockback = collision_normal * 200.0  # Knockback force
                        ship_physics.velocity = knockback
                
                # Reduce lives and handle ship destruction
                self.lives -= 1
                ship_collision.active = False  # Disable collisions temporarily
                
                if self.lives <= 0:
                    self.entities.remove(self.ship)
                    self.ship = None
                    self.state_manager.change_state(GameState.GAME_OVER)
                else:
                    # Respawn ship after delay
                    self.ship.get_component('render').visible = False
                    self.respawn_timer = 2.0  # Seconds until respawn
                break
        
        # Check bullet collisions with asteroids
        for entity in self.entities[:]:  # Copy list for safe removal
            if not isinstance(entity, Bullet):
                continue
                
            bullet_collision = entity.get_component('collision')
            if not bullet_collision:
                continue
                
            for asteroid in self.asteroids[:]:  # Copy list for safe removal
                asteroid_collision = asteroid.get_component('collision')
                if not asteroid_collision:
                    continue
                    
                if bullet_collision.check_collision(asteroid_collision):
                    # Remove bullet
                    if entity in self.entities:
                        self.entities.remove(entity)
                    
                    # Split asteroid
                    new_asteroids = asteroid.split()
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)
                    if asteroid in self.entities:
                        self.entities.remove(asteroid)
                    
                    # Add score
                    self.score += asteroid.config['points']
                    
                    # Add new asteroids
                    for new_asteroid in new_asteroids:
                        self.asteroids.append(new_asteroid)
                        self.entities.append(new_asteroid)
                    break
    
    def run(self) -> None:
        """Main game loop."""
        while True:
            # Update timing
            self.dt = self.clock.tick(FPS) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if self.state_manager.handle_input(event):
                    pygame.quit()
                    return
                
                # Handle entity input
                if event.type in [pygame.KEYDOWN, pygame.KEYUP]:
                    for entity in self.entities:
                        input_component = entity.get_component('input')
                        if input_component:
                            if event.type == pygame.KEYDOWN:
                                input_component.handle_keydown(event.key)
                            else:
                                input_component.handle_keyup(event.key)
            
            # Update game state
            self.state_manager.update()
            
            # Draw
            self.screen.fill(BLACK)
            self.state_manager.draw(self.screen)
            pygame.display.flip() 