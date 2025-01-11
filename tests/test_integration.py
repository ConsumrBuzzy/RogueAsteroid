"""Integration tests for game systems."""
import unittest
import pygame
import numpy as np
from src.core.game import Game, GameState
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet

class TestGameIntegration(unittest.TestCase):
    """Integration tests for game systems."""
    
    def setUp(self):
        """Set up test environment."""
        self.game = Game()
        pygame.init()
    
    def tearDown(self):
        """Clean up after tests."""
        pygame.quit()
    
    def test_game_initialization(self):
        """Test game system initialization."""
        self.assertEqual(self.game.state, GameState.MENU)
        self.assertEqual(len(self.game.entities), 0)
        self.assertEqual(self.game.score, 0)
        self.assertTrue(self.game.high_scores is not None)
    
    def test_game_reset(self):
        """Test game reset functionality."""
        # Start with some entities and score
        self.game.entities.append(Ship(self.game))
        self.game.score = 1000
        
        # Reset game
        self.game.reset_game()
        
        # Check reset state
        self.assertGreater(len(self.game.entities), 0)  # Should have ship and asteroids
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.lives, self.game.INITIAL_LIVES)
        self.assertTrue(any(isinstance(e, Ship) for e in self.game.entities))
        self.assertTrue(any(isinstance(e, Asteroid) for e in self.game.entities))
    
    def test_collision_system(self):
        """Test collision detection and response."""
        # Create ship and asteroid at same position
        ship = Ship(self.game)
        asteroid = Asteroid(self.game, 
                          ship.get_component('transform').position[0],
                          ship.get_component('transform').position[1],
                          'large')
        
        self.game.entities.extend([ship, asteroid])
        self.game.asteroids.append(asteroid)
        self.game.ship = ship
        self.game.state = GameState.PLAYING
        
        # Update game to trigger collision
        self.game.handle_collisions()
        
        # Check collision response
        self.assertEqual(self.game.lives, self.game.INITIAL_LIVES - 1)
        self.assertNotIn(ship, self.game.entities)
    
    def test_asteroid_destruction(self):
        """Test asteroid destruction and splitting."""
        # Create bullet and asteroid
        asteroid = Asteroid(self.game, 400, 300, 'large')
        transform = asteroid.get_component('transform')
        
        bullet = Bullet(self.game, 
                       transform.position[0],
                       transform.position[1],
                       np.array([1.0, 0.0]))
        
        self.game.entities.extend([asteroid, bullet])
        self.game.asteroids.append(asteroid)
        
        # Update to trigger collision
        bullet.update(0.016)
        
        # Check asteroid splitting
        self.assertNotIn(asteroid, self.game.entities)
        self.assertTrue(any(a.size_category == 'medium' for a in self.game.asteroids))
    
    def test_level_progression(self):
        """Test level progression system."""
        self.game.reset_game()
        initial_asteroids = len(self.game.asteroids)
        
        # Clear all asteroids
        self.game.asteroids.clear()
        self.game.entities = [e for e in self.game.entities if not isinstance(e, Asteroid)]
        
        # Update game to trigger next level
        self.game.update()
        
        # Check new level
        self.assertEqual(self.game.level, 2)
        self.assertGreater(len(self.game.asteroids), initial_asteroids)
    
    def test_high_score_system(self):
        """Test high score system integration."""
        test_score = 10000
        test_name = "TEST"
        
        # Set a high score
        self.game.score = test_score
        self.game.state = GameState.GAME_OVER
        
        # Check high score detection
        self.assertTrue(self.game.high_scores.is_high_score(test_score))
        
        # Add score
        self.game.high_scores.add_score(test_score, test_name)
        
        # Verify score was saved
        scores = self.game.high_scores.get_scores()
        self.assertTrue(any(s.score == test_score and s.name == test_name 
                          for s in scores))
    
    def test_menu_system(self):
        """Test menu system integration."""
        # Test main menu
        self.game.state = GameState.MENU
        self.game.main_menu._start_game()
        self.assertEqual(self.game.state, GameState.PLAYING)
        
        # Test options menu
        self.game.state = GameState.MENU
        self.game.main_menu._show_options()
        self.assertEqual(self.game.state, GameState.OPTIONS)
        
        # Test control scheme toggle
        initial_scheme = self.game.settings['controls']['scheme']
        self.game.options_menu._toggle_controls()
        self.assertNotEqual(self.game.settings['controls']['scheme'], initial_scheme)
    
    def test_game_over_sequence(self):
        """Test game over sequence."""
        self.game.reset_game()
        self.game.state = GameState.PLAYING
        
        # Deplete lives
        while self.game.lives > 0:
            self.game.lives -= 1
            self.game.handle_collisions()
        
        # Check game over state
        self.assertEqual(self.game.state, GameState.GAME_OVER)
        
        # If it's a high score, should transition to new high score state
        if self.game.high_scores.is_high_score(self.game.score):
            self.assertEqual(self.game.state, GameState.NEW_HIGH_SCORE)

if __name__ == '__main__':
    unittest.main() 