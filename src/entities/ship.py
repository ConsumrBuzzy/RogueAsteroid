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

if TYPE_CHECKING:
    from src.core.game import Game

class Ship(Entity):
    """Player controlled ship entity."""
    
    SHOOT_COOLDOWN = 0.25  # seconds between shots
    
    def __init__(self, game: 'Game'):
        super().__init__(game)
        print("Initializing ship...")  # Debug info
        self.shoot_timer = 0.0
        self.invulnerable_timer = SHIP_INVULNERABLE_TIME
        
        # Add components
        self._init_transform()
        self._init_physics()
        self._init_render()
        self._init_input()
        self._init_effects()
        self._init_collision()
        self._init_screen_wrap()
        
        # Verify components
        transform = self.get_component('transform')
        render = self.get_component('render')
        print(f"Transform component: {transform}")  # Debug info
        print(f"Render component: {render}")  # Debug info
        if transform and render:
            print("Ship components initialized successfully")  # Debug info
        else:
            print("Failed to initialize ship components!")  # Debug info
    
    def _init_transform(self) -> None:
        """Initialize transform component."""
        transform = self.add_component(TransformComponent, 
            WINDOW_WIDTH / 2,  # Start at center
            WINDOW_HEIGHT / 2
        )
        print(f"Transform component added: {transform}")  # Debug info
    
    def _init_physics(self) -> None:
        """Initialize physics component."""
        physics = self.add_component(PhysicsComponent, mass=1.0, max_speed=SHIP_MAX_SPEED)
        physics.friction = SHIP_FRICTION
    
    def _init_render(self) -> None:
        """Initialize render component."""
        render = self.add_component(RenderComponent)
        print(f"Render component added: {render}")  # Debug info
        
        # Define ship shape (triangle pointing up)
        size = 20.0
        render.vertices = [
            (0, -size),           # nose (top)
            (-size/2, size/2),    # left wing (bottom)
            (size/2, size/2)      # right wing (bottom)
        ]
        render.color = WHITE
        render.visible = True
        print(f"Render vertices: {render.vertices}")  # Debug info
    
    def _init_input(self) -> None:
        """Initialize input component with control bindings."""
        input_component = self.add_component(InputComponent)
        
        # Bind controls based on scheme
        if self.game.settings.get('controls', 'scheme') == 'arrows':
            thrust_key = pygame.K_UP
            reverse_key = pygame.K_DOWN
            left_key = pygame.K_LEFT
            right_key = pygame.K_RIGHT
            shoot_key = pygame.K_SPACE
        else:  # wasd
            thrust_key = pygame.K_w
            reverse_key = pygame.K_s
            left_key = pygame.K_a
            right_key = pygame.K_d
            shoot_key = pygame.K_SPACE
        
        # Bind continuous actions
        input_component.bind_key(thrust_key, self._apply_thrust, continuous=True)
        input_component.bind_key(reverse_key, self._apply_reverse_thrust, continuous=True)
        input_component.bind_key(left_key, self._rotate_left, continuous=True)
        input_component.bind_key(right_key, self._rotate_right, continuous=True)
        input_component.bind_key(shoot_key, self._shoot, continuous=False)
    
    def _init_effects(self) -> None:
        """Initialize visual effects component."""
        effects = self.add_component(EffectComponent)
        
        # Add thrust flame effect
        flame_size = 10.0
        rear_offset = (0, 15)  # Offset from center
        effects.add_effect(
            'thrust',
            vertices=[
                (0, 0),
                (-flame_size/2, flame_size),
                (flame_size/2, flame_size)
            ],
            color=(255, 165, 0),  # Orange
            offset=rear_offset
        )
    
    def _init_collision(self) -> None:
        """Initialize collision component."""
        self.add_component(CollisionComponent, radius=12.0)
    
    def _init_screen_wrap(self) -> None:
        """Initialize screen wrapping component."""
        self.add_component(ScreenWrapComponent, WINDOW_WIDTH, WINDOW_HEIGHT)
    
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
            
            # Activate thrust effect only for forward thrust
            if effects and power > 0:
                effects.set_effect_active('thrust', True)
    
    def _rotate_left(self) -> None:
        """Rotate ship counter-clockwise."""
        transform = self.get_component('transform')
        if transform:
            transform.rotation -= SHIP_ROTATION_SPEED * self.game.dt * 60
    
    def _rotate_right(self) -> None:
        """Rotate ship clockwise."""
        transform = self.get_component('transform')
        if transform:
            transform.rotation += SHIP_ROTATION_SPEED * self.game.dt * 60
    
    def _shoot(self) -> None:
        """Fire a bullet in the current direction."""
        if self.shoot_timer > 0:
            return
            
        # Check bullet limit
        if len(self.game.bullets) >= MAX_BULLETS:
            return
            
        transform = self.get_component('transform')
        if not transform:
            return
            
        # Calculate bullet direction based on ship's rotation
        angle_rad = np.radians(transform.rotation - 90)  # -90 to match ship's upward orientation
        direction = np.array([
            np.cos(angle_rad),
            np.sin(angle_rad)
        ])
        
        # Create bullet at ship's nose
        nose_offset = direction * 20.0  # Offset from center to avoid self-collision
        bullet = Bullet(
            self.game,
            transform.position[0] + nose_offset[0],
            transform.position[1] + nose_offset[1],
            direction
        )
        
        # Add bullet to game
        self.game.entities.append(bullet)
        self.game.bullets.append(bullet)  # Track bullet
        
        # Reset shoot timer
        self.shoot_timer = self.SHOOT_COOLDOWN
    
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
                render.visible = int(self.invulnerable_timer * 10) % 2 == 0
        else:
            # Ensure ship is visible when not invulnerable
            render = self.get_component('render')
            if render:
                render.visible = True
        
        # Deactivate thrust effect if not thrusting
        effects = self.get_component('effects')
        input_component = self.get_component('input')
        
        if effects and input_component:
            thrust_key = pygame.K_UP if self.game.settings.get('controls', 'scheme') == 'arrows' else pygame.K_w
            effects.set_effect_active('thrust', thrust_key in input_component.active_keys) 