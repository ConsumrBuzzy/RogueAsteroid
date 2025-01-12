"""Performance tests for game systems."""
import unittest
import pytest
import time
import gc
import psutil
import os
from src.core.config.effects import EFFECT_TEMPLATES
from src.core.components.effect import EffectComponent
from src.core.services.particle_service import ParticleService

@pytest.mark.performance
class TestParticleSystemPerformance:
    """Performance tests for particle system."""
    
    def _get_memory_usage(self):
        """Get current memory usage in MB."""
        process = psutil.Process(os.getpid())
        return process.memory_info().rss / 1024 / 1024
    
    def test_particle_emission_performance(self, performance_env, test_entity):
        """Test particle emission performance."""
        effects = EffectComponent(test_entity)
        position = (400, 300)
        iterations = 100
        total_time = 0
        
        # Measure emission time for multiple iterations
        for _ in range(iterations):
            start_time = time.perf_counter()
            effects.emit('explosion', position, 0)
            end_time = time.perf_counter()
            total_time += end_time - start_time
            
            # Clean up for next iteration
            effects.clear_particles()
        
        avg_time = total_time / iterations
        assert avg_time < 0.001, f"Particle emission too slow: {avg_time:.6f}s average"
    
    def test_particle_update_performance(self, performance_env, test_entity):
        """Test particle update performance with many particles."""
        effects = EffectComponent(test_entity)
        
        # Create many particles
        for _ in range(10):  # Create 10 explosions
            effects.emit('explosion', (400, 300), 0)
        
        # Measure update time
        start_time = time.perf_counter()
        for _ in range(60):  # Simulate 1 second at 60 FPS
            effects.update(1/60)
        end_time = time.perf_counter()
        
        update_time = end_time - start_time
        assert update_time < 0.1, f"Particle update too slow: {update_time:.6f}s for 1 second simulation"
    
    def test_particle_memory_usage(self, performance_env, test_entity):
        """Test memory usage under particle load."""
        effects = EffectComponent(test_entity)
        initial_memory = self._get_memory_usage()
        
        # Create maximum particles
        for _ in range(50):  # Create many explosions
            effects.emit('explosion', (400, 300), 0)
        
        # Measure memory after creation
        peak_memory = self._get_memory_usage()
        memory_increase = peak_memory - initial_memory
        
        # Clear particles
        effects.clear_particles()
        gc.collect()
        
        # Measure memory after cleanup
        final_memory = self._get_memory_usage()
        memory_leak = final_memory - initial_memory
        
        # Check memory usage
        assert memory_increase < 10.0, f"Excessive memory usage: {memory_increase:.2f}MB"
        assert memory_leak < 1.0, f"Possible memory leak: {memory_leak:.2f}MB residual"
    
    def test_particle_service_limits(self, performance_env):
        """Test particle service enforces limits correctly."""
        service = ParticleService(performance_env.screen)
        position = (400, 300)
        
        # Try to exceed global particle limit
        for _ in range(1000):  # Try to create way too many particles
            service.emit('explosion', position, 0)
            
        particles_after = len(service._particles)
        assert particles_after <= service.MAX_PARTICLES, "Particle service exceeded global limit"
        
        # Try to exceed per-effect limit
        service.clear()
        for _ in range(1000):  # Try to create too many of one effect
            service.emit('thrust', position, 0)
            
        effect_count = service._active_effects.get('thrust', 0)
        assert effect_count <= service.MAX_PARTICLES_PER_EFFECT, "Particle service exceeded per-effect limit"
    
    @pytest.mark.skip(reason="Long-running stress test")
    def test_particle_system_stress(self, performance_env, test_entity):
        """Stress test the particle system."""
        effects = EffectComponent(test_entity)
        position = (400, 300)
        frames = 3600  # 1 minute at 60 FPS
        
        start_time = time.perf_counter()
        start_memory = self._get_memory_usage()
        
        # Simulate heavy particle usage
        for frame in range(frames):
            # Create new particles every few frames
            if frame % 10 == 0:
                for effect_type in EFFECT_TEMPLATES:
                    effects.emit(effect_type, position, frame % 360)
            
            # Update and draw
            effects.update(1/60)
            effects.draw(performance_env.screen)
            
        end_time = time.perf_counter()
        end_memory = self._get_memory_usage()
        
        total_time = end_time - start_time
        memory_increase = end_memory - start_memory
        
        print(f"\nStress Test Results:")
        print(f"Total time: {total_time:.2f}s")
        print(f"Average FPS: {frames/total_time:.1f}")
        print(f"Memory increase: {memory_increase:.2f}MB")
        
        assert memory_increase < 50.0, f"Excessive memory growth during stress test: {memory_increase:.2f}MB" 