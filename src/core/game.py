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
from src.core.game_state import StateManager, GameState
from src.core.scoring import ScoringSystem
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet

class Game:
    """Main game class managing entities and game loop."""
    
    def __init__(self):
        """Initialize game."""
        pygame.init()
        
        # Initialize display
        self.width = WINDOW_WIDTH
        self.height = WINDOW_HEIGHT
        self.screen = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Rogue Asteroid')
        
        # Initialize clock
        self.clock = pygame.time.Clock()
        self.dt = 0
        
        # Game settings
        self.settings = {
            'controls': {
                'scheme': 'arrows'  # or 'wasd'
            }
        }
        
        # Initialize state manager
        self.state_manager = StateManager(self)
        
        # Initialize game objects
        self.ship = None
        self.entities = []
        self.asteroids = []
        self.level = 1
        
        # Reset game to initialize entities
        self.reset_game()
    
    def reset_game(self) -> None:
        """Reset game state."""
        print("Resetting game...")  # Debug info
        
        # Clear entities
        self.entities.clear()
        self.asteroids.clear()
        
        # Create player ship
        self.ship = Ship(self)
        if not self.ship:
            print("Failed to create ship!")  # Debug info
            return
            
        # Initialize ship components
        transform = self.ship.get_component('transform')
        render = self.ship.get_component('render')
        if not transform or not render:
            print("Ship components missing!")  # Debug info
            return
            
        # Set ship position and visibility
        transform.position = np.array([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
        transform.velocity = np.array([0.0, 0.0])
        render.visible = True
        print(f"Ship position: {transform.position}, visible: {render.visible}")  # Debug info
        
        # Add ship to entities
        self.entities.append(self.ship)
        
        # Reset level and spawn asteroids
        self.level = 1
        self.spawn_asteroid_wave()
        
        # Change state to PLAYING if state manager exists
        if self.state_manager:
            print("Changing state to PLAYING")  # Debug info
            self.state_manager.change_state(GameState.PLAYING)
        else:
            print("No state manager found!")  # Debug info
    
    def spawn_asteroid_wave(self) -> None:
        """Spawn a wave of asteroids based on current level."""
        if not self.ship:
            return
            
        num_asteroids = 2 + self.level
        ship_transform = self.ship.get_component('transform')
        if not ship_transform:
            return
        
        for _ in range(num_asteroids):
            # Spawn asteroids away from player
            while True:
                x = np.random.uniform(0, WINDOW_WIDTH)
                y = np.random.uniform(0, WINDOW_HEIGHT)
                
                dist = np.hypot(x - ship_transform.position[0],
                              y - ship_transform.position[1])
                if dist > 200:  # Minimum safe distance
                    break
            
            asteroid = Asteroid(self, x, y, 'large')
            self.asteroids.append(asteroid)
            self.entities.append(asteroid)
    
    def update_entities(self) -> None:
        """Update all game entities."""
        # Update scoring system
        self.scoring.update(self.dt)
        
        # Handle ship respawn
        if self.ship and hasattr(self, 'respawn_timer'):
            self.respawn_timer -= self.dt
            if self.respawn_timer <= 0:
                # Reset ship state
                transform = self.ship.get_component('transform')
                if transform:
                    transform.position = np.array([WINDOW_WIDTH/2, WINDOW_HEIGHT/2])
                    transform.velocity = np.array([0.0, 0.0])
                
                render = self.ship.get_component('render')
                if render:
                    render.visible = True
                
                collision = self.ship.get_component('collision')
                if collision:
                    collision.active = True
                
                delattr(self, 'respawn_timer')
        
        # Update all entities
        for entity in self.entities[:]:  # Copy list for safe removal
            if entity:  # Ensure entity exists
                entity.update(self.dt)
    
    def handle_collisions(self) -> None:
        """Handle collisions between entities."""
        if not self.ship:
            return
            
        ship_collision = self.ship.get_component('collision')
        if not ship_collision or not ship_collision.active:
            return
            
        # Check ship collision with asteroids
        for asteroid in self.asteroids[:]:  # Copy list for safe removal
            if not asteroid:  # Skip if asteroid was removed
                continue
                
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
                    if self.ship in self.entities:
                        self.entities.remove(self.ship)
                    self.ship = None
                    
                    # Check for high score
                    if self.scoring.check_high_score():
                        self.state_manager.change_state(GameState.HIGH_SCORE_ENTRY)
                    else:
                        self.state_manager.change_state(GameState.GAME_OVER)
                else:
                    # Respawn ship after delay
                    render = self.ship.get_component('render')
                    if render:
                        render.visible = False
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
                if not asteroid:  # Skip if asteroid was removed
                    continue
                    
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
                    
                    # Add score with combo system
                    points = self.scoring.add_points(asteroid.config['points'])
                    
                    # Add new asteroids
                    for new_asteroid in new_asteroids:
                        self.asteroids.append(new_asteroid)
                        self.entities.append(new_asteroid)
                    break
    
    def run(self) -> None:
        """Main game loop."""
        running = True
        while running:
            # Update timing
            self.dt = self.clock.tick(60) / 1000.0
            
            # Handle events
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_o and self.state_manager.current_state == GameState.MAIN_MENU:
                        self.state_manager.change_state(GameState.OPTIONS)
                    elif event.key == pygame.K_m and self.state_manager.current_state == GameState.PAUSED:
                        self.state_manager.change_state(GameState.MAIN_MENU)
                        self.reset_game()
                
                if self.state_manager.handle_input(event):
                    running = False
                    break
            
            # Update game state
            self.state_manager.update()
            
            # Clear screen
            self.screen.fill((0, 0, 0))
            
            # Draw current state
            self.state_manager.draw(self.screen)
            
            # Update display
            pygame.display.flip()
        
        pygame.quit() 