"""Particle effect constants."""

# Effect Colors
EXPLOSION_COLORS = [
    (255, 69, 0),    # Red-orange
    (255, 140, 0),   # Dark orange
    (255, 165, 0),   # Orange
    (255, 215, 0),   # Yellow
]

THRUST_COLORS = [
    (200, 200, 200),  # Light gray
    (180, 180, 180),  # Medium gray
    (160, 160, 160),  # Dark gray
]

# Particle Settings
PARTICLE_MIN_LIFETIME = 0.2
PARTICLE_MAX_LIFETIME = 0.4
THRUST_PARTICLE_COUNT = (2, 3)  # (min, max) particles per thrust
THRUST_PARTICLE_SPEED = (50, 150)  # (min, max) speed
THRUST_PARTICLE_SPREAD = 30  # Degrees
THRUST_PARTICLE_SIZE = (1.0, 2.0)  # (min, max) point size 