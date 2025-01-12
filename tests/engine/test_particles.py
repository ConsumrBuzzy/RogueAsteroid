"""Test suite for particle system."""
import pytest
import pygame
import numpy as np
from src.core.game import Game
from src.core.constants import THRUST_PARTICLES, EXPLOSION_PARTICLES

@pytest.fixture(scope="session", autouse=True)
def pygame_init():
    """Initialize pygame for all tests."""
    pygame.init()
    if not pygame.font.get_init():
        pygame.font.init()
    if not pygame.display.get_init():
        pygame.display.init()
    yield
    pygame.quit()

@pytest.fixture
def game():
    """Create a game instance for testing."""
    game = Game()
    yield game
    # Clean up game resources
    if hasattr(game, 'screen'):
        pygame.display.quit()

class TestParticleEffects:
    def test_thrust_particle_creation(self, game):
        """Test that thrust particles are created."""
        game.new_game()
        assert game.ship is not None
        initial_particles = len(game.particles)
        game.ship.create_thrust_particles()
        assert len(game.particles) > initial_particles
        
        # Verify particle properties
        for particle in game.particles[initial_particles:]:
            assert 'position' in particle
            assert 'velocity' in particle
            assert 'lifetime' in particle
            assert THRUST_PARTICLES['lifetime_range'][0] <= particle['lifetime'] <= THRUST_PARTICLES['lifetime_range'][1]

    def test_thrust_particle_input(self, game):
        """Test that thrust particles are created when UP key is pressed."""
        game.new_game()
        input_comp = game.ship.get_component('input')
        assert input_comp is not None
        
        # Simulate thrust key press
        input_comp.handle_keydown(pygame.K_UP)
        assert pygame.K_UP in input_comp.active_keys
        
        # Update a few frames
        initial_particles = len(game.particles)
        for _ in range(5):
            game.update(1/60)
        assert len(game.particles) > initial_particles

    def test_thrust_particle_cleanup(self, game):
        """Test that thrust particles are removed after lifetime expires."""
        game.new_game()
        game.ship.create_thrust_particles()
        initial_particles = len(game.particles)
        assert initial_particles > 0
        
        # Update long enough for particles to expire
        total_time = 0.5  # Most thrust particles live 0.1-0.3 seconds
        for _ in range(int(total_time * 60)):  # 60 FPS
            game.update(1/60)
        assert len(game.particles) < initial_particles
        
    def test_explosion_particle_creation(self, game):
        """Test that explosion creates correct number of particles."""
        game.new_game()
        initial_particles = len(game.particles)
        game.create_explosion(400, 300)
        new_particles = len(game.particles) - initial_particles
        assert 8 <= new_particles <= 12  # From create_explosion method
        
        # Verify particle properties
        for particle in game.particles[initial_particles:]:
            assert 'position' in particle
            assert 'velocity' in particle
            assert 'lifetime' in particle
            velocity = np.array(particle['velocity'])
            speed = np.linalg.norm(velocity)
            assert 50 <= speed <= 150  # From create_explosion method
        
    def test_explosion_particle_cleanup(self, game):
        """Test that explosion particles are removed after lifetime expires."""
        game.new_game()
        game.create_explosion(400, 300)
        initial_particles = len(game.particles)
        assert initial_particles > 0
        
        # Update long enough for particles to expire
        total_time = 1.5  # Most explosion particles live 0.5-1.0 seconds
        for _ in range(int(total_time * 60)):  # 60 FPS
            game.update(1/60)
        assert len(game.particles) == 0

    def test_particle_velocity(self, game):
        """Test that particles move according to their velocity."""
        game.new_game()
        test_pos = pygame.Vector2(400, 300)
        game.create_explosion(test_pos.x, test_pos.y)
        
        # Get initial positions
        initial_positions = [pygame.Vector2(p['position']) for p in game.particles]
        
        # Update one frame
        dt = 1/60
        game.update(dt)
        
        # Verify particles have moved according to their velocity
        for i, particle in enumerate(game.particles):
            current_pos = pygame.Vector2(particle['position'])
            velocity = pygame.Vector2(particle['velocity'])
            expected_pos = initial_positions[i] + velocity * dt
            assert np.allclose(current_pos, expected_pos, atol=0.001)

    def test_particle_color(self, game):
        """Test that particles maintain their color."""
        game.new_game()
        game.create_explosion(400, 300)
        for particle in game.particles:
            assert 'color' in particle
            assert len(particle['color']) == 3  # RGB tuple
            assert all(0 <= c <= 255 for c in particle['color'])
            
    def test_particle_screen_wrapping(self, game):
        """Test that particles do not wrap around screen."""
        game.new_game()
        # Create explosion at screen edge
        game.create_explosion(0, 0)
        initial_count = len(game.particles)
        
        # Update until particles move off screen
        for _ in range(60):  # 1 second at 60 FPS
            game.update(1/60)
            # Particles should gradually disappear as they move off screen
            assert len(game.particles) <= initial_count 