"""Common test fixtures and configuration."""
import os
import pytest
import pygame
import tempfile
from typing import Generator
from pathlib import Path

# Initialize pygame for tests that need it
pygame.init()

@pytest.fixture(scope="session")
def screen():
    """Create a pygame screen for tests."""
    return pygame.display.set_mode((800, 600))

@pytest.fixture
def temp_data_dir() -> Generator[Path, None, None]:
    """Create a temporary directory for test data files."""
    with tempfile.TemporaryDirectory() as temp_dir:
        yield Path(temp_dir)

@pytest.fixture
def mock_game(screen):
    """Create a mock game instance for testing."""
    from src.core.game import Game
    game = Game()
    game.screen = screen
    return game

@pytest.fixture
def mock_audio():
    """Create a mock audio manager for testing."""
    from src.core.services import AudioManager
    audio = AudioManager()
    # Disable actual sound playing in tests
    audio.play_sound = lambda *args, **kwargs: None
    return audio

@pytest.fixture
def mock_scoring(temp_data_dir):
    """Create a mock scoring system for testing."""
    from src.core.services import ScoringSystem
    save_file = temp_data_dir / "test_scores.json"
    return ScoringSystem(str(save_file))

@pytest.fixture
def mock_particle_system(mock_game):
    """Create a mock particle system for testing."""
    from src.core.systems import ParticleSystem
    return ParticleSystem(mock_game)

@pytest.fixture
def mock_spawner(mock_game):
    """Create a mock spawner system for testing."""
    from src.core.systems import Spawner
    return Spawner(mock_game)

def pytest_configure(config):
    """Configure test environment."""
    # Add custom markers
    config.addinivalue_line("markers", "services: Tests for core game services")
    config.addinivalue_line("markers", "systems: Tests for game systems")
    config.addinivalue_line("markers", "entities: Tests for game entities")
    config.addinivalue_line("markers", "ui: Tests for user interface components")
    config.addinivalue_line("markers", "integration: Tests for component integration")
    config.addinivalue_line("markers", "performance: Tests for performance benchmarks") 