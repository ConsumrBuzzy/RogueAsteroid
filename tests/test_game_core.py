"""Test suite for core game mechanics."""
import pytest
import pygame
import numpy as np
from src.core.game import Game
from src.entities.ship import Ship
from src.entities.asteroid import Asteroid
from src.core.constants import WINDOW_WIDTH, WINDOW_HEIGHT

@pytest.fixture
def game():
    """Fixture to create a game instance for testing."""
    pygame.init()
    game = Game()
    yield game
    pygame.quit()

@pytest.fixture
def ship(game):
    """Fixture to create a ship instance for testing."""
    return Ship(game)

@pytest.fixture
def asteroid():
    """Fixture to create an asteroid instance for testing."""
    return Asteroid(x=100, y=100, size='large')

class TestGameInitialization:
    def test_game_init(self, game):
        """Test game initialization."""
        assert game is not None
        assert game.width == WINDOW_WIDTH
        assert game.height == WINDOW_HEIGHT
        assert game.lives > 0
        assert game.level == 1
        assert game.running is True

    def test_game_screen_setup(self, game):
        """Test game screen initialization."""
        assert game.screen is not None
        assert game.screen.get_width() == WINDOW_WIDTH
        assert game.screen.get_height() == WINDOW_HEIGHT

class TestShipMechanics:
    def test_ship_movement(self, ship):
        """Test ship movement mechanics."""
        initial_pos = np.array([ship.x, ship.y])
        ship.thrust = True
        ship.update(0.016)  # Simulate one frame at 60 FPS
        new_pos = np.array([ship.x, ship.y])
        assert not np.array_equal(initial_pos, new_pos)

    def test_ship_rotation(self, ship):
        """Test ship rotation."""
        initial_angle = ship.angle
        ship.rotating_right = True
        ship.update(0.016)
        assert ship.angle != initial_angle

    def test_ship_wrapping(self, ship):
        """Test screen wrapping for ship."""
        ship.x = WINDOW_WIDTH + 10
        ship.y = WINDOW_HEIGHT + 10
        ship.update(0.016)
        assert ship.x < WINDOW_WIDTH
        assert ship.y < WINDOW_HEIGHT

class TestAsteroidMechanics:
    def test_asteroid_movement(self, asteroid):
        """Test asteroid movement."""
        initial_pos = (asteroid.x, asteroid.y)
        asteroid.update(0.016)
        current_pos = (asteroid.x, asteroid.y)
        assert initial_pos != current_pos

    def test_asteroid_splitting(self, asteroid):
        """Test asteroid splitting mechanics."""
        assert asteroid.size == 'large'
        new_asteroids = asteroid.split()
        assert len(new_asteroids) > 0
        assert all(a.size == 'medium' for a in new_asteroids)

    def test_asteroid_wrapping(self, asteroid):
        """Test screen wrapping for asteroids."""
        asteroid.x = WINDOW_WIDTH + 10
        asteroid.y = WINDOW_HEIGHT + 10
        asteroid.update(0.016)
        assert asteroid.x < WINDOW_WIDTH
        assert asteroid.y < WINDOW_HEIGHT

class TestCollisions:
    def test_ship_asteroid_collision(self, ship, asteroid):
        """Test collision detection between ship and asteroid."""
        # Position ship and asteroid at same location
        ship.x = asteroid.x
        ship.y = asteroid.y
        assert ship.collides_with(asteroid)

    def test_no_collision_when_distant(self, ship, asteroid):
        """Test that distant objects don't collide."""
        ship.x = 0
        ship.y = 0
        asteroid.x = WINDOW_WIDTH
        asteroid.y = WINDOW_HEIGHT
        assert not ship.collides_with(asteroid)

class TestGameProgression:
    def test_level_progression(self, game):
        """Test level progression mechanics."""
        initial_level = game.level
        # Simulate clearing all asteroids
        game.asteroids.clear()
        game.update(0.016)  # Update game state
        assert game.level == initial_level + 1

    def test_score_system(self, game):
        """Test scoring system."""
        initial_score = game.scoring.get_score()
        game.scoring.add_score(100)
        assert game.scoring.get_score() == initial_score + 100

    def test_lives_system(self, game):
        """Test lives system."""
        initial_lives = game.lives
        game.lives -= 1
        assert game.lives == initial_lives - 1
