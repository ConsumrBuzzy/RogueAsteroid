"""Tests for game systems."""
import pytest
import pygame
from src.core.game import Game
from src.core.services import HighScoreManager
from src.core.systems import ParticleSystem, Spawner
from src.core.managers import CollisionManager, EntityManager

@pytest.fixture
def game():
    """Create a game instance for testing."""
    return Game()

@pytest.fixture
def particle_system(game):
    """Create a particle system for testing."""
    return ParticleSystem(game)

@pytest.fixture
def spawner(game):
    """Create a spawner system for testing."""
    return Spawner(game)

@pytest.fixture
def collision_manager(game):
    """Create a collision manager for testing."""
    return CollisionManager(game)

@pytest.fixture
def entity_manager(game):
    """Create an entity manager for testing."""
    return EntityManager(game) 