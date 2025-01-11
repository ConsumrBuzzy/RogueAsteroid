"""Unit tests for additional game components."""
import unittest
import pygame
from src.core.entities.base import Entity, TransformComponent
from src.core.entities.components import (
    ScreenWrapComponent,
    InputComponent,
    PhysicsComponent,
    EffectComponent
)

class MockGame:
    """Mock game class for testing."""
    def __init__(self):
        self.width = 800
        self.height = 600
        self.dt = 0.016  # 60 FPS
        self.settings = {'controls': {'scheme': 'arrows'}}

class TestScreenWrapComponent(unittest.TestCase):
    """Test cases for ScreenWrapComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.transform = self.entity.add_component(TransformComponent)
        self.transform.position = pygame.Vector2(0.0, 0.0)
        self.wrap = self.entity.add_component(ScreenWrapComponent, 800, 600)
    
    def test_wrap_x(self):
        """Test wrapping in x direction."""
        # Test right edge
        self.transform.position.x = 850
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position.x, 0)
        
        # Test left edge
        self.transform.position.x = -50
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position.x, 800)
    
    def test_wrap_y(self):
        """Test wrapping in y direction."""
        # Test bottom edge
        self.transform.position.y = 650
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position.y, 0)
        
        # Test top edge
        self.transform.position.y = -50
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position.y, 600)

class TestInputComponent(unittest.TestCase):
    """Test cases for InputComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.input = self.entity.add_component(InputComponent)
        self.action_called = False
    
    def test_key_binding(self):
        """Test key binding and action calling."""
        def test_action():
            self.action_called = True
        
        # Bind a key
        self.input.bind_key(pygame.K_SPACE, test_action, continuous=False)
        
        # Simulate key press
        self.input.handle_keydown(pygame.K_SPACE)
        self.assertTrue(self.action_called)
    
    def test_continuous_action(self):
        """Test continuous action handling."""
        self.continuous_count = 0
        
        def continuous_action():
            self.continuous_count += 1
        
        # Bind continuous action
        self.input.bind_key(pygame.K_UP, continuous_action, continuous=True)
        
        # Simulate held key
        self.input.handle_keydown(pygame.K_UP)
        self.input.update(0.016)  # One frame
        self.input.update(0.016)  # Another frame
        
        self.assertEqual(self.continuous_count, 2)
        
        # Release key
        self.input.handle_keyup(pygame.K_UP)
        self.input.update(0.016)
        self.assertEqual(self.continuous_count, 2)  # Should not increase

class TestPhysicsComponent(unittest.TestCase):
    """Test cases for PhysicsComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.transform = self.entity.add_component(TransformComponent)
        self.transform.position = pygame.Vector2(0.0, 0.0)
        self.physics = self.entity.add_component(PhysicsComponent, mass=1.0, max_speed=100.0)
    
    def test_force_application(self):
        """Test force application and velocity update."""
        force = pygame.Vector2(10.0, 0.0)
        self.physics.apply_force(force)
        self.physics.update(1.0)  # 1 second
        
        # F = ma, v = at
        expected_velocity = pygame.Vector2(force.x / self.physics.mass, force.y / self.physics.mass)
        self.assertEqual(self.transform.velocity, expected_velocity)
    
    def test_max_speed(self):
        """Test maximum speed limit."""
        # Apply large force
        force = pygame.Vector2(1000.0, 0.0)
        self.physics.apply_force(force)
        self.physics.update(1.0)
        
        speed = (self.transform.velocity.x ** 2 + self.transform.velocity.y ** 2) ** 0.5
        self.assertLessEqual(speed, self.physics.max_speed)
    
    def test_friction(self):
        """Test friction application."""
        # Set initial velocity
        self.transform.velocity = pygame.Vector2(10.0, 0.0)
        self.physics.friction = 0.5  # 50% friction per update
        
        self.physics.update(1.0)
        expected_velocity = pygame.Vector2(5.0, 0.0)  # After 50% friction
        self.assertEqual(self.transform.velocity, expected_velocity)

class TestEffectComponent(unittest.TestCase):
    """Test cases for EffectComponent."""
    
    def setUp(self):
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.transform = self.entity.add_component(TransformComponent)
        self.transform.position = pygame.Vector2(100.0, 100.0)
        self.effects = self.entity.add_component(EffectComponent)
    
    def test_effect_creation(self):
        """Test effect creation and properties."""
        vertices = [(0, 0), (10, 0), (5, 10)]
        color = (255, 0, 0)
        offset = pygame.Vector2(5, 5)
        
        self.effects.add_effect('test', vertices, color, offset)
        
        effect = self.effects.effects.get('test')
        self.assertIsNotNone(effect)
        self.assertEqual(effect.vertices, vertices)
        self.assertEqual(effect.color, color)
        self.assertEqual(effect.offset, offset)
        self.assertFalse(effect.active)
    
    def test_effect_activation(self):
        """Test effect activation state."""
        self.effects.add_effect('test', [(0, 0)], (255, 255, 255))
        
        self.effects.set_effect_active('test', True)
        self.assertTrue(self.effects.effects['test'].active)
        
        self.effects.set_effect_active('test', False)
        self.assertFalse(self.effects.effects['test'].active)

if __name__ == '__main__':
    unittest.main() 