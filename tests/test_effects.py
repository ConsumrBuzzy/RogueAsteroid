"""Tests for the particle effect system."""
import unittest
import pygame
import math
from src.core.config.effects import validate_template, EFFECT_TEMPLATES
from src.core.components.effect import EffectComponent, Particle
from src.core.entity import Entity

class MockGame:
    """Mock game class for testing."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.width = 800
        self.height = 600

class TestEffectTemplateValidation(unittest.TestCase):
    """Test cases for effect template validation."""
    
    def setUp(self):
        """Set up test cases."""
        self.valid_template = {
            'count': 10,
            'speed_range': (50, 100),
            'angle_spread': 30,
            'lifetime_range': (0.2, 0.4),
            'size_range': (1, 2),
            'colors': [(255, 0, 0), (0, 255, 0)]
        }
    
    def test_valid_template(self):
        """Test validation of a valid template."""
        self.assertTrue(validate_template('test', self.valid_template))
    
    def test_missing_field(self):
        """Test validation with missing required field."""
        invalid = self.valid_template.copy()
        del invalid['count']
        with self.assertRaises(ValueError):
            validate_template('test', invalid)
    
    def test_invalid_type(self):
        """Test validation with invalid field type."""
        invalid = self.valid_template.copy()
        invalid['count'] = '10'  # Should be int
        with self.assertRaises(ValueError):
            validate_template('test', invalid)
    
    def test_invalid_range(self):
        """Test validation with invalid range values."""
        invalid = self.valid_template.copy()
        invalid['speed_range'] = (100, 50)  # max < min
        with self.assertRaises(ValueError):
            validate_template('test', invalid)
    
    def test_invalid_color(self):
        """Test validation with invalid color values."""
        invalid = self.valid_template.copy()
        invalid['colors'] = [(256, 0, 0)]  # Invalid RGB value
        with self.assertRaises(ValueError):
            validate_template('test', invalid)
    
    def test_empty_colors(self):
        """Test validation with empty colors list."""
        invalid = self.valid_template.copy()
        invalid['colors'] = []
        with self.assertRaises(ValueError):
            validate_template('test', invalid)
    
    def test_default_templates(self):
        """Test all default templates are valid."""
        for name, template in EFFECT_TEMPLATES.items():
            try:
                self.assertTrue(validate_template(name, template))
            except ValueError as e:
                self.fail(f"Default template '{name}' is invalid: {e}")

class TestParticle(unittest.TestCase):
    """Test cases for individual particles."""
    
    def setUp(self):
        """Set up test cases."""
        self.particle = Particle(
            x=100.0,
            y=100.0,
            velocity=(50.0, 0.0),
            color=(255, 0, 0),
            lifetime=1.0,
            size=2.0
        )
    
    def test_particle_initialization(self):
        """Test particle initialization."""
        self.assertEqual(self.particle.x, 100.0)
        self.assertEqual(self.particle.y, 100.0)
        self.assertEqual(self.particle.vx, 50.0)
        self.assertEqual(self.particle.vy, 0.0)
        self.assertEqual(self.particle.color, (255, 0, 0))
        self.assertEqual(self.particle.lifetime, 1.0)
        self.assertEqual(self.particle.size, 2.0)
        self.assertEqual(self.particle.alpha, 255)
    
    def test_particle_update(self):
        """Test particle update and lifetime."""
        # Update with 0.5s - should move and fade
        self.assertTrue(self.particle.update(0.5))
        self.assertEqual(self.particle.x, 125.0)  # 100 + 50 * 0.5
        self.assertEqual(self.particle.alpha, 127)  # ~255 * 0.5
        
        # Update with remaining lifetime - should die
        self.assertFalse(self.particle.update(0.5))

class TestEffectComponent(unittest.TestCase):
    """Test cases for EffectComponent."""
    
    def setUp(self):
        """Set up test cases."""
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.effects = EffectComponent(self.entity)
    
    def test_initialization(self):
        """Test component initialization."""
        self.assertEqual(len(self.effects._particles), 0)
        self.assertGreater(len(self.effects._effect_templates), 0)
        
        # Verify default templates are loaded
        for name in EFFECT_TEMPLATES:
            self.assertIn(name, self.effects._effect_templates)
    
    def test_emit_particles(self):
        """Test particle emission."""
        position = (100, 100)
        self.effects.emit('thrust', position, 0)
        
        # Verify particles were created
        self.assertEqual(
            len(self.effects._particles),
            EFFECT_TEMPLATES['thrust']['count']
        )
        
        # Verify particle properties
        for particle in self.effects._particles:
            self.assertGreaterEqual(particle.lifetime, 
                                  EFFECT_TEMPLATES['thrust']['lifetime_range'][0])
            self.assertLessEqual(particle.lifetime, 
                               EFFECT_TEMPLATES['thrust']['lifetime_range'][1])
    
    def test_particle_update(self):
        """Test particle system update."""
        # Create short-lived particles
        template = self.valid_template = {
            'count': 5,
            'speed_range': (50, 100),
            'angle_spread': 30,
            'lifetime_range': (0.1, 0.2),
            'size_range': (1, 2),
            'colors': [(255, 0, 0)]
        }
        self.effects.add_effect_template('test', template)
        self.effects.emit('test', (100, 100), 0)
        
        # Update half lifetime
        self.effects.update(0.05)
        self.assertEqual(len(self.effects._particles), 5)
        
        # Update remaining lifetime
        self.effects.update(0.15)
        self.assertEqual(len(self.effects._particles), 0)
    
    def test_clear_particles(self):
        """Test particle clearing."""
        self.effects.emit('thrust', (100, 100), 0)
        self.assertGreater(len(self.effects._particles), 0)
        
        self.effects.clear_particles()
        self.assertEqual(len(self.effects._particles), 0)
    
    def test_custom_template(self):
        """Test adding and using custom template."""
        template = {
            'count': 1,
            'speed_range': (10, 20),
            'angle_spread': 0,
            'lifetime_range': (1.0, 1.0),
            'size_range': (1.0, 1.0),
            'colors': [(0, 255, 0)]
        }
        
        self.effects.add_effect_template('custom', template)
        self.effects.emit('custom', (100, 100), 0)
        
        particle = self.effects._particles[0]
        self.assertEqual(particle.lifetime, 1.0)
        self.assertEqual(particle.color, (0, 255, 0))
        
    def test_invalid_effect_type(self):
        """Test emission with invalid effect type."""
        self.effects.emit('nonexistent', (100, 100), 0)
        self.assertEqual(len(self.effects._particles), 0)

if __name__ == '__main__':
    unittest.main() 