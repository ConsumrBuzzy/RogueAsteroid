"""Performance tests for RogueAsteroid."""
import time
import pytest
import numpy as np
from typing import List, Callable
from dataclasses import dataclass
from test_utils import MockGame, create_test_entity
from src.core.entities.base import Entity
from src.entities.asteroid import Asteroid
from src.entities.bullet import Bullet
from src.entities.ship import Ship

@dataclass
class BenchmarkResult:
    """Results from a benchmark run."""
    name: str
    iterations: int
    total_time: float
    avg_time: float
    min_time: float
    max_time: float

def benchmark(func: Callable, iterations: int = 1000) -> BenchmarkResult:
    """Run a benchmark test.
    
    Args:
        func: Function to benchmark
        iterations: Number of iterations to run
        
    Returns:
        Benchmark results
    """
    times = []
    total_start = time.perf_counter()
    
    for _ in range(iterations):
        start = time.perf_counter()
        func()
        end = time.perf_counter()
        times.append(end - start)
    
    total_time = time.perf_counter() - total_start
    
    return BenchmarkResult(
        name=func.__name__,
        iterations=iterations,
        total_time=total_time,
        avg_time=np.mean(times),
        min_time=min(times),
        max_time=max(times)
    )

class TestGamePerformance:
    """Performance tests for game systems."""
    
    @pytest.fixture(autouse=True)
    def setup_game(self):
        """Setup test game instance."""
        self.game = MockGame()
        
    def create_entities(self, count: int, entity_type: type) -> List[Entity]:
        """Create multiple entities of specified type."""
        entities = []
        for _ in range(count):
            x = np.random.randint(0, self.game.width)
            y = np.random.randint(0, self.game.height)
            entity = entity_type(self.game, x, y)
            entities.append(entity)
            self.game.add_entity(entity)
        return entities
    
    @pytest.mark.performance
    def test_collision_detection_performance(self):
        """Test performance of collision detection system."""
        # Create test entities
        asteroids = self.create_entities(50, Asteroid)
        bullets = self.create_entities(10, Bullet)
        
        def check_collisions():
            for bullet in bullets:
                for asteroid in asteroids:
                    if bullet.get_component('collision').check_collision(
                        asteroid.get_component('collision')):
                        pass
        
        result = benchmark(check_collisions)
        print(f"\nCollision Detection Benchmark ({result.iterations} iterations):")
        print(f"Total time: {result.total_time:.4f}s")
        print(f"Average time: {result.avg_time*1000:.4f}ms")
        print(f"Min time: {result.min_time*1000:.4f}ms")
        print(f"Max time: {result.max_time*1000:.4f}ms")
        
        # Performance assertions
        assert result.avg_time < 0.001  # Average time should be under 1ms
    
    @pytest.mark.performance
    def test_entity_update_performance(self):
        """Test performance of entity update system."""
        # Create mix of entities
        self.create_entities(30, Asteroid)
        self.create_entities(5, Bullet)
        ship = Ship(self.game, self.game.width/2, self.game.height/2)
        self.game.add_entity(ship)
        
        def update_entities():
            for entity in self.game.entities:
                entity.update(self.game.dt)
        
        result = benchmark(update_entities)
        print(f"\nEntity Update Benchmark ({result.iterations} iterations):")
        print(f"Total time: {result.total_time:.4f}s")
        print(f"Average time: {result.avg_time*1000:.4f}ms")
        print(f"Min time: {result.min_time*1000:.4f}ms")
        print(f"Max time: {result.max_time*1000:.4f}ms")
        
        # Performance assertions
        assert result.avg_time < 0.002  # Average time should be under 2ms
    
    @pytest.mark.performance
    def test_particle_system_performance(self):
        """Test performance of particle system."""
        from src.core.entities.components import ParticleComponent
        
        # Create entities with particle effects
        entities = []
        for _ in range(20):
            entity = create_test_entity(self.game)
            particle = entity.add_component(ParticleComponent)
            # Add some test particles
            for _ in range(50):
                particle.emit(
                    position=np.array([np.random.random()*self.game.width,
                                     np.random.random()*self.game.height]),
                    velocity=np.array([np.random.random()*100-50,
                                     np.random.random()*100-50]),
                    lifetime=1.0
                )
            entities.append(entity)
            self.game.add_entity(entity)
        
        def update_particles():
            for entity in entities:
                entity.get_component(ParticleComponent).update(self.game.dt)
        
        result = benchmark(update_particles)
        print(f"\nParticle System Benchmark ({result.iterations} iterations):")
        print(f"Total time: {result.total_time:.4f}s")
        print(f"Average time: {result.avg_time*1000:.4f}ms")
        print(f"Min time: {result.min_time*1000:.4f}ms")
        print(f"Max time: {result.max_time*1000:.4f}ms")
        
        # Performance assertions
        assert result.avg_time < 0.005  # Average time should be under 5ms 