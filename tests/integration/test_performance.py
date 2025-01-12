"""Performance tests for the game."""
import pytest
import pygame
import time
from typing import List
from src.core.entities.base import Entity
from src.core.entities.components import (
    TransformComponent,
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

def create_test_entities(game_mock, count: int) -> List[Entity]:
    """Create test entities with basic components."""
    entities = []
    for i in range(count):
        entity = Entity(game_mock)
        transform = entity.add_component(TransformComponent)
        transform.position = pygame.Vector2(i % 800, i % 600)
        entity.add_component(CollisionComponent, radius=10)
        entities.append(entity)
    return entities

def test_collision_performance(game_mock):
    """Test collision detection performance with many entities."""
    entity_count = 100
    entities = create_test_entities(game_mock, entity_count)
    
    # Measure time for collision checks
    start_time = time.time()
    for entity in entities:
        collision = entity.get_component(CollisionComponent)
        if collision:
            for other in entities:
                if other != entity:
                    other_collision = other.get_component(CollisionComponent)
                    if other_collision:
                        collision.check_collision(other_collision)
    end_time = time.time()
    
    # Performance should be reasonable
    elapsed = end_time - start_time
    assert elapsed < 1.0, f"Collision checks took too long: {elapsed:.2f} seconds" 