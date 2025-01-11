"""Main game class."""
import pygame
from src.core.game_state import StateManager, GameState
from src.core.scoring import ScoringSystem
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.core.constants import (
    WINDOW_WIDTH, 
    WINDOW_HEIGHT,
    SHIP_INVULNERABLE_TIME
)
import random
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
        self.score = 0
        self.respawn_timer = 0.0  # Timer for ship respawn
        
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
    
    def update_entities(self):
        """Update all game entities."""
        # Update all entities
        for entity in self.entities[:]:  # Copy list to allow removal during iteration
            if entity:
                entity.update(self.dt)
        
        # Update scoring system and sync score
        self.scoring.update(self.dt)
        self.score = self.scoring.current_score
        
        # Handle ship respawning
        if self.ship is None and self.lives > 0:
            self.respawn_timer -= self.dt
            if self.respawn_timer <= 0:
                self.respawn_ship()
        
        # Check if we need to spawn more asteroids
        if len(self.asteroids) == 0:
            self.level += 1
            print(f"Level {self.level} completed! Awarding extra life.")  # Debug info
            self.lives = min(self.lives + 1, 5)  # Award life, cap at 5
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
        if not ship_collision:
            return
            
        # Check asteroid-asteroid collisions first
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
                    
                    # Simple direction calculation
                    direction = pygame.Vector2(
                        transform2.position.x - transform1.position.x,
                        transform2.position.y - transform1.position.y
                    )
                    
                    # If asteroids are exactly overlapping, use a random direction
                    if direction.length() == 0:
                        angle = random.uniform(0, 2 * math.pi)
                        direction = pygame.Vector2(math.cos(angle), math.sin(angle))
                    else:
                        direction = direction.normalize()
                    
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
                    
                    # Normalize and scale to maintain speed
                    if new_vel1.length() > 0:
                        new_vel1 = new_vel1.normalize() * avg_speed
                    if new_vel2.length() > 0:
                        new_vel2 = new_vel2.normalize() * avg_speed
                    
                    # Add subtle deflection
                    deflection = random.uniform(-0.15, 0.15)  # Even smoother deflection
                    transform1.velocity = new_vel1.rotate(deflection * 90)
                    transform2.velocity = new_vel2.rotate(deflection * 90)
                    
                    # Gentler spin
                    spin = random.uniform(10, 30)  # Reduced spin range further
                    transform1.rotation_speed = spin * (1 if random.random() > 0.5 else -1)
                    transform2.rotation_speed = spin * (1 if random.random() > 0.5 else -1)
                    
                    # Very minimal separation
                    separation = (collision1.radius + collision2.radius) * 0.2  # Further reduced separation
                    transform1.position -= direction * separation * 0.4
                    transform2.position += direction * separation * 0.4
        
        # Then check ship-asteroid collisions
        if self.ship:
            ship_collision = self.ship.get_component('collision')
            if not ship_collision:
                return
                
            for asteroid in self.asteroids[:]:  # Copy list to allow removal
                asteroid_collision = asteroid.get_component('collision')
                if not asteroid_collision:
                    continue
                    
                if ship_collision.check_collision(asteroid_collision):
                    self.lives -= 1
                    print(f"Ship hit! Lives remaining: {self.lives}")  # Debug info
                    
                    if self.lives <= 0:
                        print("Game Over!")  # Debug info
                        if self.ship in self.entities:
                            self.entities.remove(self.ship)
                        self.ship = None
                        self.state_manager.change_state(GameState.GAME_OVER)
                    else:
                        # Remove ship and set respawn timer
                        if self.ship in self.entities:
                            self.entities.remove(self.ship)
                        self.ship = None
                        self.respawn_timer = SHIP_INVULNERABLE_TIME  # Set respawn delay
                        print(f"Ship will respawn in {SHIP_INVULNERABLE_TIME} seconds")  # Debug info
    
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
                self.update_entities()
                self.handle_collisions()
            
            # Draw
            self.state_manager.draw(self.screen)
            pygame.display.flip()
        
        pygame.quit()
        print("Game loop ended")  # Debug info