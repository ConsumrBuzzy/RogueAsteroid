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
            
            # Activate thrust effect and sound only for forward thrust
            if effects and power > 0:
                effects.set_effect_active('thrust', True)
                self.game.sound.play_sound('thrust')
    
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
    
    def _shoot(self):
        """Create and fire a bullet."""
        if len(self.game.bullets) >= MAX_BULLETS:
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
        bullet = Bullet(self.game, transform.position, transform.rotation, direction)
        
        # Add to tracking lists
        self.game.bullets.append(bullet)
        self.game.entities.append(bullet)
        
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
                render.visible = int(self.invulnerable_timer * 10) % 2 == 0
        else:
            # Ensure ship is visible when not invulnerable
            render = self.get_component('render')
            if render:
                render.visible = True
        
        # Create thrust particles if thrusting
        input_component = self.get_component('input')
        if input_component:
            thrust_key = pygame.K_UP if self.game.settings.get('controls', 'scheme') == 'arrows' else pygame.K_w
            if thrust_key in input_component.active_keys:
                self._create_thrust_particles()
        
        # Deactivate thrust effect if not thrusting
        effects = self.get_component('effects')
        if effects and input_component:
            thrust_key = pygame.K_UP if self.game.settings.get('controls', 'scheme') == 'arrows' else pygame.K_w
            effects.set_effect_active('thrust', thrust_key in input_component.active_keys) 