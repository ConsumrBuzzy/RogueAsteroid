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
    
    SHOOT_COOLDOWN = 0.25  # seconds between shots
    
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
        
        # Set up keys based on control scheme
        if controls == 'arrows':
            # Regular arrow keys and numpad
            thrust_keys = [pygame.K_UP, pygame.K_KP8]
            reverse_keys = [pygame.K_DOWN, pygame.K_KP2]
            left_keys = [pygame.K_LEFT, pygame.K_KP4]
            right_keys = [pygame.K_RIGHT, pygame.K_KP6]
        else:  # wasd
            thrust_keys = [pygame.K_w]
            reverse_keys = [pygame.K_s]
            left_keys = [pygame.K_a]
            right_keys = [pygame.K_d]
        
        # Bind controls - each key in the key groups
        for thrust_key in thrust_keys:
            self.input_component.bind_key(thrust_key, self._apply_thrust, True)
        for reverse_key in reverse_keys:
            self.input_component.bind_key(reverse_key, self._apply_reverse_thrust, True)
        for left_key in left_keys:
            self.input_component.bind_key(left_key, self._rotate_left, True)
        for right_key in right_keys:
            self.input_component.bind_key(right_key, self._rotate_right, True)
            
        # Bind shoot to both regular space and numpad enter
        self.input_component.bind_key(pygame.K_SPACE, self._shoot)
        self.input_component.bind_key(pygame.K_KP_ENTER, self._shoot)
        
        print(f"Controls updated to scheme: {controls}")  # Debug info
    
    def _apply_thrust(self) -> None:
        """Apply forward thrust force."""
        self._apply_thrust_force(1.0)
    
    def _apply_reverse_thrust(self) -> None:
        """Apply reverse thrust force."""
        self._apply_thrust_force(-0.5)  # Half power for reverse
    
    def _apply_thrust_force(self, power: float) -> None:
        """Apply thrust force in current direction with given power."""
        transform = self.get_component('transform')
        physics = self.get_component('physics')
        effects = self.get_component('effects')
        
        if transform and physics:
            # Calculate thrust direction
            # Adjust angle by -90 degrees because ship points up at 0 degrees
            angle_rad = np.radians(transform.rotation - 90)
            direction = np.array([
                np.cos(angle_rad),
                np.sin(angle_rad)
            ])
            
            # Debug thrust direction
            print(f"Rotation: {transform.rotation}, Thrust direction: {direction}, Power: {power}")  # Debug info
            
            # Apply force
            force = direction * SHIP_ACCELERATION * power
            physics.apply_force(force)
            
            # Activate thrust effect
            if effects and power > 0:
                effects.set_effect_active('thrust', True)
    
    def _rotate_left(self) -> None:
        """Rotate ship counter-clockwise."""
        transform = self.get_component('transform')
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.dt
            transform.rotation = (transform.rotation - rotation_change) % 360
            print(f"Rotating left: change={rotation_change}, new rotation={transform.rotation}")  # Debug info
    
    def _rotate_right(self) -> None:
        """Rotate ship clockwise."""
        transform = self.get_component('transform')
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.dt
            transform.rotation = (transform.rotation + rotation_change) % 360
            print(f"Rotating right: change={rotation_change}, new rotation={transform.rotation}")  # Debug info
    
    def _shoot(self):
        """Create and fire a bullet."""
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
    
    def _create_thrust_particles(self):
        """Create particles for engine thrust effect"""
        transform = self.get_component('transform')
        if not transform:
            return
        
        # Calculate thrust direction (opposite of ship's facing direction)
        angle_rad = np.radians(transform.rotation - 90)  # -90 to match ship's upward orientation
        direction = pygame.Vector2(
            np.cos(angle_rad),
            np.sin(angle_rad)
        )
        
        # Position particles at ship's rear (opposite of direction)
        rear_pos = pygame.Vector2(transform.position) - direction * 15  # 15 pixels behind ship
        
        # Create 2-3 particles per frame when thrusting
        num_particles = random.randint(2, 3)
        for _ in range(num_particles):
            particle = Particle(
                self.game,
                lifetime=random.uniform(0.2, 0.4),
                color=(random.randint(180, 220), random.randint(180, 220), 255)  # Blue-white color
            )
            
            # Position slightly randomized around rear
            offset = pygame.Vector2(random.uniform(-3, 3), random.uniform(-3, 3))
            particle_transform = particle.get_component('transform')
            if particle_transform:
                particle_transform.position = rear_pos + offset
            
            # Velocity opposite of ship direction with spread
            angle = random.uniform(-20, 20)  # 20 degree spread
            velocity = direction.rotate(180 + angle) * random.uniform(100, 150)
            physics = particle.get_component('physics')
            if physics:
                physics.velocity = velocity
            
            # Add to game entities
            self.game.entities.append(particle)
    
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
    
    def _init_thrust_effect(self, effects):
        """Initialize the thrust visual effect."""
        # Create triangular flame shape
        thrust_vertices = [
            (0, 15),      # Tip of flame (at back of ship)
            (-5, 25),     # Left point
            (0, 20),      # Middle indent
            (5, 25),      # Right point
        ]
        effects.add_effect('thrust', thrust_vertices, (255, 165, 0))  # Orange flame
        print("Thrust effect initialized")  # Debug info 

    @property
    def invulnerable(self):
        """Check if ship is currently invulnerable."""
        return self.invulnerable_timer > 0 