"""Test suite for collision system."""
import pytest
import pygame
from src.core.game import Game
from src.core.entities.base import Entity
from src.core.entities.components import CollisionComponent, TransformComponent
from src.core.systems.collision import CollisionSystem
from src.core.constants import *

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.fixture
def collision_system(game):
    """Create a collision system instance."""
    return CollisionSystem(game)

@pytest.fixture
def create_collider(game):
    """Create an entity with collision component."""
    def _create(pos=(0, 0), radius=10, tag="test"):
        entity = Entity(game)
        transform = entity.add_component(TransformComponent)
        transform.position = pygame.Vector2(pos)
        collider = entity.add_component(CollisionComponent)
        collider.radius = radius
        collider.tag = tag
        return entity, collider
    return _create

@pytest.mark.game
class TestCollisionSystem:
    """Test cases for the collision system."""
    
    def test_collision_detection(self, game, collision_system, create_collider):
        """Test basic collision detection between entities."""
        # Create two overlapping entities
        entity1, collider1 = create_collider(pos=(100, 100), radius=20)
        entity2, collider2 = create_collider(pos=(110, 110), radius=20)
        
        # Check for collision
        collision_system.update(1/60)
        collisions = collision_system.get_collisions()
        
        assert len(collisions) == 1, "One collision should be detected"
        assert (collider1, collider2) in collisions or (collider2, collider1) in collisions, \
            "Collision pair should be recorded"
    
    def test_no_collision(self, game, collision_system, create_collider):
        """Test entities that are not colliding."""
        # Create two distant entities
        entity1, collider1 = create_collider(pos=(100, 100), radius=20)
        entity2, collider2 = create_collider(pos=(200, 200), radius=20)
        
        # Check for collisions
        collision_system.update(1/60)
        collisions = collision_system.get_collisions()
        
        assert len(collisions) == 0, "No collisions should be detected"
    
    def test_collision_tags(self, game, collision_system, create_collider):
        """Test collision filtering by tags."""
        # Create entities with different tags
        entity1, collider1 = create_collider(pos=(100, 100), radius=20, tag="player")
        entity2, collider2 = create_collider(pos=(110, 110), radius=20, tag="enemy")
        entity3, collider3 = create_collider(pos=(120, 120), radius=20, tag="bullet")
        
        # Set collision masks
        collision_system.set_collision_mask("player", ["enemy"])
        collision_system.set_collision_mask("enemy", ["player", "bullet"])
        collision_system.set_collision_mask("bullet", ["enemy"])
        
        # Update and get collisions
        collision_system.update(1/60)
        collisions = collision_system.get_collisions()
        
        # Verify correct collision pairs
        for c1, c2 in collisions:
            assert (c1.tag == "player" and c2.tag == "enemy") or \
                   (c1.tag == "enemy" and c2.tag == "player") or \
                   (c1.tag == "bullet" and c2.tag == "enemy") or \
                   (c1.tag == "enemy" and c2.tag == "bullet"), \
                "Only configured tag pairs should collide"
    
    def test_collision_callbacks(self, game, collision_system, create_collider):
        """Test collision callback execution."""
        # Track callback execution
        callback_executed = False
        def on_collision(other):
            nonlocal callback_executed
            callback_executed = True
        
        # Create colliding entities
        entity1, collider1 = create_collider(pos=(100, 100), radius=20)
        entity2, collider2 = create_collider(pos=(110, 110), radius=20)
        
        # Set callback
        collider1.on_collision = on_collision
        
        # Update system
        collision_system.update(1/60)
        
        assert callback_executed, "Collision callback should be executed"
    
    def test_collision_resolution(self, game, collision_system, create_collider):
        """Test basic collision resolution."""
        # Create overlapping entities
        entity1, collider1 = create_collider(pos=(100, 100), radius=20)
        entity2, collider2 = create_collider(pos=(110, 110), radius=20)
        
        # Store initial positions
        initial_pos1 = entity1.get_component(TransformComponent).position.copy()
        initial_pos2 = entity2.get_component(TransformComponent).position.copy()
        
        # Enable collision resolution
        collision_system.resolve_collisions = True
        collision_system.update(1/60)
        
        # Check positions have changed
        current_pos1 = entity1.get_component(TransformComponent).position
        current_pos2 = entity2.get_component(TransformComponent).position
        
        assert current_pos1 != initial_pos1 or current_pos2 != initial_pos2, \
            "Entities should be moved apart"
        
        # Verify no more collision
        collision_system.update(1/60)
        collisions = collision_system.get_collisions()
        assert len(collisions) == 0, "Collision should be resolved"
    
    def test_dynamic_static_collision(self, game, collision_system, create_collider):
        """Test collision between dynamic and static entities."""
        # Create dynamic and static entities
        dynamic, dynamic_collider = create_collider(pos=(100, 100), radius=20)
        static, static_collider = create_collider(pos=(110, 110), radius=20)
        
        # Mark static entity
        static_collider.is_static = True
        
        # Store initial positions
        initial_dynamic_pos = dynamic.get_component(TransformComponent).position.copy()
        initial_static_pos = static.get_component(TransformComponent).position.copy()
        
        # Enable collision resolution
        collision_system.resolve_collisions = True
        collision_system.update(1/60)
        
        # Check only dynamic entity moved
        current_dynamic_pos = dynamic.get_component(TransformComponent).position
        current_static_pos = static.get_component(TransformComponent).position
        
        assert current_dynamic_pos != initial_dynamic_pos, "Dynamic entity should move"
        assert current_static_pos == initial_static_pos, "Static entity should not move"
    
    def test_collision_layers(self, game, collision_system, create_collider):
        """Test collision layer filtering."""
        # Create entities on different layers
        entity1, collider1 = create_collider(pos=(100, 100), radius=20)
        entity2, collider2 = create_collider(pos=(110, 110), radius=20)
        
        # Set different layers
        collider1.layer = 1
        collider2.layer = 2
        
        # Configure layer collision matrix
        collision_system.set_layer_collision(1, 2, False)
        
        # Update and check no collision
        collision_system.update(1/60)
        collisions = collision_system.get_collisions()
        
        assert len(collisions) == 0, "Entities on non-colliding layers should not interact"
        
        # Enable layer collision
        collision_system.set_layer_collision(1, 2, True)
        collision_system.update(1/60)
        collisions = collision_system.get_collisions()
        
        assert len(collisions) == 1, "Entities should collide when layers are set to interact"
    
    def test_collision_groups(self, game, collision_system, create_collider):
        """Test collision group filtering."""
        # Create entities
        entity1, collider1 = create_collider(pos=(100, 100), radius=20)
        entity2, collider2 = create_collider(pos=(110, 110), radius=20)
        entity3, collider3 = create_collider(pos=(120, 120), radius=20)
        
        # Set collision groups
        collider1.group = 1
        collider2.group = 1
        collider3.group = 2
        
        # Update and check collisions
        collision_system.update(1/60)
        collisions = collision_system.get_collisions()
        
        # Verify group behavior
        group_collisions = [(c1.group, c2.group) for c1, c2 in collisions]
        assert (1, 2) in group_collisions or (2, 1) in group_collisions, \
            "Different groups should collide"
        assert not any(g1 == g2 == 1 for g1, g2 in group_collisions), \
            "Same group should not collide" 