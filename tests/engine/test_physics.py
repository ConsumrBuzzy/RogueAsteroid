"""Test suite for physics system."""
import pytest
import pygame
import math
from src.core.game import Game
from src.core.entities.base import Entity
from src.core.entities.components import PhysicsComponent, TransformComponent
from src.core.constants import *

@pytest.fixture
def game(mock_game, screen):
    """Create a game instance for testing."""
    game = Game()
    game.screen = screen
    yield game

@pytest.fixture
def physics_entity(game):
    """Create an entity with physics and transform components."""
    entity = Entity(game)
    transform = entity.add_component(TransformComponent)
    physics = entity.add_component(PhysicsComponent, mass=1.0, max_speed=100.0)
    return entity, transform, physics

@pytest.mark.engine
class TestPhysicsSystem:
    """Test cases for the physics system."""
    
    def test_force_application(self, game, physics_entity):
        """Test basic force application."""
        entity, transform, physics = physics_entity
        
        # Apply force and update
        force = pygame.Vector2(10.0, 0.0)
        physics.apply_force(force)
        dt = 1/60
        physics.update(dt)
        
        # Verify acceleration (F = ma)
        expected_acceleration = force / physics.mass
        expected_velocity = expected_acceleration * dt
        assert transform.velocity.x == pytest.approx(expected_velocity.x, rel=1e-5)
        assert transform.velocity.y == pytest.approx(expected_velocity.y, rel=1e-5)
    
    def test_multiple_forces(self, game, physics_entity):
        """Test application of multiple forces."""
        entity, transform, physics = physics_entity
        
        # Apply multiple forces
        forces = [
            pygame.Vector2(10.0, 0.0),
            pygame.Vector2(0.0, 20.0),
            pygame.Vector2(-5.0, -10.0)
        ]
        
        for force in forces:
            physics.apply_force(force)
        
        # Update physics
        dt = 1/60
        physics.update(dt)
        
        # Verify net force effect
        net_force = sum((f for f in forces), pygame.Vector2(0, 0))
        expected_acceleration = net_force / physics.mass
        expected_velocity = expected_acceleration * dt
        assert transform.velocity.x == pytest.approx(expected_velocity.x, rel=1e-5)
        assert transform.velocity.y == pytest.approx(expected_velocity.y, rel=1e-5)
    
    def test_max_speed_limit(self, game, physics_entity):
        """Test maximum speed enforcement."""
        entity, transform, physics = physics_entity
        
        # Apply large force
        large_force = pygame.Vector2(1000.0, 1000.0)
        physics.apply_force(large_force)
        physics.update(1.0)  # Long update to build speed
        
        # Verify speed is capped
        current_speed = transform.velocity.length()
        assert current_speed <= physics.max_speed
        
        # Verify direction is preserved
        expected_direction = large_force.normalize()
        actual_direction = transform.velocity.normalize()
        assert actual_direction.x == pytest.approx(expected_direction.x, rel=1e-5)
        assert actual_direction.y == pytest.approx(expected_direction.y, rel=1e-5)
    
    def test_friction(self, game, physics_entity):
        """Test friction application."""
        entity, transform, physics = physics_entity
        
        # Set initial velocity
        initial_velocity = pygame.Vector2(50.0, 0.0)
        transform.velocity = initial_velocity
        physics.friction = 0.1  # 10% friction per update
        
        # Update and verify friction effect
        dt = 1/60
        physics.update(dt)
        
        expected_velocity = initial_velocity * (1 - physics.friction)
        assert transform.velocity.x == pytest.approx(expected_velocity.x, rel=1e-5)
        assert transform.velocity.y == pytest.approx(expected_velocity.y, rel=1e-5)
    
    def test_angular_motion(self, game, physics_entity):
        """Test angular physics."""
        entity, transform, physics = physics_entity
        
        # Set initial angular velocity
        physics.angular_velocity = 45.0  # 45 degrees per second
        initial_rotation = transform.rotation
        
        # Update and verify rotation
        dt = 1/60
        physics.update(dt)
        
        expected_rotation = initial_rotation + physics.angular_velocity * dt
        assert transform.rotation == pytest.approx(expected_rotation, rel=1e-5)
    
    def test_impulse_forces(self, game, physics_entity):
        """Test impulse force application."""
        entity, transform, physics = physics_entity
        
        # Apply impulse
        impulse = pygame.Vector2(20.0, 0.0)
        physics.apply_impulse(impulse)
        
        # Verify immediate velocity change (p = mv)
        expected_velocity = impulse / physics.mass
        assert transform.velocity.x == pytest.approx(expected_velocity.x, rel=1e-5)
        assert transform.velocity.y == pytest.approx(expected_velocity.y, rel=1e-5)
    
    def test_gravity(self, game, physics_entity):
        """Test gravity effect."""
        entity, transform, physics = physics_entity
        
        # Enable gravity
        physics.gravity = pygame.Vector2(0, 9.81)  # Standard gravity
        initial_position = pygame.Vector2(transform.position)
        
        # Update for one second
        dt = 1/60
        for _ in range(60):
            physics.update(dt)
        
        # Verify gravitational effect
        expected_velocity = physics.gravity * 1.0  # After 1 second
        assert transform.velocity.y == pytest.approx(expected_velocity.y, rel=1e-5)
        
        # Verify position change (s = ut + 1/2at²)
        expected_displacement = physics.gravity * (1.0 ** 2) * 0.5
        expected_position = initial_position + expected_displacement
        assert transform.position.y == pytest.approx(expected_position.y, rel=1e-5)
    
    def test_relative_motion(self, game):
        """Test relative motion between entities."""
        # Create two entities
        entity1, transform1, physics1 = physics_entity(game)
        entity2, transform2, physics2 = physics_entity(game)
        
        # Set up opposing velocities
        physics1.velocity = pygame.Vector2(5.0, 0.0)
        physics2.velocity = pygame.Vector2(-5.0, 0.0)
        
        # Record initial positions
        pos1_initial = pygame.Vector2(transform1.position)
        pos2_initial = pygame.Vector2(transform2.position)
        
        # Update for one second
        dt = 1/60
        for _ in range(60):
            physics1.update(dt)
            physics2.update(dt)
        
        # Verify relative motion
        displacement1 = transform1.position - pos1_initial
        displacement2 = transform2.position - pos2_initial
        relative_speed = (displacement1 - displacement2).length()
        expected_relative_speed = 10.0  # Combined speed
        
        assert relative_speed == pytest.approx(expected_relative_speed, rel=1e-5) 