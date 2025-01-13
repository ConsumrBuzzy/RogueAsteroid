"""Main game class."""
import pygame
import random
from src.core.game_state import StateManager, GameState
from src.core.services import AudioManager, HighScoreManager, ScoringSystem
from src.core.systems import ParticleSystem, Spawner, CollisionSystem
from src.entities.ship import Ship
from src.entities.bullet import Bullet
from src.entities.asteroid import Asteroid
from src.core.entities.components import (
    TransformComponent,
    CollisionComponent,
    PhysicsComponent
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
            'controls': 'arrows',  # Default to arrow keys
            'sound': False  # Default to sound off
        }
        
        # Initialize services
        self.audio = AudioManager()
        self.high_scores = HighScoreManager()
        print("Services initialized")
        
        # Initialize systems
        self.particle_system = ParticleSystem(self)
        self.spawner = Spawner(self)
        self.collision_system = CollisionSystem(self)
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
        print(f"Losing life. Lives remaining: {self.lives - 1}")  # Debug info
        self.lives -= 1
        
        if self.lives <= 0:
            print("Game Over - No lives remaining")  # Debug info
            self.state_manager.change_state(GameState.GAME_OVER)
        else:
            print(f"Respawning with {self.lives} lives remaining")  # Debug info
            # Remove the old ship
            if self.ship in self.entities:
                self.entities.remove(self.ship)
                self.ship = None
            
            # Set respawn timer
            self.respawn_timer = SHIP_INVULNERABLE_TIME
            
            # Respawn ship with invulnerability
            self.respawn_ship()
            
            # Ensure ship is properly initialized
            if self.ship:
                self.ship.invulnerable = True
                self.ship.invulnerable_timer = SHIP_INVULNERABLE_TIME
                print("Ship respawned with invulnerability")  # Debug info
            else:
                print("Error: Failed to respawn ship!")  # Debug info
    
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
            lifetime = random.uniform(*lifetime)
            size = random.uniform(*particle_size)
            particle = Particle(self.game, lifetime, color, size)
            
            # Set position and random velocity
            transform = particle.get_component(TransformComponent)
            physics = particle.get_component(PhysicsComponent)
            if transform and physics:
                transform.position = pygame.Vector2(pos)
                
                # Random direction
                angle = random.uniform(0, 360)
                angle_rad = math.radians(angle)
                
                # Random speed
                speed_var = random.uniform(0.8, 1.2) * speed
                velocity = pygame.Vector2(
                    math.cos(angle_rad) * speed_var,
                    math.sin(angle_rad) * speed_var
                )
                physics.velocity = velocity
            
            # Add to game
            self.entities.append(particle)
    
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
            self.collision_system.update()
            
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
    
    def _handle_ship_asteroid_collision(self, ship: Ship, asteroid: Asteroid):
        """Handle collision between ship and asteroid."""
        if not ship.invulnerable:
            print("Ship hit by asteroid")  # Debug info
            # Create explosion before losing life
            transform = ship.get_component(TransformComponent)
            if transform:
                self.create_explosion(transform.position, 'medium')
            self.lose_life()
    
    def _handle_bullet_asteroid_collision(self, bullet: Bullet, asteroid: Asteroid):
        """Handle collision between bullet and asteroid."""
        print(f"Bullet hit asteroid size {asteroid.size}")  # Debug info
        
        # Award points based on asteroid size
        points = {'large': 3, 'medium': 2, 'small': 1}
        self.scoring.add_points(points[asteroid.size])
        print(f"Hit asteroid size {asteroid.size}, awarded {points[asteroid.size]} points")
        
        # Create explosion effect
        transform = asteroid.get_component(TransformComponent)
        if transform:
            self.create_explosion(transform.position, asteroid.size)
        
        # Split asteroid
        pieces = asteroid.split()
        
        # Add new pieces to game
        for piece in pieces:
            self.asteroids.append(piece)
            self.entities.append(piece)
        
        # Remove bullet and asteroid
        self.remove_entity(bullet)
        self.remove_entity(asteroid)
    
    def handle_collisions(self):
        """Handle collisions between entities."""
        # Get all entities with collision components
        collidable_entities = [
            entity for entity in self.entities 
            if entity.get_component(CollisionComponent)
        ]
        
        # Check each pair of entities
        for i, entity1 in enumerate(collidable_entities):
            for entity2 in collidable_entities[i + 1:]:
                # Get collision components
                collision1 = entity1.get_component(CollisionComponent)
                collision2 = entity2.get_component(CollisionComponent)
                
                # Get transform components
                transform1 = entity1.get_component(TransformComponent)
                transform2 = entity2.get_component(TransformComponent)
                
                # Get physics components
                physics1 = entity1.get_component(PhysicsComponent)
                physics2 = entity2.get_component(PhysicsComponent)
                
                if not (collision1 and collision2 and transform1 and transform2):
                    continue
                    
                # Get positions
                pos1 = pygame.Vector2(transform1.position)
                pos2 = pygame.Vector2(transform2.position)
                
                # Calculate distance
                distance = pos1.distance_to(pos2)
                combined_radius = collision1.radius + collision2.radius
                
                # Check for collision
                if distance < combined_radius:
                    # Calculate collision normal
                    diff = pos2 - pos1
                    if diff.length() > 0:  # Prevent division by zero
                        normal = diff.normalize()
                    else:
                        normal = pygame.Vector2(1, 0)  # Default direction if positions are identical
                    
                    # Handle collision based on entity types
                    if isinstance(entity1, Ship) and isinstance(entity2, Asteroid):
                        self._handle_ship_asteroid_collision(entity1, entity2)
                    elif isinstance(entity1, Asteroid) and isinstance(entity2, Ship):
                        self._handle_ship_asteroid_collision(entity2, entity1)
                    elif isinstance(entity1, Bullet) and isinstance(entity2, Asteroid):
                        self._handle_bullet_asteroid_collision(entity1, entity2)
                    elif isinstance(entity1, Asteroid) and isinstance(entity2, Bullet):
                        self._handle_bullet_asteroid_collision(entity2, entity1)
                    elif isinstance(entity1, Asteroid) and isinstance(entity2, Asteroid):
                        # Only bounce asteroids if they both have physics components
                        if physics1 and physics2:
                            # Get velocities and masses
                            vel1 = pygame.Vector2(physics1.velocity)
                            vel2 = pygame.Vector2(physics2.velocity)
                            
                            # Get masses from asteroid sizes
                            mass1 = ASTEROID_SIZES[entity1.size]['mass']
                            mass2 = ASTEROID_SIZES[entity2.size]['mass']
                            
                            # Calculate relative velocity
                            rel_vel = vel1 - vel2
                            
                            # Calculate collision response
                            restitution = 0.8  # More bouncy
                            
                            # Calculate impulse magnitude
                            vel_along_normal = rel_vel.dot(normal)
                            if vel_along_normal > 0:
                                continue  # Skip if asteroids are moving apart
                                
                            # Calculate impulse scalar
                            j = -(1 + restitution) * vel_along_normal
                            j /= (1/mass1 + 1/mass2)
                            
                            # Apply impulse
                            impulse = normal * j
                            physics1.velocity = vel1 + (impulse / mass1)
                            physics2.velocity = vel2 - (impulse / mass2)
                            
                            # Separate the asteroids (prevent overlap)
                            overlap = combined_radius - distance
                            percent = 0.5  # Penetration resolution percentage
                            separation = normal * (overlap * percent)
                            transform1.position -= separation
                            transform2.position += separation
                            
                            # Add some spin based on collision angle and impulse magnitude
                            spin_factor = 0.5
                            tangent = pygame.Vector2(-normal.y, normal.x)
                            physics1.angular_velocity = rel_vel.dot(tangent) * spin_factor
                            physics2.angular_velocity = -rel_vel.dot(tangent) * spin_factor
    
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
    
    def toggle_sound(self):
        """Toggle sound on/off."""
        self.settings['sound'] = not self.settings['sound']
        self.audio.enabled = self.settings['sound']