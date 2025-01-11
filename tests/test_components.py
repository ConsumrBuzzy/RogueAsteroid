"""Unit tests for core components."""
import unittest
import numpy as np
from src.core.entities.base import (
    Entity,
    TransformComponent,
    RenderComponent,
    CollisionComponent
)
from src.core.entities.components import (
    ScreenWrapComponent,
    InputComponent,
    PhysicsComponent,
    EffectComponent
)

class MockGame:
    """Mock game class for testing."""
    def __init__(self):
        self.dt = 0.016  # 60 FPS
        self.settings = {'controls': {'scheme': 'arrows'}}
        self.entities = []

class TestTransformComponent(unittest.TestCase):
    """Test cases for TransformComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.transform = self.entity.add_component(TransformComponent, 100, 200)
    
    def test_initialization(self):
        """Test component initialization."""
        self.assertEqual(self.transform.position[0], 100)
        self.assertEqual(self.transform.position[1], 200)
        self.assertEqual(self.transform.rotation, 0)
        np.testing.assert_array_equal(self.transform.velocity, np.array([0.0, 0.0]))
    
    def test_update_position(self):
        """Test position update with velocity."""
        self.transform.velocity = np.array([10.0, 20.0])
        self.transform.update(0.5)  # 0.5 seconds
        np.testing.assert_array_equal(
            self.transform.position,
            np.array([105.0, 210.0])
        )

class TestPhysicsComponent(unittest.TestCase):
    """Test cases for PhysicsComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.transform = self.entity.add_component(TransformComponent, 0, 0)
        self.physics = self.entity.add_component(PhysicsComponent, mass=1.0)
    
    def test_apply_force(self):
        """Test force application."""
        force = np.array([10.0, 0.0])
        self.physics.apply_force(force)
        self.physics.update(1.0)  # 1 second
        
        transform = self.entity.get_component(TransformComponent)
        self.assertIsNotNone(transform)
        
        # F = ma, a = F/m, v = at
        expected_velocity = force / self.physics.mass
        np.testing.assert_array_almost_equal(
            transform.velocity,
            expected_velocity
        )
    
    def test_max_speed(self):
        """Test maximum speed limit."""
        self.physics.max_speed = 5.0
        force = np.array([100.0, 0.0])  # Large force
        self.physics.apply_force(force)
        self.physics.update(1.0)
        
        transform = self.entity.get_component(TransformComponent)
        self.assertIsNotNone(transform)
        
        speed = np.linalg.norm(transform.velocity)
        self.assertLessEqual(speed, self.physics.max_speed)

class TestCollisionComponent(unittest.TestCase):
    """Test cases for CollisionComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity1 = Entity(self.game)
        self.entity2 = Entity(self.game)
        
        # Set up entities with transform and collision
        self.transform1 = self.entity1.add_component(TransformComponent, 0, 0)
        self.collision1 = self.entity1.add_component(CollisionComponent, radius=10)
        
        self.transform2 = self.entity2.add_component(TransformComponent, 100, 100)
        self.collision2 = self.entity2.add_component(CollisionComponent, radius=10)
    
    def test_no_collision(self):
        """Test entities not colliding."""
        self.assertFalse(self.collision1.collides_with(self.collision2))
    
    def test_collision(self):
        """Test entities colliding."""
        # Move entities close together
        self.transform2.position = np.array([15.0, 0.0])
        self.assertTrue(self.collision1.collides_with(self.collision2))

class TestScreenWrapComponent(unittest.TestCase):
    """Test cases for ScreenWrapComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.transform = self.entity.add_component(TransformComponent, 0, 0)
        self.wrap = self.entity.add_component(ScreenWrapComponent, 800, 600)
    
    def test_wrap_x(self):
        """Test wrapping in x direction."""
        self.transform.position[0] = 850  # Beyond right edge
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position[0], 50)
        
        self.transform.position[0] = -50  # Beyond left edge
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position[0], 750)
    
    def test_wrap_y(self):
        """Test wrapping in y direction."""
        self.transform.position[1] = 650  # Beyond bottom edge
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position[1], 50)
        
        self.transform.position[1] = -50  # Beyond top edge
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position[1], 550)

if __name__ == '__main__':
    unittest.main() 