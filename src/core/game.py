"""Main game class."""
import pygame
import random
import numpy as np
from src.core.game_state import StateManager, GameState
from src.core.scoring import ScoringSystem
from src.core.sound import SoundManager
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.core.constants import (
    WINDOW_WIDTH, 
    WINDOW_HEIGHT,
    SHIP_INVULNERABLE_TIME,
    MAX_ASTEROIDS
)
import math

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
        self.respawn_timer = 0.0  # Timer for ship respawn
        
        # Settings
        self.settings = {
            'controls': 'arrows'  # or 'wasd'
        }
        
        # Systems
        self.state_manager = StateManager(self)
        self.scoring = ScoringSystem()
        
        # Initialize sound system
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init()
            self.sound = SoundManager()
            print("Sound system initialized successfully")  # Debug info
        except Exception as e:
            print(f"Warning: Sound system initialization failed: {e}")
            self.sound = None
        
        # Entities
        self.ship = None
        self.entities = []
        self.asteroids = []
        self.bullets = []  # Track active bullets
        
        print("Game initialized")  # Debug info
    
    def reset_game(self):
        """Reset the game state."""
        print("Resetting game...")  # Debug info
        
        # Clear entities
        self.entities.clear()
        self.asteroids.clear()
        self.bullets.clear()  # Clear bullets
        
        # Reset game properties
        self.level = 1
        self.lives = 3
        self.score = 0  # Reset score
        self.scoring.reset()  # Reset scoring system
        
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
            # Try to find a valid spawn position
            for attempt in range(10):  # Limit attempts to prevent infinite loop
                asteroid = Asteroid.spawn_random(self, ship_transform.position)
                transform = asteroid.get_component('transform')
                if not transform:
                    continue
                    
                # Check distance from other asteroids
                position = pygame.Vector2(transform.position)
                collision = asteroid.get_component('collision')
                if not collision:
                    continue
                    
                # Check if too close to other asteroids
                too_close = False
                for other_asteroid in self.asteroids:
                    other_collision = other_asteroid.get_component('collision')
                    if not other_collision:
                        continue
                        
                    other_pos = other_asteroid.get_component('transform').position
                    min_distance = (collision.radius + other_collision.radius) * 1.5  # 50% buffer
                    if (pygame.Vector2(position) - pygame.Vector2(other_pos)).length() < min_distance:
                        too_close = True
                        break
                
                if not too_close:
                    self.asteroids.append(asteroid)
                    self.entities.append(asteroid)
                    print(f"Spawned asteroid at {position}")  # Debug info
                    break
                else:
                    # Remove invalid asteroid
                    del asteroid
    
    def update(self, dt):
        """Update game state."""
        # Handle ship respawn timer
        if self.ship is None and self.lives > 0:
            self.respawn_timer -= dt
            if self.respawn_timer <= 0:
                print("Respawning ship...")  # Debug info
                self.respawn_ship()
        
        # Update all entities
        for entity in self.entities[:]:  # Use copy to allow removal
            entity.update(dt)
            
        # Handle collisions
        self.handle_collisions()
        
        # Check for level completion
        if len(self.asteroids) == 0:
            print(f"Level {self.level} complete!")  # Debug info
            if self.sound:
                self.sound.play_sound('level_complete')  # Play level complete sound
            
            # Increment level
            self.level += 1
            
            # Award extra life every two levels, max 5 lives
            if self.level % 2 == 0 and self.lives < 5:
                self.lives += 1
                print(f"Extra life awarded! Lives: {self.lives}")  # Debug info
            
            # Spawn new wave of asteroids
            self.spawn_asteroid_wave()
    
    def respawn_ship(self):
        """Respawn the player ship with invulnerability."""
        print(f"Respawning ship with {SHIP_INVULNERABLE_TIME} seconds invulnerability")  # Debug info
        self.ship = Ship(self)
        self.entities.append(self.ship)
        
        # Set initial invulnerability
        self.ship.invulnerable_timer = SHIP_INVULNERABLE_TIME
        
        # Make sure ship spawns in a safe location
        ship_transform = self.ship.get_component('transform')
        if ship_transform:
            # Try to find a safe spawn position
            for attempt in range(10):  # Limit attempts
                ship_transform.position = pygame.Vector2(
                    random.randint(100, WINDOW_WIDTH - 100),
                    random.randint(100, WINDOW_HEIGHT - 100)
                )
                
                # Check if position is safe from asteroids
                ship_collision = self.ship.get_component('collision')
                if not ship_collision:
                    break
                    
                safe_position = True
                for asteroid in self.asteroids:
                    asteroid_collision = asteroid.get_component('collision')
                    if not asteroid_collision:
                        continue
                        
                    distance = (pygame.Vector2(ship_transform.position) - 
                              pygame.Vector2(asteroid.get_component('transform').position)).length()
                    min_distance = (ship_collision.radius + asteroid_collision.radius) * 2.0
                    
                    if distance < min_distance:
                        safe_position = False
                        break
                
                if safe_position:
                    print(f"Ship respawned at safe position: {ship_transform.position}")  # Debug info
                    break
            
            # If no safe position found, just use center
            if not safe_position:
                ship_transform.position = pygame.Vector2(WINDOW_WIDTH/2, WINDOW_HEIGHT/2)
                print("No safe position found, respawning at center")  # Debug info
    
    def handle_collisions(self):
        """Handle collisions between entities."""
        if not self.ship:
            return
            
        # Check ship collision with asteroids
        ship_collision = self.ship.get_component('collision')
        if ship_collision and ship_collision.active:
            for asteroid in self.asteroids[:]:  # Copy list to allow removal
                asteroid_collision = asteroid.get_component('collision')
                if not asteroid_collision:
                    continue
                    
                if ship_collision.check_collision(asteroid_collision):
                    print("Ship collided with asteroid")  # Debug info
                    self.lives -= 1
                    print(f"Lives remaining: {self.lives}")  # Debug info
                    
                    # Play explosion sound
                    self.sound.play_sound('explosion_medium')
                    
                    # Remove ship from entities
                    if self.ship in self.entities:
                        self.entities.remove(self.ship)
                    self.ship = None
                    
                    if self.lives <= 0:
                        print("Game Over!")  # Debug info
                        self.sound.play_sound('game_over')
                        self.state_manager.change_state(GameState.GAME_OVER)
                    else:
                        self.respawn_timer = 2.0  # Wait 2 seconds before respawning
                    break
        
        # Check bullet collisions with asteroids
        for bullet in self.bullets[:]:  # Copy list to allow removal
            bullet_collision = bullet.get_component('collision')
            if not bullet_collision:
                continue
                
            for asteroid in self.asteroids[:]:  # Copy list to allow removal
                asteroid_collision = asteroid.get_component('collision')
                if not asteroid_collision:
                    continue
                    
                if bullet_collision.check_collision(asteroid_collision):
                    print(f"Bullet hit asteroid")  # Debug info
                    
                    # Play explosion sound based on asteroid size
                    if asteroid.size == 'large':
                        self.sound.play_sound('explosion_large')
                    elif asteroid.size == 'medium':
                        self.sound.play_sound('explosion_medium')
                    else:
                        self.sound.play_sound('explosion_small')
                    
                    # Create new asteroids from split
                    new_asteroids = asteroid.split()
                    
                    # Remove bullet and original asteroid
                    if bullet in self.entities:
                        self.entities.remove(bullet)
                    if bullet in self.bullets:
                        self.bullets.remove(bullet)
                    if asteroid in self.entities:
                        self.entities.remove(asteroid)
                    if asteroid in self.asteroids:
                        self.asteroids.remove(asteroid)
                    
                    # Add new asteroids from split
                    for new_asteroid in new_asteroids:
                        self.asteroids.append(new_asteroid)
                        self.entities.append(new_asteroid)
                    
                    break  # Bullet can only hit one asteroid
        
        # Check asteroid-asteroid collisions
        for i, asteroid1 in enumerate(self.asteroids[:-1]):
            collision1 = asteroid1.get_component('collision')
            if not collision1:
                continue
                
            for asteroid2 in self.asteroids[i+1:]:
                collision2 = asteroid2.get_component('collision')
                if not collision2:
                    continue
                    
                if collision1.check_collision(collision2):
                    # Get transforms
                    transform1 = asteroid1.get_component('transform')
                    transform2 = asteroid2.get_component('transform')
                    if not transform1 or not transform2:
                        continue
                    
                    # Get collision normal and depth
                    normal = collision1.get_collision_normal(collision2)
                    if not normal:
                        continue
                        
                    depth = collision1.get_collision_depth(collision2)
                    
                    # Separate asteroids
                    transform1.position -= normal * (depth * 0.5)
                    transform2.position += normal * (depth * 0.5)
                    
                    # Get current speeds
                    speed1 = transform1.velocity.length()
                    speed2 = transform2.velocity.length()
                    avg_speed = (speed1 + speed2) * 0.5  # Use average speed
                    
                    # Blend velocities with speed preservation
                    vel1 = pygame.Vector2(transform1.velocity)
                    vel2 = pygame.Vector2(transform2.velocity)
                    
                    # Calculate new velocities (80% new, 20% old)
                    new_vel1 = pygame.Vector2(
                        vel1.x * 0.2 + vel2.x * 0.8,
                        vel1.y * 0.2 + vel2.y * 0.8
                    )
                    new_vel2 = pygame.Vector2(
                        vel2.x * 0.2 + vel1.x * 0.8,
                        vel2.y * 0.2 + vel1.y * 0.8
                    )
                    
                    # Normalize and scale to maintain average speed
                    if new_vel1.length() > 0:
                        new_vel1.scale_to_length(avg_speed)
                    if new_vel2.length() > 0:
                        new_vel2.scale_to_length(avg_speed)
                    
                    # Apply new velocities
                    transform1.velocity = new_vel1
                    transform2.velocity = new_vel2
    
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
                    
                    # Handle ship input when playing
                    if self.state_manager.current_state == GameState.PLAYING and self.ship:
                        input_component = self.ship.get_component('input')
                        if input_component:
                            if event.type == pygame.KEYDOWN:
                                input_component.handle_keydown(event.key)
                            elif event.type == pygame.KEYUP:
                                input_component.handle_keyup(event.key)
            
            # Update game state
            if self.state_manager.current_state == GameState.PLAYING:
                self.update(self.dt)
            
            # Draw
            self.state_manager.draw(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        print("Game loop ended")  # Debug info