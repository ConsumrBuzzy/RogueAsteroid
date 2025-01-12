"""Ship entity class."""
from typing import Optional
import pygame
from pygame import Vector2

from src.core.entity.entity import Entity
from src.core.components.transform import TransformComponent
from src.core.components.render import RenderComponent
from src.core.components.physics import PhysicsComponent
from src.core.components.collision import CollisionComponent
from src.core.components.input import InputComponent
from src.core.components.effect import EffectComponent
from src.core.components.screen_wrap import ScreenWrapComponent
from src.core.constants import SHIP_MAX_SPEED, SHIP_FRICTION, INVULNERABILITY_TIME

class Ship(Entity):
    """Player-controlled ship entity.
    
    Provides:
    - Movement controls
    - Shooting mechanics
    - Collision detection
    - Visual effects
    - Screen wrapping
    """
    
    def __init__(self, game):
        """Initialize the ship.
        
        Args:
            game: The game instance this ship belongs to
        """
        super().__init__(game)
        self._invulnerable_timer = 0
        self._thrust_timer = 0
        self._init_components()
        
    def _init_components(self) -> None:
        """Initialize ship components."""
        print("Initializing ship...")
        
        # Transform component for position and movement
        transform = TransformComponent(self)
        self.add_component(transform)
        transform.position = Vector2(self.game.width / 2, self.game.height / 2)
        print(f"Transform component added: {transform}")  # Debug info
        
        # Render component for drawing
        render = RenderComponent(self)
        self.add_component(render)
        render.vertices = [(0, -20.0), (-10.0, 10.0), (10.0, 10.0)]  # Triangle shape
        render.color = (255, 255, 255)  # White
        print(f"Render component added: {render}")  # Debug info
        print(f"Render vertices: {render.vertices}")  # Debug info
        
        # Physics component for thrust and momentum
        physics = PhysicsComponent(self)
        self.add_component(physics)
        physics.max_speed = SHIP_MAX_SPEED
        physics.friction = SHIP_FRICTION
        
        # Collision component for hit detection
        collision = CollisionComponent(self, radius=15)
        self.add_component(collision)
        print(f"Collision component added: {collision}")  # Debug info
        
        # Screen wrap component to wrap around screen edges
        screen_wrap = ScreenWrapComponent(self, screen_size=(self.game.width, self.game.height))
        self.add_component(screen_wrap)
        
        # Effects component for visual effects
        effects = EffectComponent(self)
        self.add_component(effects)
        self._init_thrust_effect(effects)  # Initialize thrust effect
        
        # Input component for controls
        input_component = InputComponent(self)
        self.add_component(input_component)
        self.update_controls()  # Initialize controls
        
        # Initialize the entity after all components are added
        self.initialize()
        
    def get_transform(self) -> Optional[TransformComponent]:
        """Get the transform component.
        
        Returns:
            TransformComponent if found, None otherwise
        """
        return self.get_component(TransformComponent)
        
    def get_render(self) -> Optional[RenderComponent]:
        """Get the render component.
        
        Returns:
            RenderComponent if found, None otherwise
        """
        return self.get_component(RenderComponent)
        
    def get_physics(self) -> Optional[PhysicsComponent]:
        """Get the physics component.
        
        Returns:
            PhysicsComponent if found, None otherwise
        """
        return self.get_component(PhysicsComponent)
        
    def get_collision(self) -> Optional[CollisionComponent]:
        """Get the collision component.
        
        Returns:
            CollisionComponent if found, None otherwise
        """
        return self.get_component(CollisionComponent)
        
    def get_input(self) -> Optional[InputComponent]:
        """Get the input component.
        
        Returns:
            InputComponent if found, None otherwise
        """
        return self.get_component(InputComponent)
        
    def get_effects(self) -> Optional[EffectComponent]:
        """Get the effects component.
        
        Returns:
            EffectComponent if found, None otherwise
        """
        return self.get_component(EffectComponent)
        
    def update(self, dt: float) -> None:
        """Update the ship.
        
        Args:
            dt: Delta time in seconds
        """
        super().update(dt)
        
        # Update invulnerability
        if self._invulnerable_timer > 0:
            self._invulnerable_timer -= dt
            # Flash visibility while invulnerable
            render = self.get_render()
            if render:
                render.visible = int(self._invulnerable_timer * 10) % 2 == 0
                
        # Update thrust effect
        if self._thrust_timer > 0:
            self._thrust_timer -= dt
            effects = self.get_effects()
            if effects:
                effects.visible = self._thrust_timer > 0
                
    def make_invulnerable(self) -> None:
        """Make the ship temporarily invulnerable."""
        self._invulnerable_timer = INVULNERABILITY_TIME
        
    def _init_thrust_effect(self, effects: EffectComponent) -> None:
        """Initialize the thrust particle effect.
        
        Args:
            effects: The effects component to initialize
        """
        # Set up thrust particles
        effects.add_effect_template('thrust', {
            'count': 10,
            'speed_range': (50, 100),
            'angle_spread': 30,
            'lifetime_range': (0.2, 0.4),
            'size_range': (1, 2),
            'colors': [(255, 200, 50), (255, 100, 0), (200, 50, 0)]
        })
        
    def update_controls(self) -> None:
        """Update the ship's control mappings."""
        input_component = self.get_input()
        if not input_component:
            return
            
        # Clear existing bindings
        input_component.clear_bindings()
        
        # Add new action bindings
        input_component.bind_action("thrust", [pygame.K_w, pygame.K_UP], self._thrust_forward)
        input_component.bind_action("rotate_left", [pygame.K_a, pygame.K_LEFT], self._rotate_left)
        input_component.bind_action("rotate_right", [pygame.K_d, pygame.K_RIGHT], self._rotate_right)
        input_component.bind_action("fire", [pygame.K_SPACE], self._fire)
        
    def _thrust_forward(self) -> None:
        """Apply forward thrust to the ship."""
        transform = self.get_transform()
        physics = self.get_physics()
        if not transform or not physics:
            return
            
        # Get direction from rotation
        direction = transform.get_direction()
        
        # Apply thrust force
        physics.apply_force(direction * 500)
        
        # Update thrust effect
        self._thrust_timer = 0.1
        effects = self.get_effects()
        if effects:
            effects.emit('thrust', transform.position, -direction)
            
    def _rotate_left(self) -> None:
        """Rotate the ship counter-clockwise."""
        transform = self.get_transform()
        if transform:
            transform.rotate(-5)
            
    def _rotate_right(self) -> None:
        """Rotate the ship clockwise."""
        transform = self.get_transform()
        if transform:
            transform.rotate(5)
            
    def _fire(self) -> None:
        """Fire the ship's weapon."""
        transform = self.get_transform()
        if not transform:
            return
            
        # Get bullet spawn position (front of ship)
        direction = transform.get_direction()
        position = transform.position + direction * 20
        
        # Create bullet
        self.game.create_bullet(position, direction)
        
    @property
    def invulnerable(self) -> bool:
        """Check if ship is currently invulnerable.
        
        Returns:
            True if ship is invulnerable
        """
        return self._invulnerable_timer > 0 