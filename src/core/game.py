"""Main game class."""
import pygame
import random
import numpy as np
from src.core.game_state import StateManager, GameState
from src.core.scoring import ScoringSystem
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.core.constants import (
    WINDOW_WIDTH, 
    WINDOW_HEIGHT,
    SHIP_INVULNERABLE_TIME,
    MAX_ASTEROIDS,
    STARTING_LIVES,
    ASTEROID_SIZES
)
import math

class Game:
    def __init__(self):
        """Initialize the game."""
        print("Game initialized")
        
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
            'controls': 'arrows'  # Default to arrow keys
        }
        
        # Initialize scoring system
        self.scoring = ScoringSystem()
        print("Scoring system initialized")
        
        # Initialize game properties
        self.dt = 0
        self.clock = pygame.time.Clock()
        self.running = True
        self.level = 1
        self.lives = STARTING_LIVES
        self.respawn_timer = 0.0
        self.ship = None
        print(f"Game initialized with {self.lives} lives")
        
        # Entity tracking
        self.entities = []
        self.bullets = []
        self.asteroids = []
        
        # Initialize state management (but don't set state yet)
        self.state_manager = StateManager(self)
        print("StateManager initialized")
        
        print("Game initialization complete")
        print(f"Game initialized with settings: {self.settings}")
        
        # Now set initial state
        self.state_manager.change_state(GameState.MAIN_MENU)
        print(f"Initial state set to: {self.state_manager.current_state}")
    
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
    
    def reset_game(self):
        """Reset the game state."""
        print("Resetting game...")  # Debug info
        
        # Clear entities
        self.entities.clear()
        self.asteroids.clear()
        self.bullets.clear()  # Clear bullets
        
        # Reset game properties
        self.level = 1
        self.lives = STARTING_LIVES
        self.scoring.reset()  # Use self.scoring instead of self.scoring_system
        
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
        
        # Remove old ship from entities list if it exists
        if self.ship in self.entities:
            self.entities.remove(self.ship)
        
        # Create new ship
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
        """Handle collisions between game entities."""
        if not self.ship:
            return
            
        # Check ship collision with asteroids
        if self.ship and not self.ship.invulnerable:
            ship_collision = self.ship.get_component('collision')
            if not ship_collision:
                return
                
            for asteroid in self.asteroids[:]:  # Use copy of list for safe iteration
                asteroid_collision = asteroid.get_component('collision')
                if not asteroid_collision:
                    continue
                    
                if ship_collision.check_collision(asteroid_collision):
                    print("Ship hit by asteroid")  # Debug info
                    self.lives -= 1
                    # Clear all bullets when ship is destroyed
                    self.bullets.clear()
                    if self.lives > 0:
                        self.respawn_ship()
                    else:
                        self.state_manager.change_state(GameState.GAME_OVER)
                    break  # Exit loop since ship is destroyed
        
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
                    print("Bullet hit asteroid")  # Debug info
                    
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
            transform1 = asteroid1.get_component('transform')
            if not collision1 or not transform1:
                continue
                
            for asteroid2 in self.asteroids[i+1:]:
                collision2 = asteroid2.get_component('collision')
                transform2 = asteroid2.get_component('transform')
                if not collision2 or not transform2:
                    continue
                    
                if collision1.check_collision(collision2):
                    # Calculate collision normal and depth
                    pos1 = pygame.Vector2(transform1.position)
                    pos2 = pygame.Vector2(transform2.position)
                    normal = (pos2 - pos1).normalize()
                    overlap = (collision1.radius + collision2.radius) - (pos2 - pos1).length()
                    
                    if overlap > 0:
                        # Separate asteroids
                        separation = normal * (overlap * 0.5)
                        transform1.position -= separation
                        transform2.position += separation
                        
                        # Get velocities
                        vel1 = pygame.Vector2(transform1.velocity)
                        vel2 = pygame.Vector2(transform2.velocity)
                        
                        # Calculate relative velocity
                        rel_vel = vel2 - vel1
                        
                        # Calculate impulse (elastic collision)
                        restitution = 0.8  # Bouncy collisions
                        impulse = -(1 + restitution) * rel_vel.dot(normal) / 2
                        
                        # Apply impulse
                        mass1 = ASTEROID_SIZES[asteroid1.size]['mass']
                        mass2 = ASTEROID_SIZES[asteroid2.size]['mass']
                        
                        transform1.velocity = vel1 - (normal * impulse / mass1)
                        transform2.velocity = vel2 + (normal * impulse / mass2)
                        
                        # Add some random spin
                        spin1 = random.uniform(-45, 45)
                        spin2 = random.uniform(-45, 45)
                        transform1.rotation_speed = spin1
                        transform2.rotation_speed = spin2
    
    def handle_input(self, event):
        """Handle input events."""
        if self.state_manager:
            self.state_manager.handle_input(event)

    def render(self):
        """Render the game state."""
        # Clear screen
        self.screen.fill((0, 0, 0))
        
        # Render based on current state
        if self.state_manager.current_state == GameState.PLAYING:
            # Render game entities
            if self.ship:
                render = self.ship.get_component('render')
                if render:
                    render.draw(self.screen)
            
            for asteroid in self.asteroids:
                render = asteroid.get_component('render')
                if render:
                    render.draw(self.screen)
            
            for bullet in self.bullets:
                render = bullet.get_component('render')
                if render:
                    render.draw(self.screen)
            
            # Render score
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (10, 10))
            
            # Render lives
            lives_text = font.render(f"Lives: {self.lives}", True, (255, 255, 255))
            self.screen.blit(lives_text, (10, 50))
        
        elif self.state_manager.current_state == GameState.MAIN_MENU:
            # Render menu
            font = pygame.font.Font(None, 64)
            title = font.render("ROGUE ASTEROID", True, (255, 255, 255))
            self.screen.blit(title, (self.width//2 - title.get_width()//2, 100))
            
            font = pygame.font.Font(None, 36)
            for i, option in enumerate(self.state_manager.menu_options[GameState.MAIN_MENU]):
                color = (255, 255, 0) if i == self.state_manager.selected_option else (255, 255, 255)
                text = font.render(option, True, color)
                self.screen.blit(text, (self.width//2 - text.get_width()//2, 300 + i*50))
        
        elif self.state_manager.current_state == GameState.GAME_OVER:
            # Render game over screen
            font = pygame.font.Font(None, 64)
            text = font.render("GAME OVER", True, (255, 0, 0))
            self.screen.blit(text, (self.width//2 - text.get_width()//2, self.height//2))
            
            font = pygame.font.Font(None, 36)
            score_text = font.render(f"Final Score: {self.score}", True, (255, 255, 255))
            self.screen.blit(score_text, (self.width//2 - score_text.get_width()//2, self.height//2 + 50))
        
        # Update display
        pygame.display.flip()

    def add_score(self, points):
        """Add points to the current score."""
        self.score += points
        # Check for high score
        if self.score > self.scoring.get_lowest_high_score():
            self.state_manager.change_state(GameState.NEW_HIGH_SCORE)

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
            self.render()
        
        pygame.quit()
        print("Game loop ended")  # Debug info

    def _handle_playing_input(self, event):
        """Handle input in the playing state."""
        if event.key in (pygame.K_ESCAPE, pygame.K_p):
            self.state_manager.change_state(GameState.PAUSED)
        elif event.key == pygame.K_o:
            self.state_manager.change_state(GameState.OPTIONS)
        elif event.key == pygame.K_h:
            self.state_manager.change_state(GameState.HIGH_SCORE)