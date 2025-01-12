"""Tests for additional components."""
import pytest
import pygame
from pygame import Surface, Vector2
from typing import Tuple

from src.core.entities.base import Entity
from src.core.components import (
    TransformComponent,
    PhysicsComponent,
    EffectComponent,
    WaveComponent,
    UIComponent,
    TimerComponent,
    ScoreComponent,
    HealthComponent,
    DebugComponent,
    AudioComponent
)

@pytest.fixture
def mock_game():
    """Create a mock game instance for testing."""
    class MockGame:
        def __init__(self):
            self.screen = Surface((800, 600))
            self.dt = 0.016
    return MockGame()

@pytest.fixture
def entity(mock_game):
    """Create a test entity."""
    return Entity(mock_game)

@pytest.mark.unit
class TestEffectComponent:
    """Test cases for EffectComponent."""
    
    def test_effect_init(self, entity):
        """Test EffectComponent initialization."""
        effect = EffectComponent(entity)
        assert effect.entity == entity
        assert effect.effects == {}
    
    def test_effect_creation(self, entity):
        """Test effect creation and properties."""
        effect = EffectComponent(entity)
        vertices = [(0, 0), (10, 0), (5, 10)]
        color = (255, 0, 0)
        offset = Vector2(5, 5)
        
        effect.add_effect('test', vertices, color, offset)
        created_effect = effect.effects.get('test')
        assert created_effect is not None
        assert created_effect.vertices == vertices
        assert created_effect.color == color
        assert created_effect.offset == offset
        assert not created_effect.active 