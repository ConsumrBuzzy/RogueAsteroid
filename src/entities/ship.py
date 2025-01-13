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
    SHIP_INVULNERABLE_TIME,
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
        self.blink_timer = 0.0  # Add timer for blinking
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
        collision = self.add_component(CollisionComponent, radius=12)
        
        # Screen wrap component to wrap around screen edges
        screen_wrap = self.add_component(ScreenWrapComponent)
        
        # Input component for controls - initialize with current control scheme
        current_scheme = self.game.settings.get('controls', 'arrows')
        self.input_component = self.add_component(InputComponent, control_scheme=current_scheme)
        self.logger.debug(f"Initialized ship with control scheme: {current_scheme}")
    
    def update_controls(self) -> None:
        """Update control bindings based on current control scheme."""
        if not self.input_component:
            self.logger.warning("No input component found!")
            return
            
        # Get current control scheme and update the input component
        current_scheme = self.game.settings.get('controls', 'arrows')
        self.input_component.update_control_scheme(current_scheme)
        self.logger.debug(f"Updated ship controls to scheme: {current_scheme}")
    
    def handle_thrust(self) -> None:
        """Handle thrust input."""
        transform = self.get_component(TransformComponent)
        physics = self.get_component(PhysicsComponent)
        if not transform or not physics:
            self.logger.warning("Missing required components for thrust!")
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
            self.logger.debug(f"Rotating left: change={rotation_change:.2f}, new rotation={transform.rotation:.2f}")
    
    def handle_rotate_right(self) -> None:
        """Handle rotate right input."""
        transform = self.get_component(TransformComponent)
        if transform:
            # Apply rotation speed based on delta time
            rotation_change = SHIP_ROTATION_SPEED * self.game.game_loop.dt
            transform.rotation = (transform.rotation + rotation_change) % 360
            self.logger.debug(f"Rotating right: change={rotation_change:.2f}, new rotation={transform.rotation:.2f}")
    
    def handle_shoot(self) -> None:
        """Handle shoot input."""
        if self.shoot_timer > 0:
            return
            
        if len(self.game.entity_manager.bullets) >= MAX_BULLETS:
            self.logger.debug(f"Cannot fire: max bullets ({MAX_BULLETS}) reached")
            return
            
        transform = self.get_component(TransformComponent)
        if not transform:
            self.logger.warning("Cannot shoot without transform component!")
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
        self.logger.debug("Bullet fired")
    
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
        """Update ship state."""
        super().update(dt)
        
        # Update shoot cooldown
        if self.shoot_timer > 0:
            self.shoot_timer -= dt
            
        # Update invulnerability and blinking
        if self.invulnerable_timer > 0:
            self.invulnerable_timer = max(0.0, self.invulnerable_timer - dt)
            
            # Update blink timer and effect
            self.blink_timer += dt
            render = self.get_component(RenderComponent)
            if render:
                # Blink 5 times per second
                blink_period = 0.2
                should_show = (self.blink_timer % blink_period) < (blink_period / 2)
                render.visible = should_show
        else:
            # Reset to normal when not invulnerable
            self._invulnerable = False
            render = self.get_component(RenderComponent)
            if render:
                render.visible = True  # Make sure ship is visible
            self.blink_timer = 0.0  # Reset blink timer
    
    @property
    def invulnerable(self) -> bool:
        """Get invulnerability status."""
        return self.invulnerable_timer > 0
    
    @invulnerable.setter
    def invulnerable(self, value: bool) -> None:
        """Set invulnerability status."""
        if value:
            self.invulnerable_timer = SHIP_INVULNERABLE_TIME
            self.blink_timer = 0.0  # Reset blink timer
            # Start with ship invisible
            render = self.get_component(RenderComponent)
            if render:
                render.visible = False
        else:
            self.invulnerable_timer = 0.0
            self.blink_timer = 0.0
            render = self.get_component(RenderComponent)
            if render:
                render.visible = True 