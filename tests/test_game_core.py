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
def asteroid(game):
    """Fixture to create an asteroid instance for testing."""
    position = pygame.Vector2(100, 100)
    return Asteroid(game, 'large', position)

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
        transform = ship.get_component('transform')
        physics = ship.get_component('physics')
        initial_pos = pygame.Vector2(transform.position)
        physics.velocity = pygame.Vector2(10, 10)
        ship.update(0.016)  # Simulate one frame at 60 FPS
        new_pos = pygame.Vector2(transform.position)
        assert new_pos != initial_pos

    def test_ship_rotation(self, ship):
        """Test ship rotation."""
        transform = ship.get_component('transform')
        initial_angle = transform.rotation
        ship.rotating_right = True
        ship.update(0.016)
        assert transform.rotation != initial_angle

    def test_ship_wrapping(self, ship):
        """Test screen wrapping for ship."""
        transform = ship.get_component('transform')
        screen_wrap = ship.get_component('screen_wrap')
        transform.position = pygame.Vector2(WINDOW_WIDTH + 10, WINDOW_HEIGHT + 10)
        screen_wrap.update()
        assert transform.position.x < WINDOW_WIDTH
        assert transform.position.y < WINDOW_HEIGHT

class TestAsteroidMechanics:
    def test_asteroid_movement(self, asteroid):
        """Test asteroid movement."""
        transform = asteroid.get_component('transform')
        physics = asteroid.get_component('physics')
        initial_pos = pygame.Vector2(transform.position)
        physics.velocity = pygame.Vector2(10, 10)
        asteroid.update(0.016)
        current_pos = pygame.Vector2(transform.position)
        assert initial_pos != current_pos

    def test_asteroid_splitting(self, game):
        """Test asteroid splitting mechanics."""
        position = pygame.Vector2(100, 100)
        asteroid = Asteroid(game, 'large', position)
        assert asteroid.size == 'large'
        new_asteroids = asteroid.split()
        assert len(new_asteroids) > 0
        assert all(a.size == 'medium' for a in new_asteroids)

    def test_asteroid_wrapping(self, asteroid):
        """Test screen wrapping for asteroids."""
        transform = asteroid.get_component('transform')
        screen_wrap = asteroid.get_component('screen_wrap')
        transform.position = pygame.Vector2(WINDOW_WIDTH + 10, WINDOW_HEIGHT + 10)
        screen_wrap.update()
        assert transform.position.x < WINDOW_WIDTH
        assert transform.position.y < WINDOW_HEIGHT

class TestCollisions:
    def test_ship_asteroid_collision(self, game):
        """Test collision detection between ship and asteroid."""
        ship = Ship(game)
        position = pygame.Vector2(100, 100)
        asteroid = Asteroid(game, 'large', position)
        
        ship_transform = ship.get_component('transform')
        ship_collision = ship.get_component('collision')
        asteroid_transform = asteroid.get_component('transform')
        asteroid_collision = asteroid.get_component('collision')
        
        # Position ship and asteroid at same location
        ship_transform.position = pygame.Vector2(asteroid_transform.position)
        
        assert ship_collision.check_collision(asteroid_collision)

    def test_no_collision_when_distant(self, game):
        """Test that distant objects don't collide."""
        ship = Ship(game)
        position = pygame.Vector2(WINDOW_WIDTH, WINDOW_HEIGHT)
        asteroid = Asteroid(game, 'large', position)
        
        ship_transform = ship.get_component('transform')
        ship_collision = ship.get_component('collision')
        asteroid_collision = asteroid.get_component('collision')
        
        ship_transform.position = pygame.Vector2(0, 0)
        
        assert not ship_collision.check_collision(asteroid_collision)

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
        initial_score = game.score
        game.add_score(100)
        assert game.score == initial_score + 100

    def test_lives_system(self, game):
        """Test lives system."""
        initial_lives = game.lives
        game.lives -= 1
        assert game.lives == initial_lives - 1
