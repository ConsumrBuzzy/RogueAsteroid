"""Tests for additional components."""
import pytest
import pygame
from pygame import Surface
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
        
    def test_wrap_inactive(self):
        """Test wrapping when component is inactive."""
        self.wrap.active = False
        self.transform.position.x = 850
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position.x, 850)  # Should not wrap
        
    def test_wrap_missing_transform(self):
        """Test wrapping behavior with missing transform."""
        self.entity.remove_component(self.transform)
        self.wrap.update(0.016)  # Should not raise error
        
    def test_wrap_diagonal(self):
        """Test wrapping in both directions simultaneously."""
        self.transform.position = pygame.Vector2(850, 650)
        self.wrap.update(0.016)
        self.assertEqual(self.transform.position, pygame.Vector2(0, 0))

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
        
    def test_multiple_bindings(self):
        """Test multiple keys bound to same action."""
        self.action_count = 0
        
        def test_action():
            self.action_count += 1
        
        # Bind multiple keys
        self.input.bind_key(pygame.K_SPACE, test_action)
        self.input.bind_key(pygame.K_RETURN, test_action)
        
        # Test both keys
        self.input.handle_keydown(pygame.K_SPACE)
        self.input.handle_keydown(pygame.K_RETURN)
        self.assertEqual(self.action_count, 2)
        
    def test_unbind_key(self):
        """Test key unbinding."""
        def test_action():
            self.action_called = True
            
        # Bind and then unbind
        self.input.bind_key(pygame.K_SPACE, test_action)
        self.input.unbind_key(pygame.K_SPACE)
        
        # Test unbound key
        self.input.handle_keydown(pygame.K_SPACE)
        self.assertFalse(self.action_called)
        
    def test_inactive_component(self):
        """Test input handling when component is inactive."""
        def test_action():
            self.action_called = True
            
        self.input.bind_key(pygame.K_SPACE, test_action)
        self.input.active = False
        
        self.input.handle_keydown(pygame.K_SPACE)
        self.assertFalse(self.action_called)

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
        
    def test_zero_mass(self):
        """Test behavior with zero mass."""
        self.physics.mass = 0
        force = pygame.Vector2(10.0, 0.0)
        self.physics.apply_force(force)
        self.physics.update(1.0)
        
        # Zero mass should result in no velocity change
        self.assertEqual(self.transform.velocity, pygame.Vector2(0.0, 0.0))
        
    def test_negative_friction(self):
        """Test behavior with negative friction."""
        self.physics.friction = -0.5  # Invalid friction
        self.transform.velocity = pygame.Vector2(10.0, 0.0)
        self.physics.update(1.0)
        
        # Negative friction should be clamped to 0
        self.assertEqual(self.transform.velocity, pygame.Vector2(10.0, 0.0))
        
    def test_missing_transform(self):
        """Test physics behavior with missing transform."""
        self.entity.remove_component(self.transform)
        force = pygame.Vector2(10.0, 0.0)
        self.physics.apply_force(force)
        self.physics.update(1.0)  # Should not raise error

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
        
    def test_invalid_effect(self):
        """Test handling of invalid effect names."""
        with self.assertRaises(KeyError):
            self.effects.set_effect_active('nonexistent', True)
            
    def test_duplicate_effect(self):
        """Test adding duplicate effect."""
        self.effects.add_effect('test', [(0, 0)], (255, 255, 255))
        
        # Adding same effect should update it
        new_color = (0, 255, 0)
        self.effects.add_effect('test', [(0, 0)], new_color)
        self.assertEqual(self.effects.effects['test'].color, new_color)
        
    def test_effect_cleanup(self):
        """Test effect cleanup on component destruction."""
        self.effects.add_effect('test', [(0, 0)], (255, 255, 255))
        self.effects.set_effect_active('test', True)
        
        self.effects.destroy()
        self.assertEqual(len(self.effects.effects), 0)
        
    def test_missing_transform(self):
        """Test effect behavior with missing transform."""
        self.effects.add_effect('test', [(0, 0)], (255, 255, 255))
        self.effects.set_effect_active('test', True)
        
        self.entity.remove_component(self.transform)
        screen = pygame.Surface((800, 600))
        self.effects.draw(screen)  # Should not raise error

if __name__ == '__main__':
    unittest.main() 