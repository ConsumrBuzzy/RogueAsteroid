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
import pygame
import random

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
    """Test cases for game performance."""

    def test_collision_detection_performance(self):
        """Test the performance of collision detection."""
        game = MockGame()
        # Create test entities
        entities = []
        for _ in range(20):  # Create 20 entities with collision components
            entity = Entity(game)
            transform = entity.add_component(TransformComponent)
            transform.position = pygame.Vector2(random.randint(0, 800), random.randint(0, 600))
            entity.add_component(CollisionComponent, radius=20)
            entities.append(entity)
            game.add_entity(entity)

        def check_collisions():
            for i, entity1 in enumerate(entities):
                collision1 = entity1.get_component('collision')
                if collision1:
                    for entity2 in entities[i+1:]:
                        collision2 = entity2.get_component('collision')
                        if collision2:
                            collision1.check_collision(collision2)

        # Run benchmark
        result = benchmark(check_collisions, num_iterations=100)
        print(f"Collision detection average time: {result.average_time_ms:.2f}ms")
        assert result.average_time_ms < 5.0, f"Collision detection too slow: {result.average_time_ms:.2f}ms"

    def test_entity_update_performance(self):
        """Test the performance of entity updates."""
        game = MockGame()
        entities = []
        for _ in range(100):  # Create 100 entities
            entity = Entity(game)
            transform = entity.add_component(TransformComponent)
            transform.position = pygame.Vector2(random.randint(0, 800), random.randint(0, 600))
            transform.velocity = pygame.Vector2(random.uniform(-100, 100), random.uniform(-100, 100))
            entities.append(entity)
            game.add_entity(entity)

        def update_entities():
            for entity in entities:
                entity.update(1/60)  # Update at 60 FPS

        # Run benchmark
        result = benchmark(update_entities, num_iterations=100)
        print(f"Entity update average time: {result.average_time_ms:.2f}ms")
        assert result.average_time_ms < 10.0, f"Entity updates too slow: {result.average_time_ms:.2f}ms"

    def test_particle_system_performance(self):
        """Test the performance of the particle system."""
        game = MockGame()
        particles = []
        for _ in range(1000):  # Create 1000 particles
            particle = Entity(game)
            transform = particle.add_component(TransformComponent)
            transform.position = pygame.Vector2(random.randint(0, 800), random.randint(0, 600))
            transform.velocity = pygame.Vector2(random.uniform(-100, 100), random.uniform(-100, 100))
            particles.append(particle)
            game.add_entity(particle)

        def update_particles():
            for particle in particles:
                particle.update(1/60)  # Update at 60 FPS

        # Run benchmark
        result = benchmark(update_particles, num_iterations=100)
        print(f"Particle system average time: {result.average_time_ms:.2f}ms")
        assert result.average_time_ms < 50.0, f"Particle system too slow: {result.average_time_ms:.2f}ms" 