"""Unit tests for core component system."""
import unittest
import numpy as np
from src.core.entities.base import (
    Entity,
    Component,
    TransformComponent,
    RenderComponent,
    CollisionComponent
)

class MockGame:
    """Mock game class for testing."""
    def __init__(self):
        self.width = 800
        self.height = 600
        self.dt = 0.016  # 60 FPS

class TestComponent(unittest.TestCase):
    """Test cases for base Component class."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
    
    def test_component_init(self):
        """Test component initialization."""
        component = Component(self.entity)
        self.assertEqual(component.entity, self.entity)
    
    def test_component_update(self):
        """Test component update method."""
        component = Component(self.entity)
        # Base update should not raise any errors
        component.update(0.016)

class TestTransformComponent(unittest.TestCase):
    """Test cases for TransformComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.transform = self.entity.add_component(TransformComponent, 100.0, 200.0)
    
    def test_transform_init(self):
        """Test transform initialization."""
        self.assertTrue(np.array_equal(self.transform.position, np.array([100.0, 200.0])))
        self.assertTrue(np.array_equal(self.transform.velocity, np.array([0.0, 0.0])))
        self.assertEqual(self.transform.rotation, 0.0)
        self.assertEqual(self.transform.rotation_speed, 0.0)
    
    def test_transform_update(self):
        """Test transform update with velocity."""
        self.transform.velocity = np.array([10.0, -5.0])
        self.transform.rotation_speed = 45.0  # 45 degrees per second
        
        # Update for 1 second
        self.transform.update(1.0)
        
        expected_pos = np.array([110.0, 195.0])
        self.assertTrue(np.allclose(self.transform.position, expected_pos))
        self.assertEqual(self.transform.rotation, 45.0)

class TestCollisionComponent(unittest.TestCase):
    """Test cases for CollisionComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity1 = Entity(self.game)
        self.entity2 = Entity(self.game)
        
        # Add transform components
        self.transform1 = self.entity1.add_component(TransformComponent, 0.0, 0.0)
        self.transform2 = self.entity2.add_component(TransformComponent, 10.0, 0.0)
        
        # Add collision components
        self.collision1 = self.entity1.add_component(CollisionComponent, radius=5.0)
        self.collision2 = self.entity2.add_component(CollisionComponent, radius=5.0)
    
    def test_collision_detection(self):
        """Test basic collision detection."""
        # Objects should be colliding (distance 10, combined radius 10)
        self.assertTrue(self.collision1.check_collision(self.collision2))
        
        # Move objects apart
        self.transform2.position = np.array([20.0, 0.0])
        self.assertFalse(self.collision1.check_collision(self.collision2))
    
    def test_collision_normal(self):
        """Test collision normal calculation."""
        normal = self.collision1.get_collision_normal(self.collision2)
        expected = np.array([-1.0, 0.0])  # Points from entity2 to entity1
        self.assertTrue(np.allclose(normal, expected))
    
    def test_collision_active_state(self):
        """Test collision active state."""
        self.assertTrue(self.collision1.check_collision(self.collision2))
        
        # Disable collision on one object
        self.collision1.active = False
        self.assertFalse(self.collision1.check_collision(self.collision2))
        
        # Re-enable collision
        self.collision1.active = True
        self.assertTrue(self.collision1.check_collision(self.collision2))

class TestRenderComponent(unittest.TestCase):
    """Test cases for RenderComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.transform = self.entity.add_component(TransformComponent, 100.0, 100.0)
        self.render = self.entity.add_component(RenderComponent)
    
    def test_render_init(self):
        """Test render component initialization."""
        self.assertEqual(self.render.vertices, [])
        self.assertEqual(self.render.color, (255, 255, 255))
        self.assertTrue(self.render.visible)
    
    def test_render_visibility(self):
        """Test render visibility control."""
        self.assertTrue(self.render.visible)
        self.render.visible = False
        self.assertFalse(self.render.visible)

if __name__ == '__main__':
    unittest.main() 