"""Ship entity for the game."""
import math
import random
import pygame
from typing import TYPE_CHECKING, Optional
from src.core.entities.base import Entity
from src.core.entities.components import (
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    PhysicsComponent,
    InputComponent,
    EffectComponent,
    ScreenWrapComponent
)
from src.core.constants import (
    SHIP_ACCELERATION,
    SHIP_MAX_SPEED,
    SHIP_ROTATION_SPEED,
    SHIP_FRICTION,
    WHITE,
    MAX_BULLETS
)
from src.entities.bullet import Bullet
from src.entities.particle import Particle

# Debug flag
DEBUG = False  # Set to True to enable debug output

if TYPE_CHECKING:
    from src.core.game import Game

class Ship(Entity):
    """Player controlled ship entity."""
    
    SHOOT_COOLDOWN = 0.20  # Reduced from 0.25 to 0.20 seconds between shots
    
    def __init__(self, game: 'Game'):
        super().__init__(game)
        print("Initializing ship...")  # Debug info
        self.shoot_timer = 0.0
        self.invulnerable_timer = 0.0
        self.input_component = None
        
        # Add components
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize ship components."""
        # Transform component for position and movement
        transform = self.add_component(TransformComponent)
        transform.position = pygame.Vector2(self.game.width / 2, self.game.height / 2)
        transform.rotation = 0.0
        print(f"Transform component added: {transform}")  # Debug info
        
        # Render component for drawing
        render = self.add_component(RenderComponent)
        render.vertices = [(0, -20), (-10, 10), (10, 10)]  # Triangle shape
        render.color = WHITE
        print(f"Render component added: {render}")  # Debug info
        
        # Physics component for thrust and momentum
        physics = self.add_component(PhysicsComponent)
        physics.max_speed = SHIP_MAX_SPEED
        physics.friction = SHIP_FRICTION
        print(f"Physics component added: {physics}")  # Debug info
        
        # Collision component for hit detection
        collision = self.add_component(CollisionComponent, radius=15)
        print(f"Collision component added: {collision}")  # Debug info
        
        # Screen wrap component to wrap around screen edges
        screen_wrap = self.add_component(ScreenWrapComponent)
        print(f"Screen wrap component added: {screen_wrap}")  # Debug info
        
        # Effects component for visual effects
        effects = self.add_component(EffectComponent)
        self._init_thrust_effect(effects)
        print(f"Effects component added: {effects}")  # Debug info
        
        # Input component for controls
        self.input_component = self.add_component(InputComponent)
        self.update_controls()  # Initialize controls
        print(f"Input component added: {self.input_component}")  # Debug info
    
    def update_controls(self) -> None:
        """Update control bindings based on current control scheme."""
        if not self.input_component:
            print("Warning: No input component found!")  # Debug info
            return
            
        # Clear existing bindings by creating a new empty dict
        self.input_component.key_bindings = {}
        
        # Get current control scheme
        controls = self.game.settings.get('controls', 'arrows')
        print(f"Controls updated to scheme: {controls}")  # Debug info
        
        if controls == 'arrows':
            # Arrow key controls
            self.input_component.bind_key(pygame.K_UP, self.handle_thrust, continuous=True)
            self.input_component.bind_key(pygame.K_LEFT, self.handle_rotate_left, continuous=True)
            self.input_component.bind_key(pygame.K_RIGHT, self.handle_rotate_right, continuous=True)
            self.input_component.bind_key(pygame.K_SPACE, self.handle_shoot)
        else:
            # WASD controls
            self.input_component.bind_key(pygame.K_w, self.handle_thrust, continuous=True)
            self.input_component.bind_key(pygame.K_a, self.handle_rotate_left, continuous=True)
            self.input_component.bind_key(pygame.K_d, self.handle_rotate_right, continuous=True)
            self.input_component.bind_key(pygame.K_SPACE, self.handle_shoot)
    
    def handle_thrust(self) -> None:
        """Handle thrust input."""
        transform = self.get_component(TransformComponent)
        physics = self.get_component(PhysicsComponent)
        if not transform or not physics:
            print("Warning: Missing required components for thrust!")  # Debug info
            return
            
        # Calculate thrust direction based on rotation
        angle_rad = math.radians(transform.rotation)
        thrust_dir = pygame.Vector2(
            math.sin(angle_rad),
            -math.cos(angle_rad)
        )
        
        # Apply thrust force
        thrust_force = thrust_dir * SHIP_ACCELERATION
        physics.apply_force(thrust_force)
        
        # Create thrust particles
        self.create_thrust_particles()
        
        # Update thrust effect
        effects = self.get_component(EffectComponent)
        if effects:
            effects.set_effect_active('thrust', True)
    
    def handle_rotate_left(self) -> None:
        """Handle rotate left input."""
        transform = self.get_component(TransformComponent)
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.dt
            transform.rotation = (transform.rotation - rotation_change) % 360
            print(f"Rotating left: change={rotation_change}, new rotation={transform.rotation}")  # Debug info
    
    def handle_rotate_right(self) -> None:
        """Handle rotate right input."""
        transform = self.get_component(TransformComponent)
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.dt
            transform.rotation = (transform.rotation + rotation_change) % 360
            print(f"Rotating right: change={rotation_change}, new rotation={transform.rotation}")  # Debug info
    
    def handle_shoot(self) -> None:
        """Handle shoot input."""
        if len(self.game.bullets) >= MAX_BULLETS:
            return
            
        transform = self.get_component(TransformComponent)
        if not transform:
            print("Warning: Cannot shoot without transform component!")  # Debug info
            return
            
        # Calculate bullet direction based on ship's rotation
        angle_rad = math.radians(transform.rotation)
        direction = pygame.Vector2(
            math.sin(angle_rad),
            -math.cos(angle_rad)
        )
        
        # Create bullet at ship's position
        bullet = Bullet(
            self.game,
            pygame.Vector2(transform.position),
            direction
        )
        
        # Add to tracking lists
        self.game.bullets.append(bullet)
        self.game.entities.append(bullet)
        
        # Play shoot sound
        self.game.audio.play_shoot()
        
        # Reset shoot timer
        self.shoot_timer = self.SHOOT_COOLDOWN
        print("Bullet fired")  # Debug info
    
    def create_thrust_particles(self) -> None:
        """Create particles for thrust effect."""
        transform = self.get_component(TransformComponent)
        if not transform:
            return
            
        # Calculate thrust direction based on ship rotation
        angle_rad = math.radians(transform.rotation)
        thrust_dir = pygame.Vector2(
            math.sin(angle_rad),
            -math.cos(angle_rad)
        )
        
        # Create 2-3 particles per thrust
        num_particles = random.randint(2, 3)
        for _ in range(num_particles):
            # Create particle with proper initial position and color
            particle = Particle(
                self.game,
                lifetime=random.uniform(0.2, 0.4),
                color=(255, 165, 0)  # Orange color
            )
            
            # Calculate particle spawn position behind ship
            pos = transform.position - thrust_dir * 20  # Offset behind ship
            
            # Set particle position and velocity
            particle_transform = particle.get_component(TransformComponent)
            if particle_transform:
                particle_transform.position = pos
                
                # Randomize particle velocity around thrust direction
                spread = 30  # Degrees
                particle_angle = transform.rotation + random.uniform(-spread, spread)
                particle_speed = random.uniform(50, 150)
                
                particle_angle_rad = math.radians(particle_angle)
                particle_vel = pygame.Vector2(
                    math.sin(particle_angle_rad),
                    -math.cos(particle_angle_rad)
                ) * particle_speed
                
                particle_transform.velocity = -particle_vel  # Opposite of thrust direction
            
            # Add to game entities
            self.game.entities.append(particle)
            
            if DEBUG:
                print(f"Created thrust particle at {pos} with velocity {particle_vel}")  # Debug info
    
    def update(self, dt: float) -> None:
        """Update the ship's state."""
        super().update(dt)
        
        # Update shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        
        # Update invulnerability
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
            
            # Flash the ship while invulnerable
            render = self.get_component(RenderComponent)
            if render:
                render.visible = int(self.invulnerable_timer * 10) % 2 == 0  # Flash 5 times per second
        else:
            # Ensure ship is visible when not invulnerable
            render = self.get_component(RenderComponent)
            if render:
                render.visible = True
        
        # Deactivate thrust effect if not thrusting
        effects = self.get_component(EffectComponent)
        input_comp = self.input_component
        if effects and input_comp:
            controls = self.game.settings.get('controls', 'arrows')
            thrust_key = pygame.K_UP if controls == 'arrows' else pygame.K_w
            effects.set_effect_active('thrust', thrust_key in input_comp.pressed_keys)
    
    def _init_thrust_effect(self, effects: EffectComponent) -> None:
        """Initialize the thrust visual effect."""
        # Store effect parameters as instance variables
        self.thrust_vertices = [(0, 10), (-5, 20), (5, 20)]  # Small triangle behind ship
        self.thrust_color = (255, 165, 0)  # Orange color
        self.thrust_offset = pygame.Vector2(0, 15)  # Offset behind ship
        
        # Add thrust effect with proper callbacks
        effects.add_effect(
            name='thrust',
            duration=float('inf'),  # Permanent effect until removed
            on_start=None,  # No start callback needed
            on_update=None,  # Update handled in ship's update method
            on_end=None  # No end callback needed
        )
        print("Thrust effect initialized")  # Debug info
        
    @property
    def invulnerable(self) -> bool:
        """Check if ship is currently invulnerable."""
        return self.invulnerable_timer > 0 