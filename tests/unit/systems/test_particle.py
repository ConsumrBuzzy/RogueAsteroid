"""Unit tests for particle system."""
import pytest
import pygame
from src.core.systems import ParticleSystem

@pytest.mark.unit
@pytest.mark.systems
class TestParticleSystem:
    """Test cases for the particle system."""
    
    def test_particle_creation(self, mock_particle_system):
        """Test creating individual particles."""
        pos = (100, 100)
        velocity = (10, 10)
        color = (255, 0, 0)
        size = 2.0
        lifetime = 1.0
        
        particle = mock_particle_system.create_particle(
            pos=pos,
            velocity=velocity,
            color=color,
            size=size,
            lifetime=lifetime
        )
        
        assert len(mock_particle_system.particles) == 1
        assert particle.pos == pygame.Vector2(pos)
        assert particle.velocity == pygame.Vector2(velocity)
        assert particle.color == list(color)
        assert particle.size == size
        assert particle.lifetime == lifetime
    
    def test_particle_update(self, mock_particle_system):
        """Test particle movement and lifetime."""
        pos = (100, 100)
        velocity = (10, 10)
        lifetime = 1.0
        
        mock_particle_system.create_particle(
            pos=pos,
            velocity=velocity,
            color=(255, 0, 0),
            size=2.0,
            lifetime=lifetime
        )
        
        # Update half the lifetime
        dt = 0.5
        mock_particle_system.update(dt)
        particle = mock_particle_system.particles[0]
        
        # Check position update
        expected_pos = pygame.Vector2(pos) + pygame.Vector2(velocity) * dt
        assert particle.pos.x == pytest.approx(expected_pos.x)
        assert particle.pos.y == pytest.approx(expected_pos.y)
        
        # Check lifetime update
        assert particle.lifetime == pytest.approx(lifetime - dt)
        
        # Update remaining lifetime
        mock_particle_system.update(dt)
        assert len(mock_particle_system.particles) == 0
    
    def test_circular_emission(self, mock_particle_system):
        """Test emitting particles in a circular pattern."""
        center = (100, 100)
        speed = 100.0
        color = (255, 0, 0)
        size = 2.0
        lifetime = 1.0
        count = 8
        
        mock_particle_system.emit_circular(
            center=center,
            speed=speed,
            color=color,
            size=size,
            lifetime=lifetime,
            count=count
        )
        
        assert len(mock_particle_system.particles) == count
        
        # Check that particles are evenly distributed in a circle
        angles = []
        for particle in mock_particle_system.particles:
            velocity = pygame.Vector2(particle.velocity)
            angle = pygame.math.Vector2().angle_to(velocity)
            angles.append(angle)
        
        # Sort angles and check they're roughly evenly spaced
        angles.sort()
        angle_step = 360 / count
        for i in range(count):
            expected_angle = i * angle_step
            assert angles[i] == pytest.approx(expected_angle, abs=1.0)
    
    def test_cone_emission(self, mock_particle_system):
        """Test emitting particles in a cone pattern."""
        pos = (100, 100)
        direction = 0  # Right
        spread = 45  # degrees
        speed = 100.0
        color = (255, 0, 0)
        size = 2.0
        lifetime = 1.0
        count = 5
        
        mock_particle_system.emit_cone(
            pos=pos,
            direction=direction,
            spread=spread,
            speed=speed,
            color=color,
            size=size,
            lifetime=lifetime,
            count=count
        )
        
        assert len(mock_particle_system.particles) == count
        
        # Check that particles are within the cone
        for particle in mock_particle_system.particles:
            velocity = pygame.Vector2(particle.velocity)
            angle = abs(pygame.math.Vector2().angle_to(velocity))
            assert angle <= spread / 2
    
    def test_particle_fade(self, mock_particle_system):
        """Test particle fade effect."""
        pos = (100, 100)
        color = (255, 0, 0)
        lifetime = 1.0
        
        mock_particle_system.create_particle(
            pos=pos,
            velocity=(0, 0),
            color=color,
            size=2.0,
            lifetime=lifetime,
            fade=True
        )
        
        # Update half the lifetime
        mock_particle_system.update(0.5)
        particle = mock_particle_system.particles[0]
        
        # Color should be about half intensity
        for i in range(3):
            assert particle.color[i] == pytest.approx(color[i] * 0.5, abs=1)
    
    def test_particle_size_change(self, mock_particle_system):
        """Test particle size change over lifetime."""
        pos = (100, 100)
        initial_size = 2.0
        size_change = 2.0  # Double size over lifetime
        lifetime = 1.0
        
        mock_particle_system.create_particle(
            pos=pos,
            velocity=(0, 0),
            color=(255, 0, 0),
            size=initial_size,
            lifetime=lifetime,
            size_change=size_change
        )
        
        # Update half the lifetime
        mock_particle_system.update(0.5)
        particle = mock_particle_system.particles[0]
        
        # Size should be halfway between initial and final
        expected_size = initial_size + size_change * 0.5
        assert particle.size == pytest.approx(expected_size)
    
    def test_system_pause(self, mock_particle_system):
        """Test pausing the particle system."""
        mock_particle_system.create_particle(
            pos=(100, 100),
            velocity=(10, 10),
            color=(255, 0, 0),
            size=2.0,
            lifetime=1.0
        )
        
        # Pause system
        mock_particle_system.paused = True
        initial_pos = mock_particle_system.particles[0].pos
        
        # Update while paused
        mock_particle_system.update(0.5)
        
        # Position should not change
        assert mock_particle_system.particles[0].pos == initial_pos
    
    def test_clear_particles(self, mock_particle_system):
        """Test clearing all particles."""
        # Create several particles
        for _ in range(5):
            mock_particle_system.create_particle(
                pos=(100, 100),
                velocity=(10, 10),
                color=(255, 0, 0),
                size=2.0,
                lifetime=1.0
            )
        
        assert len(mock_particle_system.particles) == 5
        
        # Clear particles
        mock_particle_system.clear()
        assert len(mock_particle_system.particles) == 0 