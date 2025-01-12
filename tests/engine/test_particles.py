"""Test suite for particle system."""
import pytest
import pygame
import random
from src.core.game import Game
from src.core.systems.particle import ParticleSystem, Particle
from src.core.constants import *

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.fixture
def particle_system(game):
    """Create a particle system instance."""
    return ParticleSystem(game)

@pytest.mark.engine
class TestParticleSystem:
    """Test cases for the particle system."""
    
    def test_particle_creation(self, game, particle_system):
        """Test creating particles with different properties."""
        # Create test particles
        test_particles = [
            particle_system.create_particle(
                pos=(100, 100),
                velocity=(random.uniform(-1, 1), random.uniform(-1, 1)),
                color=(255, 0, 0),
                size=5,
                lifetime=1.0
            ) for _ in range(10)
        ]
        
        assert len(particle_system.particles) == 10, "All particles should be added to system"
        for particle in test_particles:
            assert isinstance(particle, Particle), "Created object should be a Particle"
            assert particle.lifetime > 0, "Particle should have positive lifetime"
    
    def test_particle_update(self, game, particle_system):
        """Test particle position updates."""
        # Create test particle with known velocity
        particle = particle_system.create_particle(
            pos=(100, 100),
            velocity=(10, 5),
            color=(255, 0, 0),
            size=5,
            lifetime=1.0
        )
        
        # Update one frame
        dt = 1/60
        initial_pos = particle.pos.copy()
        particle_system.update(dt)
        
        # Check position update
        expected_x = initial_pos[0] + particle.velocity[0] * dt
        expected_y = initial_pos[1] + particle.velocity[1] * dt
        assert abs(particle.pos[0] - expected_x) < 0.001, "X position should update correctly"
        assert abs(particle.pos[1] - expected_y) < 0.001, "Y position should update correctly"
    
    def test_particle_lifetime(self, game, particle_system):
        """Test particle lifetime and removal."""
        # Create particles with different lifetimes
        lifetimes = [0.5, 1.0, 1.5]
        for lifetime in lifetimes:
            particle_system.create_particle(
                pos=(100, 100),
                velocity=(0, 0),
                color=(255, 0, 0),
                size=5,
                lifetime=lifetime
            )
        
        assert len(particle_system.particles) == 3, "All particles should be created"
        
        # Update past shortest lifetime
        particle_system.update(0.6)
        assert len(particle_system.particles) == 2, "Shortest lifetime particle should be removed"
        
        # Update past medium lifetime
        particle_system.update(0.5)
        assert len(particle_system.particles) == 1, "Medium lifetime particle should be removed"
        
        # Update past longest lifetime
        particle_system.update(0.5)
        assert len(particle_system.particles) == 0, "All particles should be removed"
    
    def test_particle_color_fade(self, game, particle_system):
        """Test particle color fading over lifetime."""
        # Create particle with color fade
        initial_color = (255, 0, 0)
        particle = particle_system.create_particle(
            pos=(100, 100),
            velocity=(0, 0),
            color=initial_color,
            size=5,
            lifetime=1.0,
            fade=True
        )
        
        # Update halfway through lifetime
        particle_system.update(0.5)
        
        # Check color components have faded
        for i in range(3):
            assert particle.color[i] < initial_color[i], f"Color component {i} should fade"
    
    def test_particle_size_change(self, game, particle_system):
        """Test particle size changes over lifetime."""
        # Create particle with size change
        initial_size = 10
        particle = particle_system.create_particle(
            pos=(100, 100),
            velocity=(0, 0),
            color=(255, 0, 0),
            size=initial_size,
            lifetime=1.0,
            size_change=-5  # Shrink by 5 over lifetime
        )
        
        # Update halfway through lifetime
        particle_system.update(0.5)
        
        # Check size has changed
        expected_size = initial_size + (particle.size_change * 0.5)
        assert abs(particle.size - expected_size) < 0.001, "Size should change linearly"
    
    def test_particle_acceleration(self, game, particle_system):
        """Test particle acceleration."""
        # Create particle with acceleration
        particle = particle_system.create_particle(
            pos=(100, 100),
            velocity=(0, 0),
            acceleration=(0, 10),  # Accelerate downward
            color=(255, 0, 0),
            size=5,
            lifetime=1.0
        )
        
        # Update and check velocity changes
        dt = 1/60
        initial_velocity = particle.velocity[1]
        particle_system.update(dt)
        
        assert particle.velocity[1] > initial_velocity, "Velocity should increase with acceleration"
    
    def test_particle_emission(self, game, particle_system):
        """Test particle emission patterns."""
        # Test circular emission
        num_particles = 8
        particle_system.emit_circular(
            center=(100, 100),
            speed=10,
            color=(255, 0, 0),
            size=5,
            lifetime=1.0,
            count=num_particles
        )
        
        assert len(particle_system.particles) == num_particles, "All particles should be emitted"
        
        # Check particles are distributed in a circle
        angles = set()
        for particle in particle_system.particles:
            angle = pygame.math.Vector2(particle.velocity).angle_to((1, 0))
            angles.add(round(angle, 2))
        
        assert len(angles) == num_particles, "Particles should have unique angles"
    
    def test_particle_system_clear(self, game, particle_system):
        """Test clearing all particles from the system."""
        # Create some particles
        for _ in range(5):
            particle_system.create_particle(
                pos=(100, 100),
                velocity=(0, 0),
                color=(255, 0, 0),
                size=5,
                lifetime=1.0
            )
        
        assert len(particle_system.particles) > 0, "Particles should be created"
        
        # Clear system
        particle_system.clear()
        assert len(particle_system.particles) == 0, "All particles should be removed"
    
    def test_particle_system_pause(self, game, particle_system):
        """Test pausing particle system updates."""
        # Create test particle
        particle = particle_system.create_particle(
            pos=(100, 100),
            velocity=(10, 0),
            color=(255, 0, 0),
            size=5,
            lifetime=1.0
        )
        
        # Pause system and update
        particle_system.paused = True
        initial_pos = particle.pos.copy()
        initial_lifetime = particle.lifetime
        
        particle_system.update(1/60)
        
        # Check nothing changed while paused
        assert particle.pos == initial_pos, "Position should not change while paused"
        assert particle.lifetime == initial_lifetime, "Lifetime should not change while paused" 