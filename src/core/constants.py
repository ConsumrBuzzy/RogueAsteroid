"""Game constants."""

# Display
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# Particle Effects
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

# Game Settings
STARTING_LIVES = 3
SCORE_MULTIPLIER = 100
HIGH_SCORE_COUNT = 10

# Ship Settings
SHIP_ACCELERATION = 300.0
SHIP_MAX_SPEED = 300.0
SHIP_ROTATION_SPEED = 150.0  # Degrees per second
SHIP_FRICTION = 0.02
SHIP_INVULNERABLE_TIME = 3.0

# Weapon Settings
BULLET_SPEED = 500.0
BULLET_LIFETIME = 1.0
MAX_BULLETS = 4

# Asteroid Settings
MAX_ASTEROIDS = 12
ASTEROID_SIZES = {
    'large': {
        'radius': 40,
        'speed_range': (50, 100),
        'mass': 9.0,
        'points': 3,
        'vertices_range': (10, 14)  # More vertices for larger asteroids
    },
    'medium': {
        'radius': 20,
        'speed_range': (100, 150),
        'mass': 4.0,
        'points': 2,
        'vertices_range': (8, 12)  # Medium complexity
    },
    'small': {
        'radius': 10,
        'speed_range': (150, 200),
        'mass': 1.0,
        'points': 1,
        'vertices_range': (6, 10)  # Simpler shape for small asteroids
    }
}

# Particle Settings
PARTICLE_MIN_LIFETIME = 0.2
PARTICLE_MAX_LIFETIME = 0.4
THRUST_PARTICLE_COUNT = (2, 3)  # (min, max) particles per thrust
THRUST_PARTICLE_SPEED = (50, 150)  # (min, max) speed
THRUST_PARTICLE_SPREAD = 30  # Degrees
THRUST_PARTICLE_SIZE = (1.0, 2.0)  # (min, max) point size 