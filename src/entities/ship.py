"""Ship entity for the game."""
import math
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
    MAX_BULLETS,
    THRUST_COLORS,
    THRUST_PARTICLE_COUNT,
    THRUST_PARTICLE_LIFETIME,
    THRUST_PARTICLE_SPEED,
    THRUST_PARTICLE_SPREAD,
    THRUST_PARTICLE_SIZE,
    THRUST_OFFSET
)
from src.entities.bullet import Bullet
from src.core.logging import get_logger

if TYPE_CHECKING:
    from src.core.game import Game

class Ship(Entity):
    """Player controlled ship entity."""
    
    SHOOT_COOLDOWN = 0.20  # Reduced from 0.25 to 0.20 seconds between shots
    
    def __init__(self, game: 'Game'):
        super().__init__(game)
        self.logger = get_logger()
        self.shoot_timer = 0.0
        self.invulnerable_timer = 0.0
        self._invulnerable = False
        self.input_component = None
        
        # Add components
        self._init_components()
    
    def _init_components(self) -> None:
        """Initialize ship components."""
        # Transform component for position and movement
        transform = self.add_component(TransformComponent)
        transform.position = pygame.Vector2(self.game.width / 2, self.game.height / 2)
        transform.rotation = 0.0
        
        # Render component for drawing
        render = self.add_component(RenderComponent)
        render.vertices = [(0, -20), (-10, 10), (10, 10)]  # Triangle shape
        render.color = WHITE
        
        # Physics component for thrust and momentum
        physics = self.add_component(PhysicsComponent)
        physics.max_speed = SHIP_MAX_SPEED
        physics.friction = SHIP_FRICTION
        
        # Collision component for hit detection
        collision = self.add_component(CollisionComponent, radius=15)
        
        # Screen wrap component to wrap around screen edges
        screen_wrap = self.add_component(ScreenWrapComponent)
        
        # Effects component for invulnerability flash
        effects = self.add_component(EffectComponent)
        
        # Input component for controls
        self.input_component = self.add_component(InputComponent)
        self.update_controls()  # Initialize controls
    
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
    
    def handle_rotate_left(self) -> None:
        """Handle rotate left input."""
        transform = self.get_component(TransformComponent)
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.game_loop.dt
            transform.rotation = (transform.rotation - rotation_change) % 360
            print(f"Rotating left: change={rotation_change}, new rotation={transform.rotation}")  # Debug info
    
    def handle_rotate_right(self) -> None:
        """Handle rotate right input."""
        transform = self.get_component(TransformComponent)
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.game_loop.dt
            transform.rotation = (transform.rotation + rotation_change) % 360
            print(f"Rotating right: change={rotation_change}, new rotation={transform.rotation}")  # Debug info
    
    def handle_shoot(self) -> None:
        """Handle shoot input."""
        if len(self.game.entity_manager.bullets) >= MAX_BULLETS:
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
        
        # Add bullet to game
        self.game.entity_manager.add_entity(bullet)
        
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
        
        # Calculate particle spawn position behind ship
        pos = transform.position - thrust_dir * THRUST_OFFSET
        
        # Use particle system to create thrust effect
        self.game.particle_system.emit_circular(
            position=pos,
            color=random.choice(THRUST_COLORS),
            count=random.randint(*THRUST_PARTICLE_COUNT),
            lifetime=(THRUST_PARTICLE_LIFETIME[0], THRUST_PARTICLE_LIFETIME[1]),
            speed_range=(THRUST_PARTICLE_SPEED[0], THRUST_PARTICLE_SPEED[1]),
            size_range=(THRUST_PARTICLE_SIZE[0], THRUST_PARTICLE_SIZE[1])
        )
    
    def update(self, dt: float) -> None:
        """Update the ship's state."""
        super().update(dt)
        
        # Update shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        
        # Update invulnerability
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
            # Flash effect while invulnerable
            effects = self.get_component(EffectComponent)
            if effects:
                flash_rate = 8  # Times per second
                flash_alpha = 128 + (127 * math.sin(self.invulnerable_timer * flash_rate))
                effects.set_alpha(int(flash_alpha))
        elif self._invulnerable:
            # Reset to normal when invulnerability ends
            self._invulnerable = False
            effects = self.get_component(EffectComponent)
            if effects:
                effects.set_alpha(255)
        
        # Check if thrust key is pressed and update effect
        effects = self.get_component(EffectComponent)
        if effects and self.input_component:
            controls = self.game.settings.get('controls', 'arrows')
            thrust_key = pygame.K_UP if controls == 'arrows' else pygame.K_w
            effects.set_effect_active('thrust', thrust_key in self.input_component.pressed_keys)
    
    @property
    def invulnerable(self) -> bool:
        """Get invulnerability status."""
        return self._invulnerable or self.invulnerable_timer > 0
    
    @invulnerable.setter
    def invulnerable(self, value: bool) -> None:
        """Set invulnerability status."""
        self._invulnerable = value
        # Update visual effect
        effects = self.get_component(EffectComponent)
        if effects:
            if value:
                effects.set_alpha(128)  # Semi-transparent when invulnerable
            else:
                effects.set_alpha(255)  # Fully opaque when vulnerable
    
    def update(self, dt: float) -> None:
        """Update the ship's state."""
        super().update(dt)
        
        # Update shoot timer
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
        
        # Update invulnerability
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
            # Flash effect while invulnerable
            effects = self.get_component(EffectComponent)
            if effects:
                flash_rate = 8  # Times per second
                flash_alpha = 128 + (127 * math.sin(self.invulnerable_timer * flash_rate))
                effects.set_alpha(int(flash_alpha))
        elif self._invulnerable:
            # Reset to normal when invulnerability ends
            self._invulnerable = False
            effects = self.get_component(EffectComponent)
            if effects:
                effects.set_alpha(255) 
    
    def fire_bullet(self):
        """Fire a bullet in the direction the ship is facing."""
        if len(self.game.entity_manager.bullets) >= MAX_BULLETS:
            return
            
        transform = self.get_component(TransformComponent)
        if transform:
            # Calculate bullet direction based on ship's rotation
            angle_rad = math.radians(transform.rotation)
            direction = pygame.Vector2(
                math.sin(angle_rad),
                -math.cos(angle_rad)
            )
            
            # Create bullet at ship's position with calculated direction
            bullet = Bullet(self.game, pygame.Vector2(transform.position), direction)
            self.game.entity_manager.add_entity(bullet)
            print("Bullet fired") 