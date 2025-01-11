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
    WHITE
)

if TYPE_CHECKING:
    from src.core.game import Game

class Ship(Entity):
    """Player controlled ship entity."""
    
    def __init__(self, game: 'Game'):
        super().__init__(game)
        
        # Add components
        self._init_transform()
        self._init_physics()
        self._init_render()
        self._init_input()
        self._init_effects()
        self._init_collision()
        self._init_screen_wrap()
    
    def _init_transform(self) -> None:
        """Initialize transform component."""
        self.add_component(
            TransformComponent,
            WINDOW_WIDTH / 2,  # Start at center
            WINDOW_HEIGHT / 2
        )
    
    def _init_physics(self) -> None:
        """Initialize physics component."""
        physics = self.add_component(PhysicsComponent, mass=1.0, max_speed=SHIP_MAX_SPEED)
        physics.friction = SHIP_FRICTION
    
    def _init_render(self) -> None:
        """Initialize render component."""
        render = self.add_component(RenderComponent)
        render.color = WHITE
        
        # Define ship shape (triangle)
        size = 20.0
        render.vertices = [
            (0, -size),           # nose
            (-size/2, size/2),    # left wing
            (size/2, size/2)      # right wing
        ]
    
    def _init_input(self) -> None:
        """Initialize input component with control bindings."""
        input_component = self.add_component(InputComponent)
        
        # Bind controls based on scheme
        if self.game.settings.get('controls', 'scheme') == 'arrows':
            thrust_key = pygame.K_UP
            left_key = pygame.K_LEFT
            right_key = pygame.K_RIGHT
        else:  # wasd
            thrust_key = pygame.K_w
            left_key = pygame.K_a
            right_key = pygame.K_d
        
        # Bind continuous actions
        input_component.bind_key(thrust_key, self._apply_thrust, continuous=True)
        input_component.bind_key(left_key, self._rotate_left, continuous=True)
        input_component.bind_key(right_key, self._rotate_right, continuous=True)
    
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
        """Apply thrust force in current direction."""
        transform = self.get_component('transform')
        physics = self.get_component('physics')
        effects = self.get_component('effects')
        
        if transform and physics:
            # Calculate thrust direction
            angle_rad = np.radians(transform.rotation)
            direction = np.array([
                np.cos(angle_rad),
                np.sin(angle_rad)
            ])
            
            # Apply force
            force = direction * SHIP_ACCELERATION
            physics.apply_force(force)
            
            # Activate thrust effect
            if effects:
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
    
    def update(self, dt: float) -> None:
        """Update ship state."""
        super().update(dt)
        
        # Deactivate thrust effect if not thrusting
        effects = self.get_component('effects')
        input_component = self.get_component('input')
        
        if effects and input_component:
            thrust_key = pygame.K_UP if self.game.settings.get('controls', 'scheme') == 'arrows' else pygame.K_w
            effects.set_effect_active('thrust', thrust_key in input_component.active_keys) 