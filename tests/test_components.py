"""Unit tests for core component system."""
import pytest
import pygame
from pygame import Surface, Vector2
from typing import Tuple

from src.core.components.base import (
    Component,
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    InputComponent,
    ScreenWrapComponent
)

@pytest.mark.unit
class TestComponent:
    """Test cases for base Component class."""

    def test_component_init(self, entity):
        """Test component initialization."""
        component = Component(entity)
        assert component.entity == entity
        assert component.active is True
    
    def test_component_lifecycle(self, entity):
        """Test component lifecycle methods."""
        component = Component(entity)
        
        # Test initial state
        assert component.active is True
        
        # Test update (should not raise error)
        component.update(1/60)
        
        # Test draw (should not raise error)
        surface = Surface((800, 600))
        component.draw(surface)
        
        # Test cleanup
        component.cleanup()
        assert component.active is True  # Base cleanup doesn't change active state

@pytest.mark.unit
class TestTransformComponent:
    """Test cases for TransformComponent."""
    
    def test_transform_init(self, entity):
        """Test transform component initialization."""
        transform = TransformComponent(entity, x=100, y=200, rotation=45)
        assert transform.x == 100
        assert transform.y == 200
        assert transform.rotation == 45
        assert transform.velocity == Vector2(0, 0)
    
    def test_transform_position(self, transform):
        """Test position getting and setting."""
        transform.set_position(300, 400)
        assert transform.get_position() == (300, 400)
        
    def test_transform_velocity(self, transform):
        """Test velocity updates position."""
        transform.velocity = Vector2(100, 50)
        dt = 1/60
        
        initial_x = transform.x
        initial_y = transform.y
        
        transform.update(dt)
        
        assert transform.x == pytest.approx(initial_x + 100 * dt)
        assert transform.y == pytest.approx(initial_y + 50 * dt)

@pytest.mark.unit
class TestRenderComponent:
    """Test cases for RenderComponent."""
    
    def test_render_init(self, entity):
        """Test render component initialization."""
        points = [(0, 0), (10, 0), (0, 10)]
        color = (255, 0, 0)
        render = RenderComponent(entity, color=color, points=points)
        
        assert render.color == color
        assert render.points == points
        assert render.visible is True
    
    def test_render_visibility(self, render, screen):
        """Test render visibility control."""
        render.visible = False
        render.draw(screen)  # Should not draw when invisible
        
        render.visible = True
        render.draw(screen)  # Should draw when visible

@pytest.mark.unit
class TestCollisionComponent:
    """Test cases for CollisionComponent."""
    
    def test_collision_init(self, entity):
        """Test collision component initialization."""
        collision = CollisionComponent(entity, radius=10)
        assert collision.radius == 10
        assert collision.colliding is False
    
    def test_collision_rect(self, collision, transform):
        """Test collision rectangle calculation."""
        rect = collision.get_collision_rect()
        assert rect.width == collision.radius * 2
        assert rect.height == collision.radius * 2
        assert rect.centerx == transform.x
        assert rect.centery == transform.y

@pytest.mark.unit
class TestInputComponent:
    """Test cases for InputComponent."""
    
    def test_input_init(self, entity):
        """Test input component initialization."""
        input_comp = InputComponent(entity)
        assert len(input_comp._action_bindings) == 0
        assert len(input_comp._action_handlers) == 0
    
    def test_input_bindings(self, input_component):
        """Test action binding and handling."""
        action_called = False
        
        def test_action():
            nonlocal action_called
            action_called = True
        
        # Bind action
        input_component.bind_action("test", [pygame.K_SPACE], test_action)
        
        # Simulate key press
        pygame.event.post(pygame.event.Event(pygame.KEYDOWN, {'key': pygame.K_SPACE}))
        input_component.update(1/60)
        
        assert action_called is True

@pytest.mark.unit
class TestScreenWrapComponent:
    """Test cases for ScreenWrapComponent."""
    
    def test_wrap_horizontal(self, screen_wrap, transform):
        """Test horizontal screen wrapping."""
        from src.core.constants import SCREEN_WIDTH
        
        # Test wrap right to left
        transform.x = SCREEN_WIDTH + 10
        screen_wrap.update(1/60)
        assert transform.x == 0
        
        # Test wrap left to right
        transform.x = -10
        screen_wrap.update(1/60)
        assert transform.x == SCREEN_WIDTH
    
    def test_wrap_vertical(self, screen_wrap, transform):
        """Test vertical screen wrapping."""
        from src.core.constants import SCREEN_HEIGHT
        
        # Test wrap bottom to top
        transform.y = SCREEN_HEIGHT + 10
        screen_wrap.update(1/60)
        assert transform.y == 0
        
        # Test wrap top to bottom
        transform.y = -10
        screen_wrap.update(1/60)
        assert transform.y == SCREEN_HEIGHT 