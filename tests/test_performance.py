"""Performance tests for game systems."""
import unittest
import time
import pygame
import gc
import psutil
import os
from src.core.config.effects import EFFECT_TEMPLATES
from src.core.components.effect import EffectComponent
from src.core.services.particle_service import ParticleService
from src.core.entity import Entity

class MockGame:
    """Mock game class for testing."""
    def __init__(self):
        pygame.init()
        self.screen = pygame.Surface((800, 600))
        self.width = 800
        self.height = 600

class TestParticleSystemPerformance(unittest.TestCase):
    """Performance tests for particle system."""
    
    def setUp(self):
        """Set up test environment."""
        self.game = MockGame()
        self.entity = Entity(self.game)
        self.effects = EffectComponent(self.entity)
        self.particle_service = ParticleService(self.game.screen)
        
        # Force garbage collection before each test
        gc.collect()
        
    def tearDown(self):
        """Clean up after tests."""
        self.effects.clear_particles()
        self.particle_service.clear()
        gc.collect()
    
    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def test_particle_emission_performance(self):
        """Test particle emission performance."""
        position = (400, 300)
        iterations = 100
        total_time = 0
        
        # Measure emission time for multiple iterations
        for _ in range(iterations):
            start_time = time.perf_counter()
            self.effects.emit('explosion', position, 0)
            end_time = time.perf_counter()
            total_time += end_time - start_time
            
            # Clean up for next iteration
            self.effects.clear_particles()
        
        avg_time = total_time / iterations
        self.assertLess(avg_time, 0.001, 
                       f"Particle emission too slow: {avg_time:.6f}s average")
    
    def test_particle_update_performance(self):
        """Test particle update performance with many particles."""
        # Create many particles
        for _ in range(10):  # Create 10 explosions
            self.effects.emit('explosion', (400, 300), 0)
        
        # Measure update time
        start_time = time.perf_counter()
        for _ in range(60):  # Simulate 1 second at 60 FPS
            self.effects.update(1/60)
        end_time = time.perf_counter()
        
        update_time = end_time - start_time
        self.assertLess(update_time, 0.1, 
                       f"Particle update too slow: {update_time:.6f}s for 1 second simulation")
    
    def test_particle_memory_usage(self):
        """Test memory usage under particle load."""
        initial_memory = self._get_memory_usage()
        
        # Create maximum particles
        for _ in range(50):  # Create many explosions
            self.effects.emit('explosion', (400, 300), 0)
        
        # Measure memory after creation
        peak_memory = self._get_memory_usage()
        memory_increase = peak_memory - initial_memory
        
        # Clear particles
        self.effects.clear_particles()
        gc.collect()
        
        # Measure memory after cleanup
        final_memory = self._get_memory_usage()
        memory_leak = final_memory - initial_memory
        
        # Check memory usage
        self.assertLess(memory_increase, 10.0,  # Allow up to 10MB increase
                       f"Excessive memory usage: {memory_increase:.2f}MB")
        self.assertLess(memory_leak, 1.0,  # Allow up to 1MB residual
                       f"Possible memory leak: {memory_leak:.2f}MB residual")
    
    def test_particle_service_limits(self):
        """Test particle service enforces limits correctly."""
        position = (400, 300)
        
        # Try to exceed global particle limit
        particles_before = len(self.particle_service._particles)
        for _ in range(1000):  # Try to create way too many particles
            self.particle_service.emit('explosion', position, 0)
            
        particles_after = len(self.particle_service._particles)
        self.assertLessEqual(particles_after, self.particle_service.MAX_PARTICLES,
                           "Particle service exceeded global limit")
        
        # Try to exceed per-effect limit
        self.particle_service.clear()
        for _ in range(1000):  # Try to create too many of one effect
            self.particle_service.emit('thrust', position, 0)
            
        effect_count = self.particle_service._active_effects.get('thrust', 0)
        self.assertLessEqual(effect_count, self.particle_service.MAX_PARTICLES_PER_EFFECT,
                           "Particle service exceeded per-effect limit")
    
    @unittest.skip("Long-running stress test")
    def test_particle_system_stress(self):
        """Stress test the particle system."""
        position = (400, 300)
        frames = 3600  # 1 minute at 60 FPS
        
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()
        
        # Simulate heavy particle usage
        for frame in range(frames):
            # Create new particles every few frames
            if frame % 10 == 0:
                for effect_type in EFFECT_TEMPLATES:
                    self.effects.emit(effect_type, position, frame % 360)
            
            # Update and draw
            self.effects.update(1/60)
            self.effects.draw(self.game.screen)
            
        end_time = time.perf_counter()
        end_memory = self._get_memory_usage()
        
        total_time = end_time - start_time
        memory_increase = end_memory - start_memory
        
        print(f"\nStress Test Results:")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average FPS: {frames/total_time:.1f}")
        print(f"Memory increase: {memory_increase:.2f}MB")
        
        self.assertLess(memory_increase, 50.0,  # Allow up to 50MB increase for stress test
                       f"Excessive memory growth during stress test: {memory_increase:.2f}MB")

if __name__ == '__main__':
    unittest.main() 