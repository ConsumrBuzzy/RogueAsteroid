"""Player ship entity using component system."""
import pygame
import numpy as np
from typing import TYPE_CHECKING
from src.core.entities.base import Entity, TransformComponent, RenderComponent, CollisionComponent
from src.core.entities.components import (
    ScreenWrapComponent,
    InputComponent,
    PhysicsComponent,
    EffectComponent
)
from src.core.constants import (
    SHIP_ACCELERATION,
    SHIP_MAX_SPEED,
    SHIP_ROTATION_SPEED,
    SHIP_FRICTION,
    WINDOW_WIDTH,
    WINDOW_HEIGHT,
    WHITE,
    MAX_BULLETS,
    SHIP_INVULNERABLE_TIME
)
from src.entities.bullet import Bullet
from src.entities.particle import Particle
import random

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
        
        # Add components
        self._init_components()
        
        # Verify components
        transform = self.get_component('transform')
        render = self.get_component('render')
        print(f"Transform component: {transform}")  # Debug info
        print(f"Render component: {render}")  # Debug info
        if transform and render:
            print("Ship components initialized successfully")  # Debug info
        else:
            print("Failed to initialize ship components!")  # Debug info
    
    def _init_components(self) -> None:
        """Initialize ship components."""
        print("Initializing ship...")
        
        # Transform component for position and movement
        transform = self.add_component(TransformComponent)
        transform.position = pygame.Vector2(self.game.width / 2, self.game.height / 2)
        print(f"Transform component added: {transform}")  # Debug info
        
        # Render component for drawing
        render = self.add_component(RenderComponent)
        render.vertices = [(0, -20.0), (-10.0, 10.0), (10.0, 10.0)]  # Triangle shape
        render.color = (255, 255, 255)  # White
        print(f"Render component added: {render}")  # Debug info
        print(f"Render vertices: {render.vertices}")  # Debug info
        
        # Physics component for thrust and momentum
        physics = self.add_component(PhysicsComponent)
        physics.max_speed = SHIP_MAX_SPEED
        physics.friction = SHIP_FRICTION
        
        # Collision component for hit detection
        collision = self.add_component(CollisionComponent, radius=15)  # Pass radius in constructor
        print(f"Collision component added: {collision}")  # Debug info
        
        # Screen wrap component to wrap around screen edges
        screen_wrap = self.add_component(ScreenWrapComponent)
        
        # Effects component for visual effects
        effects = self.add_component(EffectComponent)
        self._init_thrust_effect(effects)  # Initialize thrust effect
        
        # Input component for controls
        self.input_component = self.add_component(InputComponent)
        self.update_controls()  # Initialize controls
    
    def update_controls(self) -> None:
        """Update control bindings based on current control scheme."""
        if not self.input_component:
            return
            
        # Clear existing bindings
        self.input_component.clear_bindings()
        
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
        transform = self.get_component('transform')
        physics = self.get_component('physics')
        if not transform or not physics:
            return
            
        # Calculate thrust direction based on rotation
        angle = transform.rotation
        thrust_dir = np.array([
            np.sin(np.radians(angle)),
            -np.cos(np.radians(angle))
        ])
        
        # Apply thrust force
        thrust_force = thrust_dir * SHIP_ACCELERATION
        physics.apply_force(thrust_force)
        
        # Create thrust particles
        self.create_thrust_particles()
        
        # Update thrust effect
        effects = self.get_component('effect')
        if effects:
            effects.set_effect_active('thrust', True)
    
    def handle_rotate_left(self) -> None:
        """Handle rotate left input."""
        transform = self.get_component('transform')
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.dt
            transform.rotation = (transform.rotation - rotation_change) % 360
            print(f"Rotating left: change={rotation_change}, new rotation={transform.rotation}")  # Debug info
    
    def handle_rotate_right(self) -> None:
        """Handle rotate right input."""
        transform = self.get_component('transform')
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.dt
            transform.rotation = (transform.rotation + rotation_change) % 360
            print(f"Rotating right: change={rotation_change}, new rotation={transform.rotation}")  # Debug info
    
    def handle_shoot(self):
        """Handle shoot input."""
        if len(self.game.bullets) >= MAX_BULLETS or self.shoot_timer > 0:
            return
            
        transform = self.get_component('transform')
        if not transform:
            return
            
        # Calculate bullet direction based on ship's rotation
        # Adjust angle by -90 degrees because ship points up at 0 degrees
        angle_rad = np.radians(transform.rotation - 90)
        direction = pygame.Vector2(
            np.cos(angle_rad),
            np.sin(angle_rad)
        )
        
        # Create bullet at ship's position with calculated direction
        bullet = Bullet(
            self.game,
            pygame.Vector2(transform.position),  # Convert position to Vector2
            direction
        )
        
        # Add to tracking lists
        self.game.bullets.append(bullet)
        self.game.entities.append(bullet)
        
        # Reset shoot timer
        self.shoot_timer = self.SHOOT_COOLDOWN
        
        print("Bullet fired")  # Debug info
    
    def create_thrust_particles(self) -> None:
        """Create particles for thrust effect."""
        transform = self.get_component('transform')
        if not transform:
            return
            
        # Calculate thrust direction based on ship rotation
        angle = transform.rotation
        thrust_dir = np.array([
            np.sin(np.radians(angle)),
            -np.cos(np.radians(angle))
        ])
        print(f"Rotation: {angle}, Thrust direction: {thrust_dir}, Power: {1.0}")  # Debug info
        
        # Create 2-3 particles per thrust
        num_particles = random.randint(2, 3)
        for _ in range(num_particles):
            # Randomize particle velocity around thrust direction
            spread = 30  # Degrees
            particle_angle = angle + random.uniform(-spread, spread)
            particle_speed = random.uniform(50, 150)
            particle_vel = np.array([
                np.sin(np.radians(particle_angle)),
                -np.cos(np.radians(particle_angle))
            ]) * particle_speed
            
            # Create particle at ship's position
            pos = transform.position + thrust_dir * 20  # Offset behind ship
            particle = {
                'position': np.array([pos[0], pos[1]]),
                'velocity': -particle_vel,  # Opposite of thrust direction
                'lifetime': random.uniform(0.2, 0.4),  # Short lifetime
                'color': (255, 165, 0)  # Orange color
            }
            self.game.particles.append(particle)
    
    def update(self, dt: float) -> None:
        """Update ship state."""
        super().update(dt)
        
        # Update shoot cooldown
        self.shoot_timer = max(0.0, self.shoot_timer - dt)
        
        # Update invulnerability
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
            
            # Flash the ship while invulnerable
            render = self.get_component('render')
            if render:
                render.visible = int(self.invulnerable_timer * 10) % 2 == 0  # Flash 5 times per second
        else:
            # Ensure ship is visible when not invulnerable
            render = self.get_component('render')
            if render:
                render.visible = True
        
        # Create thrust particles if thrusting
        input_component = self.get_component('input')
        if input_component:
            controls = self.game.settings.get('controls', 'arrows')
            thrust_key = pygame.K_UP if controls == 'arrows' else pygame.K_w
            if thrust_key in input_component.active_keys:
                self._create_thrust_particles()
        
        # Deactivate thrust effect if not thrusting
        effects = self.get_component('effects')
        if effects and input_component:
            controls = self.game.settings.get('controls', 'arrows')
            thrust_key = pygame.K_UP if controls == 'arrows' else pygame.K_w
            effects.set_effect_active('thrust', thrust_key in input_component.active_keys)
    
    def _init_thrust_effect(self, effects: 'EffectComponent') -> None:
        """Initialize the thrust visual effect."""
        print("Thrust effect initialized")  # Debug info
        
        # Add thrust effect
        effects.add_effect(
            'thrust',
            [(0, 10), (-5, 20), (5, 20)],  # Small triangle behind ship
            (255, 165, 0),  # Orange color
            (0, 15)  # Offset behind ship
        )
        
    @property
    def invulnerable(self):
        """Check if ship is currently invulnerable."""
        return self.invulnerable_timer > 0 