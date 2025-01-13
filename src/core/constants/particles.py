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

# Thrust Particle Settings
THRUST_PARTICLE_COUNT = (2, 3)      # (min, max) particles per thrust
THRUST_PARTICLE_LIFETIME = (0.1, 0.2)  # Shorter lifetime for thrust
THRUST_PARTICLE_SPEED = (50, 150)    # (min, max) speed
THRUST_PARTICLE_SPREAD = 30          # Degrees
THRUST_PARTICLE_SIZE = (1.0, 2.0)    # (min, max) point size
THRUST_OFFSET = 20                   # Distance behind ship to emit particles

# Explosion Particle Settings
EXPLOSION_PARTICLE_COUNT = {
    'large': (12, 15),    # More particles for large explosions
    'medium': (8, 10),    # Medium amount for medium explosions
    'small': (4, 6)       # Few particles for small explosions
}
EXPLOSION_PARTICLE_LIFETIME = (0.3, 0.6)  # Longer lifetime for explosions
EXPLOSION_PARTICLE_SPEED = (100, 200)      # Faster particles for explosions
EXPLOSION_PARTICLE_SIZE = (2.0, 3.0)       # Larger particles for explosions
EXPLOSION_SPREAD = 360                     # Full circle spread for explosions 