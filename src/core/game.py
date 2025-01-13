"""Main game class."""
import pygame
import random
from src.core.game_state import StateManager, GameState
from src.core.services import AudioManager, HighScoreManager, ScoringSystem
from src.core.systems import ParticleSystem, Spawner
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.core.entities.components import (
    TransformComponent,
    CollisionComponent
)
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
        
        # Initialize services
        self.audio = AudioManager()
        self.high_scores = HighScoreManager()
        print("Services initialized")
        
        # Initialize systems
        self.particle_system = ParticleSystem(self)
        self.spawner = Spawner(self)
        print("Systems initialized")
        
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
        print("Entity lists initialized")
        
        # Initialize state management
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
    
    def new_game(self):
        """Start a new game."""
        print("Starting new game...")  # Debug info
        self.reset_game()
        print("Spawning player ship...")  # Debug info
        self.spawn_ship()
        print("Spawning initial asteroids...")  # Debug info
        self.spawn_asteroid_wave()
        # Don't change state here - let the state manager handle it
    
    def reset_game(self):
        """Reset the game state."""
        print("Resetting game...")  # Debug info
        
        # Clear entities
        self.entities.clear()
        self.asteroids.clear()
        self.bullets.clear()
        
        # Reset game properties
        self.level = 1
        self.lives = STARTING_LIVES
        self.scoring.reset()
        self.ship = None
        print("Game state reset complete")  # Debug info
    
    def spawn_ship(self):
        """Spawn the player's ship."""
        if self.ship is None:
            print("Creating new ship...")  # Debug info
            self.ship = Ship(self)
            self.entities.append(self.ship)
            # Set initial position
            transform = self.ship.get_component(TransformComponent)
            if transform:
                transform.position = pygame.Vector2(self.width // 2, self.height // 2)
                transform.rotation = 0.0
                print(f"Ship spawned at position {transform.position}")  # Debug info
            else:
                print("Warning: Ship missing transform component!")  # Debug info
    
    def spawn_asteroid_wave(self):
        """Spawn a wave of asteroids."""
        print(f"Spawning asteroid wave for level {self.level}")  # Debug info
        self.spawner.start_wave()
    
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
            self.state_manager.change_state(GameState.GAME_OVER)
        else:
            self.respawn_timer = SHIP_INVULNERABLE_TIME
            self.spawn_ship()
    
    def toggle_control_scheme(self):
        """Toggle between arrow keys and WASD controls."""
        current = self.settings['controls']
        self.settings['controls'] = 'wasd' if current == 'arrows' else 'arrows'
    
    def create_explosion(self, x: float, y: float, size: str = 'medium'):
        """Create an explosion effect."""
        # Play explosion sound
        self.audio.play_explosion(size)
        
        # Create particles
        position = pygame.Vector2(x, y)
        color = (255, 165, 0)  # Orange
        
        if size == 'large':
            self.particle_system.emit_circular(
                center=position,
                speed=150.0,
                color=color,
                size=3.0,
                lifetime=1.0,
                count=12
            )
        elif size == 'medium':
            self.particle_system.emit_circular(
                center=position,
                speed=100.0,
                color=color,
                size=2.0,
                lifetime=0.7,
                count=8
            )
        else:  # small
            self.particle_system.emit_circular(
                center=position,
                speed=50.0,
                color=color,
                size=1.0,
                lifetime=0.5,
                count=6
            )
    
    def update(self, dt: float) -> None:
        """Update game state."""
        self.dt = dt
        
        # Only update gameplay elements when in PLAYING state
        if self.state == GameState.PLAYING:
            # Update systems
            self.particle_system.update(dt)
            self.spawner.update(dt)
            
            # Update entities
            for entity in self.entities[:]:  # Copy list to allow removal during iteration
                entity.update(dt)
            
            # Handle collisions
            self.handle_collisions()
            
            # Check for wave completion
            if self.spawner.check_wave_complete():
                self.level += 1
                self.spawner.advance_wave()
        
        # Always update particles for visual effects
        elif self.state != GameState.PAUSED:
            self.particle_system.update(dt)
    
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
        ship_transform = self.ship.get_component(TransformComponent)
        if ship_transform:
            # Try to find a safe spawn position
            for attempt in range(10):  # Limit attempts
                ship_transform.position = pygame.Vector2(
                    random.randint(100, WINDOW_WIDTH - 100),
                    random.randint(100, WINDOW_HEIGHT - 100)
                )
                
                # Check if position is safe from asteroids
                ship_collision = self.ship.get_component(CollisionComponent)
                if not ship_collision:
                    continue
                    
                # Check distance to all asteroids
                safe_position = True
                for asteroid in self.asteroids:
                    asteroid_transform = asteroid.get_component(TransformComponent)
                    if asteroid_transform:
                        distance = (asteroid_transform.position - ship_transform.position).length()
                        if distance < 100:  # Minimum safe distance
                            safe_position = False
                            break
                
                if safe_position:
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
            ship_collision = self.ship.get_component(CollisionComponent)
            if not ship_collision:
                return
                
            for asteroid in self.asteroids[:]:  # Use copy of list for safe iteration
                asteroid_collision = asteroid.get_component(CollisionComponent)
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
            bullet_collision = bullet.get_component(CollisionComponent)
            if not bullet_collision:
                continue
                
            for asteroid in self.asteroids[:]:  # Copy list to allow removal
                asteroid_collision = asteroid.get_component(CollisionComponent)
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
            collision1 = asteroid1.get_component(CollisionComponent)
            transform1 = asteroid1.get_component(TransformComponent)
            if not collision1 or not transform1:
                continue
                
            for asteroid2 in self.asteroids[i+1:]:
                collision2 = asteroid2.get_component(CollisionComponent)
                transform2 = asteroid2.get_component(TransformComponent)
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
                    # Handle state manager input first
                    self.state_manager.handle_input(event)
                    
                    # Handle ship input when playing
                    if self.state == GameState.PLAYING and self.ship:
                        from src.core.entities.components import InputComponent
                        input_component = self.ship.get_component(InputComponent)
                        if input_component:
                            if event.type == pygame.KEYDOWN:
                                input_component.handle_keydown(event.key)
                            elif event.type == pygame.KEYUP:
                                input_component.handle_keyup(event.key)
            
            # Update game state
            self.update(self.dt)
            
            # Draw
            self.state_manager.draw(self.screen)
            pygame.display.flip()
        
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

    def add_entity(self, entity):
        """Add an entity to the game."""
        if entity not in self.entities:
            self.entities.append(entity)
            print(f"Added entity: {entity}")
            
    def remove_entity(self, entity):
        """Remove an entity from the game."""
        if entity in self.entities:
            self.entities.remove(entity)
            print(f"Removed entity: {entity}")
            
            # Also remove from specific lists if present
            if entity in self.bullets:
                self.bullets.remove(entity)
            if entity in self.asteroids:
                self.asteroids.remove(entity)
            if entity == self.ship:
                self.ship = None