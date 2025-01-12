"""Ship entity module."""
import math
from typing import Dict, List, Tuple, Type, Any, Optional
import pygame
from pygame import Vector2

from src.core.entities.base import Entity
from src.core.components import (
    TransformComponent,
    PhysicsComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent,
    HealthComponent,
    ScoreComponent,
    AudioComponent,
    EffectComponent
)
from src.core.constants import SHIP_MAX_SPEED, SHIP_FRICTION, SHIP_INVULNERABILITY_TIME

class Ship(Entity):
    """Player-controlled ship entity.
    
    Provides:
    - Movement controls
    - Shooting mechanics
    - Collision detection
    - Visual effects
    - Screen wrapping
    """
    
    # Required components for ship functionality
    REQUIRED_COMPONENTS: Dict[Type, str] = {
        TransformComponent: "Position and movement",
        RenderComponent: "Visual representation",
        PhysicsComponent: "Movement physics",
        CollisionComponent: "Collision detection",
        InputComponent: "Control handling",
        EffectComponent: "Visual effects",
        ScreenWrapComponent: "Screen wrapping"
    }
    
    def __init__(self, game):
        """Initialize the ship.
        
        Args:
            game: The game instance this ship belongs to
            
        Raises:
            RuntimeError: If required components fail to initialize
        """
        super().__init__(game)
        self._invulnerable_timer = 0
        self._thrust_timer = 0
        self._initialized_components = set()
        
        try:
            self._init_components()
            self._validate_components()
        except Exception as e:
            print(f"Error initializing ship: {e}")
            self.destroy()
            raise RuntimeError(f"Ship initialization failed: {e}")
        
    def _init_components(self) -> None:
        """Initialize ship components.
        
        Raises:
            RuntimeError: If component initialization fails
        """
        components = []
        try:
            # Transform component for position and movement
            transform = self._registry.create_component('TransformComponent', self)
            transform.position = Vector2(self.game.width / 2, self.game.height / 2)
            components.append(transform)
            self._initialized_components.add(TransformComponent)
            
            # Render component for drawing
            render = self._registry.create_component('RenderComponent', self)
            render.vertices = [(0, -20.0), (-10.0, 10.0), (10.0, 10.0)]
            render.color = (255, 255, 255)
            components.append(render)
            self._initialized_components.add(RenderComponent)
            
            # Physics component for thrust and momentum
            physics = self._registry.create_component('PhysicsComponent', self)
            physics.max_speed = SHIP_MAX_SPEED
            physics.friction = SHIP_FRICTION
            components.append(physics)
            self._initialized_components.add(PhysicsComponent)
            
            # Collision component for hit detection
            collision = self._registry.create_component('CollisionComponent', self, radius=15)
            components.append(collision)
            self._initialized_components.add(CollisionComponent)
            
            # Screen wrap component
            screen_wrap = self._registry.create_component('ScreenWrapComponent', self, 
                screen_size=(self.game.width, self.game.height))
            components.append(screen_wrap)
            self._initialized_components.add(ScreenWrapComponent)
            
            # Effects component for visual effects
            effects = self._registry.create_component('EffectComponent', self)
            self._init_thrust_effect(effects)
            components.append(effects)
            self._initialized_components.add(EffectComponent)
            
            # Input component for controls
            input_component = self._registry.create_component('InputComponent', self)
            self.update_controls()
            components.append(input_component)
            self._initialized_components.add(InputComponent)
            
            # Add all components to entity
            self.components.extend(components)
            
            # Initialize the entity after all components are added
            self.initialize()
            
        except Exception as e:
            # Clean up any components that were created
            for component in components:
                if hasattr(component, 'destroy'):
                    component.destroy()
            self._initialized_components.clear()
            raise RuntimeError(f"Missing required components: {e}")
            
    def _validate_components(self) -> None:
        """Validate that all required components are initialized.
        
        Raises:
            RuntimeError: If any required components are missing
        """
        missing_components = []
        for component_type, purpose in self.REQUIRED_COMPONENTS.items():
            if component_type not in self._initialized_components:
                missing_components.append(f"{component_type.__name__} ({purpose})")
                
        if missing_components:
            self.destroy()  # Clean up the entity if validation fails
            raise RuntimeError(f"Missing required components: {', '.join(missing_components)}")
            
        print("All required ship components initialized successfully")
        
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
        self._invulnerable_timer = SHIP_INVULNERABILITY_TIME
        
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