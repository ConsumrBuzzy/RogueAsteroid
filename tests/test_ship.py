"""Unit tests for ship entity and components."""
import os
import sys
import unittest
import pygame

# Add project root to Python path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, project_root)

from src.entities.ship import Ship
from src.core.entities.base import (
    Entity,
    TransformComponent,
    RenderComponent,
    CollisionComponent
)
from src.core.components.effect import EffectComponent

class MockGame:
    """Mock game class for testing."""
    def __init__(self):
        pygame.init()
        self.width = 800
        self.height = 600
        self.dt = 0.016  # 60 FPS
        self.screen = pygame.Surface((self.width, self.height))

class TestShip(unittest.TestCase):
    """Test cases for Ship entity."""
    
    def setUp(self):
        """Set up test environment."""
        self.game = MockGame()
        self.ship = None
    
    def tearDown(self):
        """Clean up test environment."""
        if self.ship:
            self.ship.destroy()
        pygame.quit()
    
    def test_ship_initialization(self):
        """Test successful ship initialization."""
        self.ship = Ship(self.game)
        
        # Verify required components
        self.assertIsNotNone(self.ship.get_component(TransformComponent))
        self.assertIsNotNone(self.ship.get_component(RenderComponent))
        self.assertIsNotNone(self.ship.get_component(CollisionComponent))
        self.assertIsNotNone(self.ship.get_component(EffectComponent))
    
    def test_ship_missing_transform(self):
        """Test ship initialization with missing transform component."""
        self.ship = Ship(self.game)
        transform = self.ship.get_component(TransformComponent)
        self.ship.remove_component(transform)
        
        with self.assertRaises(RuntimeError) as context:
            self.ship.initialize()
        self.assertIn("Missing required component", str(context.exception))
    
    def test_ship_missing_render(self):
        """Test ship initialization with missing render component."""
        self.ship = Ship(self.game)
        render = self.ship.get_component(RenderComponent)
        self.ship.remove_component(render)
        
        with self.assertRaises(RuntimeError) as context:
            self.ship.initialize()
        self.assertIn("Missing required component", str(context.exception))
    
    def test_ship_missing_collision(self):
        """Test ship initialization with missing collision component."""
        self.ship = Ship(self.game)
        collision = self.ship.get_component(CollisionComponent)
        self.ship.remove_component(collision)
        
        with self.assertRaises(RuntimeError) as context:
            self.ship.initialize()
        self.assertIn("Missing required component", str(context.exception))
    
    def test_ship_missing_effect(self):
        """Test ship initialization with missing effect component."""
        self.ship = Ship(self.game)
        effect = self.ship.get_component(EffectComponent)
        self.ship.remove_component(effect)
        
        with self.assertRaises(RuntimeError) as context:
            self.ship.initialize()
        self.assertIn("Missing required component", str(context.exception))
    
    def test_ship_component_order(self):
        """Test ship component initialization order."""
        self.ship = Ship(self.game)
        
        # Components should be initialized in specific order
        components = self.ship.components
        transform_idx = next(i for i, c in enumerate(components) if isinstance(c, TransformComponent))
        render_idx = next(i for i, c in enumerate(components) if isinstance(c, RenderComponent))
        collision_idx = next(i for i, c in enumerate(components) if isinstance(c, CollisionComponent))
        effect_idx = next(i for i, c in enumerate(components) if isinstance(c, EffectComponent))
        
        # Transform should be first
        self.assertEqual(transform_idx, 0)
        # Render should be before Effect
        self.assertLess(render_idx, effect_idx)
        # Collision should be before Effect
        self.assertLess(collision_idx, effect_idx)

if __name__ == '__main__':
    unittest.main() 