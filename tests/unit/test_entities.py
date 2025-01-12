"""Unit tests for entity system."""
import pytest
import pygame
from typing import Any
from src.core.entities.base import Entity
from src.core.entities.components import (
    Component,
    TransformComponent,
    RenderComponent,
    CollisionComponent
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

def test_entity_creation(entity):
    """Test entity creation."""
    assert entity is not None
    assert isinstance(entity, Entity)
    assert entity.game is not None

def test_add_component(entity):
    """Test adding components to entity."""
    transform = entity.add_component(TransformComponent)
    assert transform is not None
    assert isinstance(transform, TransformComponent)
    assert transform.entity == entity

def test_get_component(entity):
    """Test getting components from entity."""
    transform = entity.add_component(TransformComponent)
    assert entity.get_component(TransformComponent) == transform
    assert entity.get_component('transform') == transform

def test_duplicate_component(entity):
    """Test adding duplicate component."""
    entity.add_component(TransformComponent)
    with pytest.raises(ValueError):
        entity.add_component(TransformComponent)

def test_component_update(entity):
    """Test component update."""
    class TestComponent(Component):
        def __init__(self, entity):
            super().__init__(entity)
            self.updated = False
        def update(self, dt: float):
            self.updated = True
    
    component = entity.add_component(TestComponent)
    entity.update(0.016)
    assert component.updated 