"""Unit tests for components."""
import pytest
import pygame
from src.core.entities.base import Entity
from src.core.entities.components import (
    Component,
    TransformComponent,
    RenderComponent,
    CollisionComponent,
    PhysicsComponent
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

def test_transform_component(entity):
    """Test transform component functionality."""
    transform = entity.add_component(TransformComponent)
    
    # Test position
    transform.position = pygame.Vector2(100, 200)
    assert transform.position.x == 100
    assert transform.position.y == 200
    
    # Test rotation
    transform.rotation = 45
    assert transform.rotation == 45

def test_physics_component(entity):
    """Test physics component functionality."""
    physics = entity.add_component(PhysicsComponent)
    transform = entity.add_component(TransformComponent)
    
    # Test velocity
    physics.velocity = pygame.Vector2(10, 0)
    entity.update(1.0)
    assert transform.position.x == 10
    assert transform.position.y == 0

def test_collision_component(entity):
    """Test collision component functionality."""
    collision = entity.add_component(CollisionComponent, radius=10)
    transform = entity.add_component(TransformComponent)
    
    # Create another entity for collision testing
    other_entity = Entity(game_mock)
    other_collision = other_entity.add_component(CollisionComponent, radius=10)
    other_transform = other_entity.add_component(TransformComponent)
    
    # Test collision detection
    transform.position = pygame.Vector2(0, 0)
    other_transform.position = pygame.Vector2(15, 0)
    assert collision.check_collision(other_collision)
    
    other_transform.position = pygame.Vector2(25, 0)
    assert not collision.check_collision(other_collision)

def test_render_component(entity):
    """Test render component functionality."""
    render = entity.add_component(RenderComponent)
    
    # Test color
    render.color = (255, 0, 0)
    assert render.color == (255, 0, 0)
    
    # Test vertices
    vertices = [(0, 0), (10, 0), (0, 10)]
    render.vertices = vertices
    assert render.vertices == vertices
    
    # Test visibility
    render.visible = False
    assert not render.visible 