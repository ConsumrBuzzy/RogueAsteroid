"""Integration tests for game systems."""
import unittest
from src.core.game import Game
from src.core.game_state import GameState
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
import pygame

class TestGameIntegration(unittest.TestCase):
    """Test cases for game system integration."""
    
    def setUp(self):
        self.game = Game()
    
    def test_game_initialization(self):
        """Test game initialization."""
        self.assertIsNone(self.game.ship)
        self.assertEqual(len(self.game.entities), 0)
        self.assertEqual(len(self.game.asteroids), 0)
        self.assertEqual(len(self.game.bullets), 0)
        self.assertEqual(self.game.state, GameState.MAIN_MENU)
    
    def test_game_reset(self):
        """Test game reset functionality."""
        # Add some score
        self.game.score = 1000
        
        # Reset game
        self.game.reset_game()
        
        # Check reset state
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.level, 1)
        self.assertEqual(self.game.lives, 3)
        self.assertIsNotNone(self.game.ship)
        self.assertGreater(len(self.game.asteroids), 0)
        self.assertEqual(self.game.state, GameState.PLAYING)
    
    def test_collision_system(self):
        """Test collision detection between entities."""
        self.game.reset_game()
        
        # Get ship position
        ship_transform = self.game.ship.get_component('transform')
        self.assertIsNotNone(ship_transform)
        
        # Create asteroid near ship
        asteroid = Asteroid(
            self.game,
            'large',
            pygame.Vector2(
                ship_transform.position.x + 10,  # Very close to ship
                ship_transform.position.y
            )
        )
        self.game.asteroids.append(asteroid)
        self.game.entities.append(asteroid)
        
        # Update game to trigger collision
        self.game.update(0.016)  # One frame at 60 FPS
        
        # Ship should be destroyed and life lost
        self.assertIsNone(self.game.ship)
        self.assertEqual(self.game.lives, 2)
    
    def test_level_progression(self):
        """Test level progression mechanics."""
        self.game.reset_game()
        initial_level = self.game.level
        
        # Clear all asteroids to trigger level completion
        self.game.asteroids.clear()
        
        # Update game
        self.game.update(0.016)
        
        # Level should increase
        self.assertEqual(self.game.level, initial_level + 1)
        self.assertGreater(len(self.game.asteroids), 0)  # New asteroids spawned
    
    def test_high_score_system(self):
        """Test high score system."""
        test_score = 10000
        self.game.scoring_system.current_score = test_score
        
        # Check if score is high score
        self.assertTrue(self.game.scoring_system.check_high_score())
        
        # Add high score
        self.assertTrue(self.game.scoring_system.add_high_score("TEST", 1))
        
        # Verify score was added
        scores = self.game.scoring_system.get_high_scores()
        self.assertIn(test_score, [score.score for score in scores])
    
    def test_menu_system(self):
        """Test menu system state changes."""
        # Start in main menu
        self.assertEqual(self.game.state, GameState.MAIN_MENU)
        
        # Start game
        self.game.state = GameState.PLAYING
        self.assertEqual(self.game.state, GameState.PLAYING)
        
        # Pause game
        self.game.state = GameState.PAUSED
        self.assertEqual(self.game.state, GameState.PAUSED)
        
        # Resume game
        self.game.state = GameState.PLAYING
        self.assertEqual(self.game.state, GameState.PLAYING)
        
        # Game over
        self.game.state = GameState.GAME_OVER
        self.assertEqual(self.game.state, GameState.GAME_OVER)
    
    def test_game_over_sequence(self):
        """Test game over sequence."""
        self.game.reset_game()
        
        # Set lives to 1
        self.game.lives = 1
        
        # Create asteroid near ship
        ship_transform = self.game.ship.get_component('transform')
        self.assertIsNotNone(ship_transform)
        
        asteroid = Asteroid(
            self.game,
            'large',
            pygame.Vector2(
                ship_transform.position.x + 10,
                ship_transform.position.y
            )
        )
        self.game.asteroids.append(asteroid)
        self.game.entities.append(asteroid)
        
        # Update game to trigger collision and game over
        self.game.update(0.016)
        
        # Game should be over
        self.assertEqual(self.game.state, GameState.GAME_OVER)
        self.assertEqual(self.game.lives, 0)
        self.assertIsNone(self.game.ship)

if __name__ == '__main__':
    unittest.main() 