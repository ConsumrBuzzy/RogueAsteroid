"""Test suite for particle effects system."""
import pytest
import pygame
from src.core.game import Game
from src.core.constants import *

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.fixture
def particle_setup(game):
    """Setup a fresh game state for particle testing."""
    game.new_game()
    return game

@pytest.mark.engine
class TestParticleSystem:
    """Test cases for the particle effects system."""
    
    def test_particle_creation(self, game, particle_setup):
        """Test basic particle creation."""
        initial_count = len(game.particles)
        
        # Create test particles
        position = pygame.Vector2(400, 300)
        velocity = pygame.Vector2(1, 0)
        color = (255, 0, 0)
        lifetime = 1.0
        
        game.create_particle(position, velocity, color, lifetime)
        
        assert len(game.particles) == initial_count + 1, "Particle should be added to system"
        particle = game.particles[-1]
        assert pygame.Vector2(particle['position']) == position, "Particle should have correct position"
        assert pygame.Vector2(particle['velocity']) == velocity, "Particle should have correct velocity"
        assert particle['color'] == color, "Particle should have correct color"
        assert particle['lifetime'] == lifetime, "Particle should have correct lifetime"
    
    def test_particle_update(self, game, particle_setup):
        """Test particle movement and lifetime."""
        # Create test particle
        position = pygame.Vector2(400, 300)
        velocity = pygame.Vector2(100, 0)  # 100 pixels per second
        game.create_particle(position, velocity, (255, 0, 0), 1.0)
        
        # Update for one frame
        dt = 1/60
        game.update(dt)
        
        # Verify position update
        particle = game.particles[0]
        expected_pos = position + velocity * dt
        actual_pos = pygame.Vector2(particle['position'])
        assert (actual_pos - expected_pos).length() < 0.1, "Particle should move according to velocity"
        
        # Verify lifetime update
        assert particle['lifetime'] < 1.0, "Particle lifetime should decrease"
    
    def test_particle_cleanup(self, game, particle_setup):
        """Test particle removal after lifetime expires."""
        # Create particles with different lifetimes
        lifetimes = [0.1, 0.2, 0.3]
        for lifetime in lifetimes:
            game.create_particle(
                pygame.Vector2(400, 300),
                pygame.Vector2(0, 0),
                (255, 0, 0),
                lifetime
            )
        
        initial_count = len(game.particles)
        
        # Update until first particle should be removed
        for _ in range(int(0.15 * 60)):  # 0.15 seconds at 60 FPS
            game.update(1/60)
        
        assert len(game.particles) < initial_count, "Expired particles should be removed"
        
        # Update until all particles should be removed
        for _ in range(int(0.3 * 60)):  # Another 0.3 seconds
            game.update(1/60)
        
        assert len(game.particles) == 0, "All particles should be removed after expiration"
    
    def test_explosion_effect(self, game, particle_setup):
        """Test explosion particle effect."""
        position = pygame.Vector2(400, 300)
        initial_count = len(game.particles)
        
        # Create explosion
        game.create_explosion(position.x, position.y)
        
        # Verify particle creation
        assert len(game.particles) > initial_count, "Explosion should create multiple particles"
        
        # Verify particle properties
        for particle in game.particles:
            pos = pygame.Vector2(particle['position'])
            assert (pos - position).length() < 1.0, "Particles should start at explosion center"
            assert 'velocity' in particle, "Particles should have velocity"
            assert 'color' in particle, "Particles should have color"
            assert particle['lifetime'] > 0, "Particles should have positive lifetime"
    
    def test_thrust_effect(self, game, particle_setup):
        """Test ship thrust particle effect."""
        # Verify ship exists
        assert game.ship is not None, "Ship should exist for thrust test"
        
        initial_count = len(game.particles)
        
        # Create thrust effect
        game.ship.create_thrust_particles()
        
        # Verify particle creation
        assert len(game.particles) > initial_count, "Thrust should create particles"
        
        # Get ship position and rotation
        ship_transform = game.ship.get_component('transform')
        ship_pos = ship_transform.position
        ship_rot = ship_transform.rotation
        
        # Verify particle properties
        for particle in game.particles[initial_count:]:  # Only check new particles
            pos = pygame.Vector2(particle['position'])
            # Particles should start near ship's rear
            distance = (pos - ship_pos).length()
            assert distance < 20, "Thrust particles should start near ship"
            
            # Verify particle color is appropriate for thrust
            assert all(0 <= c <= 255 for c in particle['color']), "Color values should be valid"
    
    def test_particle_color_interpolation(self, game, particle_setup):
        """Test particle color changes over lifetime."""
        # Create particle with color transition
        start_color = (255, 0, 0)
        end_color = (0, 0, 255)
        lifetime = 1.0
        
        game.create_particle_with_color_transition(
            pygame.Vector2(400, 300),
            pygame.Vector2(0, 0),
            start_color,
            end_color,
            lifetime
        )
        
        # Get initial color
        initial_color = game.particles[0]['color']
        assert initial_color == start_color, "Particle should start with initial color"
        
        # Update halfway through lifetime
        for _ in range(int(lifetime * 0.5 * 60)):  # Half lifetime at 60 FPS
            game.update(1/60)
        
        # Check intermediate color
        mid_color = game.particles[0]['color']
        assert all(s <= m <= e for s, m, e in zip(start_color, mid_color, end_color)), \
            "Color should interpolate between start and end colors" 