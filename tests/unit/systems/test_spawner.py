"""Unit tests for spawner system."""
import pytest
import numpy as np
from src.core.systems import Spawner
from src.entities.asteroid import Asteroid

@pytest.mark.unit
@pytest.mark.systems
class TestSpawnerSystem:
    """Test cases for the spawner system."""
    
    def test_spawner_initialization(self, mock_spawner):
        """Test spawner initial state."""
        assert mock_spawner.wave == 1
        assert mock_spawner.asteroids_per_wave == 4
        assert mock_spawner.spawn_timer == 0.0
        assert mock_spawner.spawn_delay == 0.5
        assert not mock_spawner.spawning_wave
        assert mock_spawner.asteroids_to_spawn == 0
    
    def test_start_wave(self, mock_spawner):
        """Test starting a new wave."""
        mock_spawner.start_wave()
        
        assert mock_spawner.spawning_wave
        assert mock_spawner.asteroids_to_spawn == mock_spawner.asteroids_per_wave
        assert mock_spawner.spawn_timer == mock_spawner.spawn_delay
    
    def test_wave_progression(self, mock_spawner):
        """Test wave progression mechanics."""
        initial_asteroids = mock_spawner.asteroids_per_wave
        
        # Start and complete first wave
        mock_spawner.start_wave()
        while mock_spawner.spawning_wave:
            mock_spawner.update(mock_spawner.spawn_delay)
        
        # Verify asteroids were spawned
        asteroid_count = sum(
            1 for entity in mock_spawner.game.entities
            if isinstance(entity, Asteroid)
        )
        assert asteroid_count == initial_asteroids
        
        # Advance to next wave
        mock_spawner.advance_wave()
        assert mock_spawner.wave == 2
        assert mock_spawner.asteroids_to_spawn == initial_asteroids + 1
    
    def test_spawn_timing(self, mock_spawner):
        """Test asteroid spawn timing."""
        mock_spawner.start_wave()
        initial_count = len(mock_spawner.game.entities)
        
        # Update just before spawn time
        mock_spawner.update(mock_spawner.spawn_delay - 0.1)
        assert len(mock_spawner.game.entities) == initial_count
        
        # Update past spawn time
        mock_spawner.update(0.2)  # Total time > spawn_delay
        assert len(mock_spawner.game.entities) == initial_count + 1
    
    def test_asteroid_spawn_position(self, mock_spawner):
        """Test asteroid spawn position mechanics."""
        mock_spawner.start_wave()
        mock_spawner.update(mock_spawner.spawn_delay)  # Spawn one asteroid
        
        # Get spawned asteroid
        asteroid = next(
            entity for entity in mock_spawner.game.entities
            if isinstance(entity, Asteroid)
        )
        
        # Check that asteroid spawned on screen edge
        x, y = asteroid.position
        window_width = mock_spawner.game.width
        window_height = mock_spawner.game.height
        
        # Should be on one of the edges
        on_vertical_edge = (x == 0 or x == window_width)
        on_horizontal_edge = (y == 0 or y == window_height)
        assert on_vertical_edge or on_horizontal_edge
    
    def test_asteroid_initial_velocity(self, mock_spawner):
        """Test asteroid initial velocity direction."""
        mock_spawner.start_wave()
        mock_spawner.update(mock_spawner.spawn_delay)  # Spawn one asteroid
        
        # Get spawned asteroid
        asteroid = next(
            entity for entity in mock_spawner.game.entities
            if isinstance(entity, Asteroid)
        )
        
        # Velocity should be non-zero
        assert np.any(asteroid.velocity != 0)
        
        # Calculate direction to center
        center = np.array([mock_spawner.game.width/2, mock_spawner.game.height/2])
        to_center = center - asteroid.position
        to_center_normalized = to_center / np.linalg.norm(to_center)
        
        # Velocity should be roughly towards center (within 45 degrees)
        velocity_normalized = asteroid.velocity / np.linalg.norm(asteroid.velocity)
        dot_product = np.dot(to_center_normalized, velocity_normalized)
        angle = np.arccos(dot_product)
        assert angle <= np.pi/4  # 45 degrees
    
    def test_wave_completion_check(self, mock_spawner):
        """Test wave completion detection."""
        # Start wave but don't spawn asteroids
        mock_spawner.start_wave()
        assert not mock_spawner.check_wave_complete()
        
        # Complete spawning but asteroids still exist
        while mock_spawner.spawning_wave:
            mock_spawner.update(mock_spawner.spawn_delay)
        assert not mock_spawner.check_wave_complete()
        
        # Remove all asteroids
        mock_spawner.game.entities = [
            entity for entity in mock_spawner.game.entities
            if not isinstance(entity, Asteroid)
        ]
        assert mock_spawner.check_wave_complete()
    
    def test_multiple_waves(self, mock_spawner):
        """Test multiple wave progression."""
        initial_asteroids = mock_spawner.asteroids_per_wave
        
        for wave in range(1, 4):
            # Start wave
            mock_spawner.start_wave()
            
            # Complete spawning
            while mock_spawner.spawning_wave:
                mock_spawner.update(mock_spawner.spawn_delay)
            
            # Verify asteroid count
            asteroid_count = sum(
                1 for entity in mock_spawner.game.entities
                if isinstance(entity, Asteroid)
            )
            assert asteroid_count == initial_asteroids + (wave - 1)
            
            # Clear asteroids and advance
            mock_spawner.game.entities.clear()
            mock_spawner.advance_wave()
            assert mock_spawner.wave == wave + 1 