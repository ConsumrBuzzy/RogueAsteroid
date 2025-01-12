"""Unit tests for additional components."""
import pytest
import pygame
from src.core.entities.base import Entity
from src.core.entities.components import (
    TransformComponent,
    InputComponent,
    ScreenWrapComponent,
    ParticleComponent,
    EffectComponent
)

@pytest.fixture
def game_mock():
    """Create a mock game instance."""
    class GameMock:
        def __init__(self):
            self.width = 800
            self.height = 600
            self.dt = 0.016
    return GameMock()

@pytest.fixture
def entity(game_mock):
    """Create a test entity."""
    return Entity(game_mock)

def test_input_component(entity):
    """Test input component functionality."""
    input_comp = entity.add_component(InputComponent)
    
    # Test key binding
    test_key = pygame.K_SPACE
    test_called = False
    
    def test_action():
        nonlocal test_called
        test_called = True
    
    input_comp.bind_key(test_key, test_action)
    input_comp.handle_keydown(test_key)
    assert test_called

def test_screen_wrap_component(entity):
    """Test screen wrap component functionality."""
    wrap = entity.add_component(ScreenWrapComponent)
    transform = entity.add_component(TransformComponent)
    
    # Test wrapping
    transform.position = pygame.Vector2(-10, -10)
    entity.update(0.016)
    assert transform.position.x >= 0
    assert transform.position.y >= 0

def test_particle_component(entity):
    """Test particle component functionality."""
    particle = entity.add_component(ParticleComponent)
    
    # Test lifetime
    particle.lifetime = 1.0
    entity.update(0.5)
    assert particle.enabled
    entity.update(0.6)
    assert not particle.enabled

def test_effect_component(entity):
    """Test effect component functionality."""
    effect = entity.add_component(EffectComponent)
    
    # Test effect management
    test_called = False
    def on_end():
        nonlocal test_called
        test_called = True
    
    effect.add_effect("test", 1.0, on_end=on_end)
    assert effect.has_effect("test")
    
    entity.update(1.1)
    assert not effect.has_effect("test")
    assert test_called 