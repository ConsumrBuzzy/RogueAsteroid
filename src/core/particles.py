"""Particle system for visual effects."""
import numpy as np
from typing import List, Tuple, Optional
import pygame

class Particle:
    """Individual particle with position, velocity, and lifetime."""
    
    def __init__(self, position: np.ndarray, velocity: np.ndarray, 
                 color: Tuple[int, int, int], lifetime: float,
                 size: float = 2.0, fade: bool = True):
        # Convert position to numpy array if it's a Vector2
        if hasattr(position, 'x'):
            self.position = np.array([float(position.x), float(position.y)])
        else:
            self.position = position.copy()
            
        # Convert velocity to numpy array if it's a Vector2
        if hasattr(velocity, 'x'):
            self.velocity = np.array([float(velocity.x), float(velocity.y)])
        else:
            self.velocity = velocity.copy()
            
        self.color = color
        self.initial_lifetime = lifetime
        self.lifetime = lifetime
        self.size = size
        self.fade = fade
        self.alpha = 255
    
    def update(self, dt: float) -> bool:
        """Update particle state. Returns False when particle should be removed."""
        self.lifetime -= dt
        if self.lifetime <= 0:
            return False
            
        self.position += self.velocity * dt
        
        if self.fade:
            self.alpha = int(255 * (self.lifetime / self.initial_lifetime))
        
        return True
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw particle on screen."""
        # Convert position to integers for drawing
        pos = self.position.astype(int)
        
        if self.alpha < 255:
            # Create surface for alpha blending
            surf = pygame.Surface((int(self.size * 2), int(self.size * 2)), pygame.SRCALPHA)
            pygame.draw.circle(
                surf,
                (*self.color, self.alpha),
                (int(self.size), int(self.size)),
                max(1, int(self.size))  # Ensure minimum radius of 1
            )
            screen.blit(surf, pos - np.array([int(self.size), int(self.size)]))
        else:
            pygame.draw.circle(
                screen,
                self.color,
                pos,
                max(1, int(self.size))  # Ensure minimum radius of 1
            )

class ParticleSystem:
    """Manages multiple particle effects."""
    
    def __init__(self):
        self.particles: List[Particle] = []
    
    def update(self, dt: float) -> None:
        """Update all particles."""
        self.particles = [p for p in self.particles if p.update(dt)]
    
    def draw(self, screen: pygame.Surface) -> None:
        """Draw all particles."""
        for particle in self.particles:
            particle.draw(screen)
    
    def create_explosion(self, position: np.ndarray, color: Tuple[int, int, int],
                        num_particles: int = 20, speed_range: Tuple[float, float] = (50, 150),
                        lifetime_range: Tuple[float, float] = (0.5, 1.0),
                        size_range: Tuple[float, float] = (1.0, 3.0)) -> None:
        """Create an explosion effect at the given position."""
        for _ in range(num_particles):
            angle = np.random.uniform(0, 2 * np.pi)
            speed = np.random.uniform(*speed_range)
            velocity = np.array([
                np.cos(angle) * speed,
                np.sin(angle) * speed
            ])
            
            lifetime = np.random.uniform(*lifetime_range)
            size = np.random.uniform(*size_range)
            
            particle = Particle(position, velocity, color, lifetime, size)
            self.particles.append(particle)
    
    def create_thrust(self, position: np.ndarray, direction: np.ndarray,
                     color: Tuple[int, int, int] = (255, 165, 0)) -> None:
        """Create a thrust effect behind the ship."""
        num_particles = 5
        spread_angle = np.pi / 6  # 30 degrees
        
        for _ in range(num_particles):
            angle_offset = np.random.uniform(-spread_angle, spread_angle)
            rot_matrix = np.array([
                [np.cos(angle_offset), -np.sin(angle_offset)],
                [np.sin(angle_offset), np.cos(angle_offset)]
            ])
            
            velocity = -rot_matrix.dot(direction) * np.random.uniform(100, 200)
            lifetime = np.random.uniform(0.1, 0.3)
            size = np.random.uniform(1.0, 2.0)
            
            particle = Particle(position, velocity, color, lifetime, size)
            self.particles.append(particle)
    
    def clear(self) -> None:
        """Remove all particles."""
        self.particles.clear() 